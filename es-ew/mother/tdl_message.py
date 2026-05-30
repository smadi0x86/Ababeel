import time
import struct

class TDLTrackMessage:
    FORMAT = '<B H I h h B B I 15x'
    SIZE = 32

    def __init__(self, track_id, freq_mhz, rssi, bearing_deg, threat, protocol_id=0):
        self.msg_type = 0x01
        self.track_id = track_id
        self.freq_khz = int(freq_mhz * 1000)
        self.rssi_scaled = int(rssi * 10)
        self.bearing_scaled = int(bearing_deg * 10)
        self.threat = threat
        self.protocol_id = protocol_id
        self.timestamp = int(time.time())

    def pack(self):
        return struct.pack(
            self.FORMAT,
            self.msg_type,
            self.track_id,
            self.freq_khz,
            self.rssi_scaled,
            self.bearing_scaled,
            self.threat,
            self.protocol_id,
            self.timestamp
        )
