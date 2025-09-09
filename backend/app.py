from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any
import time, asyncio, uuid

from anomaly import deviation_from_route, inactivity
from geofence import in_high_risk_zone
from blockchain_mock import append_entry, verify_chain

app = FastAPI(title="Smart Tourist Safety (Prototype)")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# In-memory stores (for prototype)
TOURISTS: Dict[str, Dict[str, Any]] = {}
ALERTS: List[Dict[str, Any]] = []
DASHBOARD_CLIENTS: List[WebSocket] = []

class RegisterBody(BaseModel):
    name: str
    passport_or_aadhaar_hash: str
    emergency_contact: str
    itinerary: List[Dict[str, float]]  # [{lat, lng}]

class LocationBody(BaseModel):
    tourist_id: str
    lat: float
    lng: float

def broadcast_alert(alert: Dict[str, Any]):
    ALERTS.append(alert)
    # Push to all connected dashboards
    to_remove = []
    for ws in DASHBOARD_CLIENTS:
        try:
            asyncio.create_task(ws.send_json({"type":"alert", "data":alert}))
        except:
            to_remove.append(ws)
    for ws in to_remove:
        if ws in DASHBOARD_CLIENTS:
            DASHBOARD_CLIENTS.remove(ws)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/tourist", response_class=HTMLResponse)
async def tourist_page(request: Request):
    return templates.TemplateResponse("tourist.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/register")
async def register(body: RegisterBody):
    tourist_id = str(uuid.uuid4())
    TOURISTS[tourist_id] = {
        "id": tourist_id,
        "name": body.name,
        "emergency_contact": body.emergency_contact,
        "itinerary": body.itinerary,
        "last_location": None,
        "last_update": None,
        "safety_score": 80, # start baseline
        "active": True,
    }
    # Append to blockchain-like ledger
    entry = append_entry({"event":"REGISTER","tourist_id":tourist_id,"kyc_hash":body.passport_or_aadhaar_hash})
    return {"tourist_id": tourist_id, "ledger_hash": entry["hash"]}

@app.post("/location")
async def update_location(body: LocationBody):
    t = TOURISTS.get(body.tourist_id)
    if not t:
        return JSONResponse({"error":"invalid tourist_id"}, status_code=404)
    t["last_location"] = {"lat": body.lat, "lng": body.lng}
    t["last_update"] = time.time()

    # Geofence check
    if in_high_risk_zone(body.lat, body.lng):
        alert = {"type":"GEOFENCE", "tourist_id": t["id"], "name": t["name"], "location": t["last_location"], "ts": time.time(), "msg":"Entered high-risk zone"}
        broadcast_alert(alert)
        append_entry({"event":"GEOFENCE_ALERT","tourist_id":t["id"],"loc":t["last_location"]})

    # Route deviation check
    if deviation_from_route((body.lat, body.lng), t["itinerary"], threshold_km=3.0):
        alert = {"type":"DEVIATION", "tourist_id": t["id"], "name": t["name"], "location": t["last_location"], "ts": time.time(), "msg":"Deviated from planned route"}
        broadcast_alert(alert)
        append_entry({"event":"ROUTE_DEVIATION","tourist_id":t["id"],"loc":t["last_location"]})

    return {"ok": True}

@app.post("/panic")
async def panic(tourist_id: str = Form(...), lat: float = Form(...), lng: float = Form(...)):
    t = TOURISTS.get(tourist_id)
    if not t:
        return JSONResponse({"error":"invalid tourist_id"}, status_code=404)
    alert = {"type":"PANIC", "tourist_id": t["id"], "name": t["name"], "location": {"lat":lat,"lng":lng}, "ts": time.time(), "msg":"PANIC button pressed"}
    broadcast_alert(alert)
    append_entry({"event":"PANIC","tourist_id":t["id"],"loc":{"lat":lat,"lng":lng}})
    return {"ok": True}

@app.get("/tourists")
async def list_tourists():
    return list(TOURISTS.values())

@app.get("/alerts")
async def list_alerts():
    return ALERTS

@app.get("/ledger/verify")
async def ledger_verify():
    return {"valid": verify_chain()}

@app.websocket("/ws/alerts")
async def ws_alerts(ws: WebSocket):
    await ws.accept()
    DASHBOARD_CLIENTS.append(ws)
    try:
        # Send recent alerts on connect
        await ws.send_json({"type":"init","data":ALERTS[-50:]})
        while True:
            await ws.receive_text()  # keep alive, ignore incoming
    except WebSocketDisconnect:
        pass
    finally:
        if ws in DASHBOARD_CLIENTS:
            DASHBOARD_CLIENTS.remove(ws)
