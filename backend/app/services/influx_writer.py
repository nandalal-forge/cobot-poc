from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUX_URL = 'http://localhost:8086'
INFLUX_TOKEN = 'mytoken123'
INFLUX_ORG = 'cobot'
INFLUX_BUCKET = 'telemetry'

_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
_write_api = _client.write_api(write_options=SYNCHRONOUS)

def write_position(cobot_id: str, x: float, y: float):
    point = (Point('position')
             .tag('cobot_id', cobot_id)
             .field('x', x)
             .field('y', y))
    _write_api.write(bucket=INFLUX_BUCKET, record=point)

def write_imu(cobot_id: str, ax: float, ay: float, az: float,
              gx: float, gy: float, gz: float):
    point = (Point('imu')
             .tag('cobot_id', cobot_id)
             .field('ax', ax).field('ay', ay).field('az', az)
             .field('gx', gx).field('gy', gy).field('gz', gz))
    _write_api.write(bucket=INFLUX_BUCKET, record=point)