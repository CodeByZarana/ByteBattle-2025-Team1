#!/usr/bin/env python3
"""
Smart Mirror - Complete App with Camera Preview for Testing
Shows both the mirror interface AND a camera window with hand landmarks
"""

import tkinter as tk
from tkinter import ttk
import cv2
import mediapipe as mp
import numpy as np
import math
import time
import threading
from datetime import datetime
from collections import deque

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

class AdvancedSmartMirrorGestures:
    def __init__(self):
        self.finger_tips = [4, 8, 12, 16, 20]
        self.hand_positions = deque(maxlen=10)
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.8
        self.swipe_threshold = 150
        
    def update_hand_position(self, landmarks, frame_width, frame_height):
        if landmarks:
            index_tip = landmarks[8]
            x = int(index_tip.x * frame_width)
            y = int(index_tip.y * frame_height)
            
            current_time = time.time()
            self.hand_positions.append({'x': x, 'y': y, 'time': current_time})
            return (x, y)
        return None
    
    def detect_swipe(self):
        if len(self.hand_positions) < 5:
            return None
        
        start_pos = self.hand_positions[0]
        end_pos = self.hand_positions[-1]
        
        dx = end_pos['x'] - start_pos['x']
        dy = end_pos['y'] - start_pos['y']
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > self.swipe_threshold:
            if abs(dx) > abs(dy):
                return "SWIPE_RIGHT" if dx > 0 else "SWIPE_LEFT"
            else:
                return "SWIPE_DOWN" if dy > 0 else "SWIPE_UP"
        return None
    
    def recognize_dynamic_gesture(self, landmarks, frame_width, frame_height):
        current_time = time.time()
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return None
        
        self.update_hand_position(landmarks, frame_width, frame_height)
        swipe = self.detect_swipe()
        
        if swipe:
            self.last_gesture_time = current_time
            self.hand_positions.clear()
            return swipe
        return None

class SmartMirrorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Core components
        self.camera_active = False
        self.current_widget = "news"  # Start with news
        self.show_camera_preview = True  # FOR TESTING
        
        # Gesture recognizers
        self.static_recognizer = SimpleGestureRecognizer()
        self.dynamic_recognizer = AdvancedSmartMirrorGestures()
        
        # Action cooldown
        self.last_action_time = 0
        self.action_cooldown = 1.0
        
        # Initialize UI
        self.create_layout()
        
        # Start camera thread
        self.start_camera_thread()
    
    def setup_window(self):
        """Configure the main window"""
        self.root.title("Smart Mirror")
        self.root.configure(bg='black')
        self.root.attributes('-fullscreen', False)  # Set True for mirror mode
        self.root.geometry("1200x800")  # For development
        
        # Exit on ESC
        self.root.bind('<Escape>', lambda e: self.root.quit())
        # Toggle camera preview with 'c' key
        self.root.bind('<KeyPress-c>', lambda e: self.toggle_camera_preview())
        self.root.focus_set()  # Make sure window can receive key events
    
    def toggle_camera_preview(self):
        """Toggle camera preview window"""
        self.show_camera_preview = not self.show_camera_preview
        print(f"Camera preview: {'ON' if self.show_camera_preview else 'OFF'}")
    
    def create_layout(self):
        """Create the main UI layout"""
        # Top row - Time and Weather
        self.top_frame = tk.Frame(self.root, bg='black')
        self.top_frame.pack(fill='x', padx=20, pady=20)
        
        # Time widget (left)
        self.time_label = tk.Label(
            self.top_frame, 
            text="12:00", 
            font=("Arial", 48, "bold"),
            fg='white', 
            bg='black'
        )
        self.time_label.pack(side='left')
        
        # Weather widget (right)
        self.weather_label = tk.Label(
            self.top_frame, 
            text="22°C\nSunny", 
            font=("Arial", 24),
            fg='white', 
            bg='black',
            justify='right'
        )
        self.weather_label.pack(side='right')
        
        # Center - Main content area
        self.center_frame = tk.Frame(self.root, bg='black')
        self.center_frame.pack(fill='both', expand=True, padx=20)
        
        # News/Calendar area
        self.content_label = tk.Label(
            self.center_frame,
            text="📰 Latest News\n• Tech stocks rising\n• Weather update coming\n• Local events tonight",
            font=("Arial", 18),
            fg='white',
            bg='black',
            justify='left',
            anchor='nw'
        )
        self.content_label.pack(fill='both', expand=True)
        
        # Bottom - Gesture feedback
        self.bottom_frame = tk.Frame(self.root, bg='black')
        self.bottom_frame.pack(fill='x', side='bottom', padx=20, pady=20)
        
        self.gesture_label = tk.Label(
            self.bottom_frame,
            text="👋 Ready for gestures... (Press 'c' to toggle camera preview)",
            font=("Arial", 16),
            fg='cyan',
            bg='black'
        )
        self.gesture_label.pack()
        
        # Start UI updates
        self.update_ui()
    
    def update_ui(self):
        """Update UI elements periodically"""
        # Update time
        current_time = datetime.now().strftime("%H:%M")
        self.time_label.config(text=current_time)
        
        # Schedule next update
        self.root.after(1000, self.update_ui)  # Update every second
    
    def start_camera_thread(self):
        """Start camera processing in separate thread"""
        self.camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
        self.camera_active = True
        self.camera_thread.start()
    
    def camera_loop(self):
        """Camera processing loop with gesture recognition AND optional preview"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        with mp_hands.Hands(
            static_image_mode=False,
            model_complexity=0,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            max_num_hands=1
        ) as hands:
        
            while self.camera_active:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Process frame for gesture recognition
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)
                
                current_gesture = "NO_HAND"
                dynamic_gesture = None
                
                # Detect gestures
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    
                    # Draw landmarks on frame for preview
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
                    # Static gestures
                    current_gesture = self.static_recognizer.recognize_gesture(hand_landmarks.landmark)
                    
                    # Dynamic gestures
                    dynamic_gesture = self.dynamic_recognizer.recognize_dynamic_gesture(
                        hand_landmarks.landmark, w, h
                    )
                    
                    # Handle gestures
                    if dynamic_gesture:
                        self.handle_gesture(dynamic_gesture)
                        self.update_gesture_feedback(f"🌀 {dynamic_gesture}")
                    elif current_gesture != "NO_HAND":
                        self.handle_gesture(current_gesture)
                        self.update_gesture_feedback(f"👋 {current_gesture}")
                    else:
                        self.update_gesture_feedback("👋 Hand detected - make a gesture")
                else:
                    self.update_gesture_feedback("👋 Ready for gestures...")
                
                # Show camera preview if enabled
                if self.show_camera_preview:
                    # Add gesture info to camera feed
                    if current_gesture != "NO_HAND":
                        cv2.putText(frame, f"Static: {current_gesture}", 
                                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    if dynamic_gesture:
                        cv2.putText(frame, f"Dynamic: {dynamic_gesture}", 
                                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                    
                    # Show current widget
                    cv2.putText(frame, f"Widget: {self.current_widget}", 
                               (10, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                    
                    cv2.imshow('Camera Preview - Gesture Recognition', frame)
                
                # Handle OpenCV window events
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                time.sleep(0.033)  # ~30 FPS
        
        cap.release()
        cv2.destroyAllWindows()
    
    def can_perform_action(self):
        """Check if enough time has passed since last action"""
        current_time = time.time()
        if current_time - self.last_action_time > self.action_cooldown:
            self.last_action_time = current_time
            return True
        return False
    
    def update_gesture_feedback(self, message):
        """Update gesture feedback label (thread-safe)"""
        def update():
            self.gesture_label.config(text=f"🎯 {message}")
        
        self.root.after(0, update)
    
    def handle_gesture(self, gesture):
        """Handle detected gestures"""
        if not self.can_perform_action():
            return
            
        if gesture == "SWIPE_RIGHT":
            self.next_widget()
        elif gesture == "SWIPE_LEFT":
            self.prev_widget()
        elif gesture == "FIST":
            self.activate_widget()
        elif gesture == "PEACE":
            self.toggle_settings()
        elif gesture == "THUMBS_UP":
            self.like_action()
    
    def next_widget(self):
        """Switch to next widget"""
        widgets = ["time", "weather", "news", "calendar"]
        current_index = widgets.index(self.current_widget)
        next_index = (current_index + 1) % len(widgets)
        self.current_widget = widgets[next_index]
        self.update_content_display()
        print(f"Switched to: {self.current_widget}")
    
    def prev_widget(self):
        """Switch to previous widget"""
        widgets = ["time", "weather", "news", "calendar"]
        current_index = widgets.index(self.current_widget)
        prev_index = (current_index - 1) % len(widgets)
        self.current_widget = widgets[prev_index]
        self.update_content_display()
        print(f"Switched to: {self.current_widget}")
    
    def update_content_display(self):
        """Update the main content area based on current widget"""
        content_map = {
            "time": "🕐 Current Time Focus\n⏰ Set alarms\n🌍 World clocks\n⏱️ Stopwatch & timers",
            "weather": "🌤️ Weather Information\n🌡️ 22°C, Sunny\n🌧️ Chance of rain: 10%\n💨 Wind: 5 mph\n📅 7-day forecast",
            "news": "📰 Latest News\n📈 Tech stocks rising\n🌦️ Weather update\n🎉 Local events tonight\n💼 Business headlines",
            "calendar": "📅 Today's Schedule\n• 9:00 AM - Team Meeting\n• 12:00 PM - Lunch\n• 2:00 PM - Project Review\n• 6:00 PM - Gym"
        }
        
        def update_ui():
            self.content_label.config(text=content_map.get(self.current_widget, "Unknown widget"))
        
        self.root.after(0, update_ui)
    
    def activate_widget(self):
        """Activate/interact with current widget"""
        actions = {
            "time": "⏰ Alarm set for 7:00 AM",
            "weather": "🌤️ Updated weather data",
            "news": "📰 Refreshing news feed...",
            "calendar": "📅 Added reminder"
        }
        
        action_text = actions.get(self.current_widget, f"Activated {self.current_widget}!")
        self.update_gesture_feedback(f"✅ {action_text}")
        print(f"Activated: {self.current_widget}")
    
    def toggle_settings(self):
        """Toggle settings mode"""
        self.update_gesture_feedback("⚙️ Settings toggled")
        print("Settings toggled")
    
    def like_action(self):
        """Like/favorite current item"""
        self.update_gesture_feedback("💖 Liked current item!")
        print("Liked current widget")
    
    def run(self):
        """Start the application"""
        try:
            print("🪞 Smart Mirror Starting...")
            print("Gesture controls:")
            print("  👊 FIST → Select/Activate")
            print("  ⬅️ SWIPE LEFT → Previous widget")
            print("  ➡️ SWIPE RIGHT → Next widget")
            print("  ✌️ PEACE → Settings")
            print("  👍 THUMBS UP → Like")
            print("\nCamera controls:")
            print("  Press 'c' → Toggle camera preview window")
            print("  Press ESC → Exit")
            self.root.mainloop()
        finally:
            self.camera_active = False
            cv2.destroyAllWindows()
            print("Smart Mirror stopped")

if __name__ == "__main__":
    app = SmartMirrorApp()
    app.run()