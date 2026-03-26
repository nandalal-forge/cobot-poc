#!/usr/bin/env python3

from pydantic import BaseModel
from typing import List, Optional

class SessionIn(BaseModel):
    cobot_id: str
    room_width_m: float = 10.0
    room_height_m: float = 8.0

class ZoneIn(BaseModel):
    zone_type: str
    pixel_coords: List[List[float]]
    metre_coords: List[List[float]]