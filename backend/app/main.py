from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import sessions, zones, telemetry

app = FastAPI(title='Cobot POC API', version='2.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(sessions.router, prefix='/api/sessions', tags=['sessions'])
app.include_router(zones.router, prefix='/api/zones', tags=['zones'])
app.include_router(telemetry.router, prefix='/api/telemetry', tags=['telemetry'])

@app.get('/health')
def health():
    return {'status': 'ok', 'version': '2.0.0'}

@app.get('/')
def root():
    return {'status': 'ok', 'service': 'cobot-poc-api'}