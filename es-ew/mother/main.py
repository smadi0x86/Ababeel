import time
import serial
import logging
import argparse
from datetime import datetime
from pymavlink import mavutil
import pandas as pd
import numpy as np

from tdl_message import TDLTrackMessage
from config import TETHER_PORT, PIXHAWK_PORT, LOG_FILE
from rf_trigger import monitor_rf_trigger
from particle_filter import ParticleFilter
from dpc import DensityPeakCluster
from c2_export import export_c2_xml

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger("Orchestrator")

SIMULATED_BEARING_NOISE_STD_DEG = 5.0
FALLBACK_LAT = 34.0
FALLBACK_LON = -118.0


class EsEwOrchestrator:
    def __init__(self, simulate=False):
        self.simulate = simulate
        self.track_counter = 0
        self.pf = ParticleFilter(num_particles=10000)
        self.dpc = DensityPeakCluster()
        self._using_fallback_position = False

        try:
            self.ser = serial.Serial(TETHER_PORT, 115200, timeout=1)
            logger.info("Connected to ESP32 on %s", TETHER_PORT)
        except serial.SerialException as e:
            logger.error("Failed to open tether port %s: %s", TETHER_PORT, e)
            if not self.simulate:
                raise
            self.ser = None

        try:
            self.mav = mavutil.mavlink_connection(PIXHAWK_PORT, baud=115200)
            logger.info("Waiting for Pixhawk heartbeat...")
            self.mav.wait_heartbeat(timeout=10)
            # ATTITUDE (msg 30) at 10 Hz, GLOBAL_POSITION_INT (msg 33) at 10 Hz
            # https://mavlink.io/en/messages/common.html#MAV_CMD_SET_MESSAGE_INTERVAL
            self.mav.mav.command_long_send(
                self.mav.target_system, self.mav.target_component,
                mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
                30, 100000, 0, 0, 0, 0, 0)
            self.mav.mav.command_long_send(
                self.mav.target_system, self.mav.target_component,
                mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
                33, 100000, 0, 0, 0, 0, 0)
            logger.info("Pixhawk connected. Requesting ATTITUDE + GPS at 10 Hz.")
        except Exception as e:
            logger.error("Pixhawk connection failed: %s", e)
            if not self.simulate:
                raise
            self.mav = None

    def _get_telemetry(self):
        """Read latest ATTITUDE and GPS from the Pixhawk, or return simulation defaults."""
        yaw_deg = 0.0
        uav_lat = FALLBACK_LAT
        uav_lon = FALLBACK_LON
        telemetry_live = False

        if self.mav:
            att_msg = self.mav.recv_match(type='ATTITUDE', blocking=False)
            gps_msg = self.mav.recv_match(type='GLOBAL_POSITION_INT', blocking=False)
            if att_msg:
                yaw_deg = np.degrees(att_msg.yaw)
                telemetry_live = True
            if gps_msg:
                uav_lat = gps_msg.lat / 1e7
                uav_lon = gps_msg.lon / 1e7
                telemetry_live = True

        if uav_lat == 0.0 or uav_lon == 0.0:
            uav_lat = FALLBACK_LAT
            uav_lon = FALLBACK_LON

        if not telemetry_live and not self._using_fallback_position:
            self._using_fallback_position = True
            logger.warning(
                "No live telemetry. Using fallback position: %.4f, %.4f",
                uav_lat, uav_lon)

        return uav_lat, uav_lon, yaw_deg, telemetry_live

    def _estimate_bearing(self, yaw_deg, telemetry_live):
        """
        With a single omnidirectional antenna, true AoA is not possible.
        When telemetry is live, the UAV heading is the best available proxy.
        In simulation, gaussian noise is added so the particle filter
        has variance to converge on rather than a degenerate constant input.
        """
        if telemetry_live:
            return yaw_deg

        return yaw_deg + np.random.normal(0, SIMULATED_BEARING_NOISE_STD_DEG)

    def on_rf_spike(self, pdw_df):
        freq, rssi = self.dpc.cluster(pdw_df)
        logger.info("DPC Cluster Lock: %.2f MHz @ %.1f dBm", freq / 1e6, rssi)

        uav_lat, uav_lon, yaw_deg, telemetry_live = self._get_telemetry()
        measurement_bearing = self._estimate_bearing(yaw_deg, telemetry_live)

        logger.info(
            "UAV Baseline -> Lat: %.5f, Lon: %.5f, Hdg: %.1f, Bearing: %.1f%s",
            uav_lat, uav_lon, yaw_deg, measurement_bearing,
            "" if telemetry_live else " [SIM]")

        particles = self.pf.update(uav_lat, uav_lon, yaw_deg, measurement_bearing)
        target_lat = np.average(particles[:, 0], weights=self.pf.weights)
        target_lon = np.average(particles[:, 1], weights=self.pf.weights)

        self.track_counter += 1
        threat = 2 if rssi > -50 else 1

        if self.ser:
            try:
                tdl_msg = TDLTrackMessage(
                    self.track_counter, freq / 1e6, rssi, measurement_bearing, threat)
                self.ser.write(tdl_msg.pack())
                logger.info("Kinetic Handoff sent to ESP32 (32-byte payload).")
            except Exception as e:
                logger.error("Failed to send to ESP32: %s", e)

        export_c2_xml(
            self.track_counter, target_lat, target_lon, freq / 1e6, rssi,
            filepath=LOG_FILE.replace(".txt", ".xml"),
            source_lat=uav_lat, source_lon=uav_lon)

        log_line = (
            f"[{datetime.now().strftime('%H:%M:%S')}] "
            f"TDL Track {self.track_counter} | "
            f"C2: {target_lat:.4f},{target_lon:.4f} | "
            f"Bearing: {measurement_bearing:.1f}")
        logger.info(log_line)
        try:
            with open(LOG_FILE, "a") as f:
                f.write(log_line + "\n")
        except IOError as e:
            logger.error("Failed to write to log file: %s", e)

    def run(self):
        monitor_rf_trigger(
            self.on_rf_spike, freq=433.92e6, threshold=0.5, simulate=self.simulate)


def parse_args():
    parser = argparse.ArgumentParser(description="ES-EW Orchestrator")
    parser.add_argument(
        "--simulate", action="store_true",
        help="Run without physical hardware (simulated triggers/telemetry)")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    orchestrator = EsEwOrchestrator(simulate=args.simulate)
    orchestrator.run()
