#!/usr/bin/env python3

from fastapi import APIRouter
from ..models.schemas import ZoneIn

router = APIRouter()
zones_store = []

@router.post("/")
def add_zone(zone: ZoneIn):
    zones_store.append(zone.dict())
    return {"status": "added", "total": len(zones_store)}

@router.get("/")
def get_zones():
    return zones_store

@router.delete("/")
def clear_zones():
    zones_store.clear()
    return {"status": "cleared"}