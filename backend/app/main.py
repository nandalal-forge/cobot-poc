#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import sessions, zones, telemetry

app = FastAPI(title="Cobot POC API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router, prefix="/api/sessions")
app.include_router(zones.router, prefix="/api/zones")
app.include_router(telemetry.router, prefix="/api/telemetry")

@app.get("/")
def root():
    return {"status": "ok", "service": "cobot-poc-api"}