#!/usr/bin/env python3

from fastapi import APIRouter
import paho.mqtt.client as mqtt
import json

router = APIRouter()
latest = {"position": {}, "imu": {}}

@router.get("/position")
def get_position():
    return latest["position"]

@router.get("/imu")
def get_imu():
    return latest["imu"]