#!/usr/bin/env python3
"""
Quick FastAPI Test Server for React Feasibility
Run this to test WebSocket gesture streaming
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import time
import cv2
from actionable_smart_mirror import RealGestureRecognizer
import math
from collections import deque
from typing import AsyncGenerator, Optional

app = FastAPI(title="Smart Mirror - Real Gesture Recognition")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global gesture recognizer
gesture_recognizer = RealGestureRecognizer()

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Real gesture recognition API",
        "timestamp": time.time()
    }

@app.websocket("/ws/gestures")
async def real_gesture_websocket(websocket: WebSocket):
    """WebSocket endpoint streaming REAL gesture recognition data"""
    await websocket.accept()
    print("🔌 Client connected - starting REAL gesture recognition")
    
    try:
        async for gesture_data in gesture_recognizer.recognize_gestures():
            await websocket.send_text(json.dumps(gesture_data))
            
    except WebSocketDisconnect:
        print("🔌 Client disconnected from real gesture stream")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        await gesture_recognizer.stop_camera()

if __name__ == "__main__":
    print("🚀 Starting Smart Mirror with REAL Gesture Recognition...")
    print("📍 Server: http://localhost:8000")
    print("📍 WebSocket: ws://localhost:8000/ws/gestures")
    print("🎥 This will use your actual camera and MediaPipe!")
    print("👋 Make gestures to see them detected in React!")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


















