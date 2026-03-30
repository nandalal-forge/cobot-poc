from fastapi import APIRouter
from ..models.schemas import SessionIn
import paho.mqtt.client as mqtt
import json
import os
import sys

sys.path.insert(0, '/home/forge/cobot-poc')
router = APIRouter()
from . import zones as zones_router

SLAM_MAP = '/home/forge/cobot-poc/simulation/ros2_ws/src/cobot_sim/maps/lab_map.yaml'

@router.post('/start')
def start_session(session: SessionIn):
    # Use SLAM map if available and requested
    if session.use_slam_map and os.path.exists(SLAM_MAP):
        from intelligence.path_planner.boustrophedon import generate_coverage_path_from_map
        waypoints = generate_coverage_path_from_map(SLAM_MAP, robot_width=0.4)
        source = 'slam_map'
    else:
        from intelligence.path_planner.boustrophedon import generate_coverage_path
        room = [
            [0, 0],
            [session.room_width_m, 0],
            [session.room_width_m, session.room_height_m],
            [0, session.room_height_m]
        ]
        excl = [z['metre_coords'] for z in zones_router.zones_store
                if z['zone_type'] in ('exclude', 'manual_only')]
        waypoints = generate_coverage_path(room, excl if excl else None)
        source = 'manual'

    # Publish to robot via MQTT
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect('localhost', 1883)
    client.publish('cobot/waypoints', json.dumps(waypoints))
    client.disconnect()

    return {
        'status': 'started',
        'source': source,
        'waypoints': len(waypoints),
        'preview': waypoints[:5]
    }

@router.post('/stop')
def stop_session():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect('localhost', 1883)
    client.publish('cobot/command', json.dumps({'cmd': 'stop'}))
    client.disconnect()
    return {'status': 'stopped'}

@router.get('/status')
def session_status():
    return {'running': True}