#!/usr/bin/env python3
"""
Smart Mirror FastAPI Server - REAL GESTURE RECOGNITION
Integrates your existing MediaPipe gesture code with FastAPI WebSocket
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import time
import cv2
import mediapipe as mp
import numpy as np
import math
from collections import deque
from typing import AsyncGenerator, Optional

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

class SimpleGestureRecognizer:
    def __init__(self):
        self.finger_tips = [4, 8, 12, 16, 20]
        self.finger_pips = [3, 6, 10, 14, 18]
        
    def is_finger_up(self, landmarks, finger_idx):
        tip_idx = self.finger_tips[finger_idx]
        pip_idx = self.finger_pips[finger_idx]
        
        if finger_idx == 0:  # Thumb
            return landmarks[tip_idx].x > landmarks[pip_idx].x
        return landmarks[tip_idx].y < landmarks[pip_idx].y
    
    def count_fingers(self, landmarks):
        fingers_up = []
        for i in range(5):
            fingers_up.append(self.is_finger_up(landmarks, i))
        return fingers_up, sum(fingers_up)
    
    def recognize_gesture(self, landmarks):
        fingers_up, total_fingers = self.count_fingers(landmarks)
        
        if total_fingers == 0:
            return "FIST"
        elif total_fingers == 5:
            return "OPEN_HAND"
        elif total_fingers == 1 and fingers_up[1]:
            return "POINTING"
        elif total_fingers == 2 and fingers_up[1] and fingers_up[2]:
            return "PEACE"
        elif total_fingers == 1 and fingers_up[0]:
            return "THUMBS_UP"
        else:
            return f"FINGERS_{total_fingers}"

class ReliableSwipeDetector:
    def __init__(self):
        self.hand_positions = deque(maxlen=12)
        self.last_swipe_time = 0
        self.swipe_cooldown = 1.5
        self.swipe_threshold = 100
        
    def add_hand_position(self, landmarks, frame_width, frame_height):
        if landmarks and len(landmarks) > 8:
            index_tip = landmarks[8]
            x = int(index_tip.x * frame_width)
            y = int(index_tip.y * frame_height)
            
            current_time = time.time()
            self.hand_positions.append({'x': x, 'y': y, 'time': current_time})
            return True
        return False
    
    def detect_swipe(self):
        current_time = time.time()
        
        if current_time - self.last_swipe_time < self.swipe_cooldown:
            return None
        
        if len(self.hand_positions) < 8:
            return None
        
        positions = list(self.hand_positions)
        start_pos = positions[0]
        end_pos = positions[-1]
        
        dx = end_pos['x'] - start_pos['x']
        dy = end_pos['y'] - start_pos['y']
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < self.swipe_threshold:
            return None
        
        swipe_direction = None
        if abs(dx) > abs(dy) and abs(dx) > 80:
            swipe_direction = "SWIPE_RIGHT" if dx > 0 else "SWIPE_LEFT"
        elif abs(dy) > abs(dx) and abs(dy) > 80:
            swipe_direction = "SWIPE_DOWN" if dy > 0 else "SWIPE_UP"
        
        if swipe_direction:
            self.last_swipe_time = current_time
            self.hand_positions.clear()
            print(f"REAL SWIPE DETECTED: {swipe_direction} (dx={dx}, dy={dy}, dist={distance:.1f})")
            
        return swipe_direction

class RealGestureRecognizer:
    """Real-time gesture recognition for FastAPI WebSocket streaming"""
    
    def __init__(self):
        self.static_recognizer = SimpleGestureRecognizer()
        self.swipe_detector = ReliableSwipeDetector()
        
        # Gesture stability tracking
        self.gesture_buffer = deque(maxlen=5)
        self.stable_gesture = None
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.5
        
        # Camera setup
        self.cap = None
        self.hands = None
        
        # Widget simulation (for React testing)
        self.widgets = ["time", "weather", "news", "calendar"]
        self.current_widget_index = 0
        
    async def start_camera(self):
        """Initialize camera and MediaPipe"""
        try:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            self.hands = mp_hands.Hands(
                static_image_mode=False,
                model_complexity=0,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.6,
                max_num_hands=1
            )
            
            print("📷 Camera and MediaPipe initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize camera: {e}")
            return False
    
    async def stop_camera(self):
        """Cleanup camera resources"""
        if self.cap:
            self.cap.release()
        if self.hands:
            self.hands.close()
        print("📷 Camera resources released")
    
    def update_gesture_buffer(self, gesture):
        """Update gesture buffer and determine stable gesture"""
        self.gesture_buffer.append(gesture)
        
        if len(self.gesture_buffer) == 5:
            if all(g == self.gesture_buffer[0] for g in self.gesture_buffer):
                if self.gesture_buffer[0] != self.stable_gesture:
                    # Only process actionable gestures
                    if self.gesture_buffer[0] not in ["NO_HAND", "OPEN_HAND", "FINGERS_2", "FINGERS_3", "FINGERS_4"]:
                        self.stable_gesture = self.gesture_buffer[0]
                        return True
        return False
    
    def handle_widget_action(self, gesture):
        """Simulate widget actions for React demo"""
        current_time = time.time()
        
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return None
        
        self.last_gesture_time = current_time
        
        if gesture == "SWIPE_RIGHT":
            self.current_widget_index = (self.current_widget_index + 1) % len(self.widgets)
            return f"Switched to {self.widgets[self.current_widget_index]}"
        elif gesture == "SWIPE_LEFT":
            self.current_widget_index = (self.current_widget_index - 1) % len(self.widgets)
            return f"Switched to {self.widgets[self.current_widget_index]}"
        elif gesture == "FIST":
            return f"Activated {self.widgets[self.current_widget_index]}"
        elif gesture == "PEACE":
            return "Opened menu"
        elif gesture == "THUMBS_UP":
            return "Liked content"
        elif gesture == "POINTING":
            return "Showing info"
        
        return None
    
    async def recognize_gestures(self) -> AsyncGenerator[dict, None]:
        """Main gesture recognition loop - yields gesture data for WebSocket"""
        
        if not await self.start_camera():
            return
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    await asyncio.sleep(0.1)
                    continue
                
                frame_count += 1
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process with MediaPipe
                results = self.hands.process(rgb_frame)
                
                current_gesture = None
                swipe_gesture = None
                action_result = None
                
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    
                    # Static gesture recognition
                    static_gesture = self.static_recognizer.recognize_gesture(hand_landmarks.landmark)
                    stable_changed = self.update_gesture_buffer(static_gesture)
                    
                    if stable_changed and self.stable_gesture:
                        current_gesture = self.stable_gesture
                        action_result = self.handle_widget_action(self.stable_gesture)
                        self.stable_gesture = None  # Reset
                    
                    # Dynamic gesture recognition (every 3rd frame for stability)
                    self.swipe_detector.add_hand_position(hand_landmarks.landmark, w, h)
                    if frame_count % 3 == 0:
                        swipe_gesture = self.swipe_detector.detect_swipe()
                        if swipe_gesture:
                            current_gesture = swipe_gesture
                            action_result = self.handle_widget_action(swipe_gesture)
                    
                    # Send gesture data to React
                    if current_gesture:
                        gesture_data = {
                            "type": "gesture_detected",
                            "gesture": {
                                "name": current_gesture,
                                "confidence": 0.9,  # You could calculate real confidence
                                "type": "swipe" if swipe_gesture else "static",
                                "timestamp": time.time(),
                                "frame_count": frame_count
                            },
                            "widget_state": {
                                "current": self.widgets[self.current_widget_index],
                                "menu_open": False
                            },
                            "action_result": action_result
                        }
                        
                        print(f"📤 Sending REAL gesture: {current_gesture}")
                        yield gesture_data
                
                else:
                    # No hand detected - reset buffers
                    self.gesture_buffer.clear()
                    self.stable_gesture = None
                
                # Control frame rate
                await asyncio.sleep(0.033)  # ~30 FPS
                
        except Exception as e:
            print(f"❌ Gesture recognition error: {e}")
        finally:
            await self.stop_camera()