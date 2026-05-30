import os

TETHER_PORT = os.environ.get('TETHER_PORT', '/dev/ttyAMA0')
PIXHAWK_PORT = os.environ.get('PIXHAWK_PORT', '/dev/ttyACM0')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.environ.get('LOG_FILE', os.path.join(BASE_DIR, 'logs', 'es-log.txt'))
