import os
from datetime import datetime
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger("C2_Export")


def _build_track_element(track_id, lat, lon, freq_mhz, rssi, source_lat, source_lon):
    track = ET.Element("track")

    ET.SubElement(track, "source").text = "AB123"
    ET.SubElement(track, "sendTime").text = datetime.utcnow().strftime("%H:%M:%S")
    ET.SubElement(track, "mustAck").text = "false"
    ET.SubElement(track, "messageID").text = str(track_id)

    ET.SubElement(track, "sourceLat").text = f"{source_lat:.4f}"
    ET.SubElement(track, "sourceLon").text = f"{source_lon:.4f}"
    ET.SubElement(track, "sourceElev").text = "400"

    ET.SubElement(track, "trackNum").text = f"TR{track_id:03d}"
    ET.SubElement(track, "time").text = datetime.utcnow().strftime("%H:%M:%S")

    ET.SubElement(track, "lat").text = f"{lat:.4f}"
    ET.SubElement(track, "lon").text = f"{lon:.4f}"
    ET.SubElement(track, "elev").text = "0"
    ET.SubElement(track, "pointType").text = "W"
    ET.SubElement(track, "quality").text = "A"
    ET.SubElement(track, "course").text = "0"
    ET.SubElement(track, "speed").text = "0"

    return track


def export_c2_xml(track_id, lat, lon, freq_mhz, rssi,
                  filepath="../logs/c2_handoff.xml",
                  source_lat=34.0, source_lon=-118.0):
    """
    Append a J3.2 Air Track element to the FakeTDL XML log.
    Creates the file with a root <fakeTDL> element on first call,
    then appends subsequent <track> elements under that root.

    Schema reference: OpenDFDL FakeTDL (fakeTDL.dfdl.xsd)
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    root = None
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
        except ET.ParseError:
            logger.warning("Corrupt XML log detected, starting fresh: %s", filepath)
            root = None

    if root is None:
        root = ET.Element("fakeTDL")

    track = _build_track_element(track_id, lat, lon, freq_mhz, rssi, source_lat, source_lon)
    root.append(track)

    tree = ET.ElementTree(root)
    tree.write(filepath, encoding="utf-8", xml_declaration=True)
