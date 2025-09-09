# Smart Tourist Safety — Working Prototype

This is a **single-repo runnable demo** showing:
- Tourist registration with a **hash-chained append-only ledger** (blockchain-like mock).
- Tourist **mobile-like web app**: live location, **panic button**, simulated walk.
- **Geofencing** alerts and **route deviation** alerts.
- **Police dashboard** with real-time alerts over **WebSockets**.
- Ledger integrity check.

> ⚠️ Focused for hackathon demo: minimal dependencies, runs locally with FastAPI.

## Quick Start

### 1) Install & Run (Python 3.10+)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```
Open:
- Tourist App → http://127.0.0.1:8000/tourist
- Police Dashboard → http://127.0.0.1:8000/dashboard

### 2) Demo Flow
1. Tourist page → click **Register Tourist**.
2. Click **Start Simulated Walk** to start sending GPS pings.
3. Open Dashboard → you will see **live alerts** for geofence / route deviation.
4. On Tourist page, click **PANIC** → dashboard gets a red alert.
5. Check ledger integrity: http://127.0.0.1:8000/ledger/verify

## How it Works

- **Ledger (`blockchain_mock.py`)**: Append-only JSONL with `prev_hash` → `hash` chain, so any tampering breaks verification.
- **Geofence (`geofence.py`)**: High-risk polygon; if tourist enters, dashboard gets an alert.
- **Anomalies (`anomaly.py`)**:
  - Deviation from planned itinerary if current point is >3km away from all planned points.
  - (Extend) Inactivity if no updates for X minutes (hook is provided).
- **WebSocket**: `/ws/alerts` pushes real-time alerts to dashboards.

## Extend (for Finals)

- Replace mock ledger with a real smart contract (Hardhat + Polygon Amoy).
- Persist data in a DB (Postgres) and add auth (JWT).
- Integrate SMS/email to emergency contacts on PANIC using providers.
- Add multilingual UI and voice-triggered PANIC (Web Speech API).
- Add IoT stream (ESP32) or phone sensor streams for heartbeat/accelerometer.

## Folder Structure
```
backend/
  app.py
  anomaly.py
  geofence.py
  blockchain_mock.py
  requirements.txt
  templates/
    index.html
    tourist.html
    dashboard.html
  static/
  ledger.jsonl (created at runtime)
```

## Notes
- Coordinates set near Guwahati for demo.
- This is a prototype to **show the flow end-to-end** in 5 minutes.
```
Tourist → register → walk → triggers → dashboard alerts → ledger-proof
```
