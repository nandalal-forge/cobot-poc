from pydantic import BaseModel
from typing import List, Optional

class SessionIn(BaseModel):
    cobot_id: str = 'cobot_01'
    room_width_m: float = 10.0
    room_height_m: float = 8.0
    use_slam_map: bool = True

class ZoneIn(BaseModel):
    name: str = 'zone'
    zone_type: str
    pixel_coords: List[List[float]]
    metre_coords: List[List[float]]

class TelemetryOut(BaseModel):
    x: float
    y: float
    timestamp: str