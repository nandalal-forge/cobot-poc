from fastapi import APIRouter
from influxdb_client import InfluxDBClient
import os

router = APIRouter()

INFLUX_URL = 'http://localhost:8086'
INFLUX_TOKEN = 'mytoken123'
INFLUX_ORG = 'cobot'
INFLUX_BUCKET = 'telemetry'

def get_client():
    return InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

@router.get('/latest')
def get_latest():
    try:
        client = get_client()
        query = '''
        from(bucket: "telemetry")
          |> range(start: -1m)
          |> filter(fn: (r) => r._measurement == "position")
          |> last()
          |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
        '''
        tables = client.query_api().query(query, org=INFLUX_ORG)
        for table in tables:
            for record in table.records:
                return {
                    'x': record.values.get('x', 0),
                    'y': record.values.get('y', 0),
                    'timestamp': str(record.get_time())
                }
        return {'x': 0, 'y': 0, 'timestamp': 'no data'}
    except Exception as e:
        return {'error': str(e)}

@router.get('/imu')
def get_imu():
    try:
        client = get_client()
        query = '''
        from(bucket: "telemetry")
          |> range(start: -10s)
          |> filter(fn: (r) => r._measurement == "imu")
          |> last()
          |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
        '''
        tables = client.query_api().query(query, org=INFLUX_ORG)
        for table in tables:
            for record in table.records:
                return record.values
        return {'error': 'no imu data'}
    except Exception as e:
        return {'error': str(e)}