#!/usr/bin/env python3

from fastapi import APIRouter
from ..models.schemas import SessionIn
import paho.mqtt.client as mqtt
import json, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

router = APIRouter()
from . import zones as zones_router

@router.post('/start')
def start_session(session: SessionIn):
    # Use SLAM map if available, otherwise fall back to manual room coords
    slam_map = '/tmp/lab_map.yaml'

    if os.path.exists(slam_map) and not zones_router.zones_store:
        # Auto-generate from SLAM map
        from intelligence.path_planner.boustrophedon import generate_coverage_path_from_map
        waypoints = generate_coverage_path_from_map(slam_map, robot_width=0.4)
        source = 'slam_map'
    else:
        # Use manual room + exclusion zones from UI
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
        source = 'manual_zones'

    # Publish waypoints to ROS 2 cobot via MQTT
    client = mqtt.Client()
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
    client = mqtt.Client()
    client.connect('localhost', 1883)
    client.publish('cobot/command', json.dumps({'cmd': 'stop'}))
    client.disconnect()
    return {'status': 'stopped'}