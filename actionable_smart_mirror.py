#!/usr/bin/env python3
"""
Smart Mirror - ACTIONABLE VERSION
Deep interaction within widgets with selectable menu items
"""

import tkinter as tk
import cv2
import mediapipe as mp
import numpy as np
import math
import time
import threading
from datetime import datetime
from collections import deque
import queue

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
            print(f"SWIPE DETECTED: {swipe_direction} (dx={dx}, dy={dy}, dist={distance:.1f})")
            
        return swipe_direction

class InteractiveWidget:
    """Base class for interactive widgets with selectable items"""
    def __init__(self, name):
        self.name = name
        self.items = []
        self.selected_index = 0
        self.is_expanded = False  # Whether we're in selection mode
    
    def get_display_content(self):
        """Get content to display on mirror"""
        if not self.is_expanded:
            return self.get_summary_content()
        else:
            return self.get_menu_content()
    
    def get_summary_content(self):
        """Get summary view content"""
        return f"{self.name} - Press FIST to open menu"
    
    def get_menu_content(self):
        """Get interactive menu content"""
        content = f"📋 {self.name.upper()} MENU:\n"
        for i, item in enumerate(self.items):
            prefix = "👉 " if i == self.selected_index else "   "
            content += f"{prefix}{item['name']}\n"
        content += "\n🎯 FIST=Select  ✌️PEACE=Back  ⬆️⬇️=Navigate"
        return content
    
    def navigate_up(self):
        if self.items:
            self.selected_index = (self.selected_index - 1) % len(self.items)
            return self.items[self.selected_index]['name']
        return None
    
    def navigate_down(self):
        if self.items:
            self.selected_index = (self.selected_index + 1) % len(self.items)
            return self.items[self.selected_index]['name']
        return None
    
    def select_current(self):
        if self.items and self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None
    
    def toggle_expanded(self):
        self.is_expanded = not self.is_expanded
        return self.is_expanded

class WeatherWidget(InteractiveWidget):
    def __init__(self):
        super().__init__("Weather")
        self.items = [
            {'name': 'Current Conditions', 'action': 'show_current'},
            {'name': 'Hourly Forecast', 'action': 'show_hourly'},
            {'name': 'Weekly Forecast', 'action': 'show_weekly'},
            {'name': 'Weather Alerts', 'action': 'show_alerts'},
            {'name': 'Update Location', 'action': 'update_location'}
        ]
    
    def get_summary_content(self):
        return "🌤️ Weather\n22°C, Sunny\nChance of rain: 10%\nWind: 5 mph\n\n👊 FIST to open menu"

class NewsWidget(InteractiveWidget):
    def __init__(self):
        super().__init__("News")
        self.items = [
            {'name': 'Top Headlines', 'action': 'show_headlines'},
            {'name': 'Technology News', 'action': 'show_tech'},
            {'name': 'Local News', 'action': 'show_local'},
            {'name': 'Sports Updates', 'action': 'show_sports'},
            {'name': 'Read Article Aloud', 'action': 'read_aloud'}
        ]
    
    def get_summary_content(self):
        return "📰 Latest News\n• Tech stocks continue rising\n• Local weather update\n• Community events tonight\n\n👊 FIST to open menu"

class CalendarWidget(InteractiveWidget):
    def __init__(self):
        super().__init__("Calendar")
        self.items = [
            {'name': "Today's Schedule", 'action': 'show_today'},
            {'name': 'Upcoming Events', 'action': 'show_upcoming'},
            {'name': 'Add New Event', 'action': 'add_event'},
            {'name': 'Join Next Meeting', 'action': 'join_meeting'},
            {'name': 'Calendar Settings', 'action': 'settings'}
        ]
    
    def get_summary_content(self):
        return "📅 Today's Schedule\n• 9:00 AM - Team Meeting\n• 12:00 PM - Lunch\n• 2:00 PM - Project Review\n\n👊 FIST to open menu"

class TimeWidget(InteractiveWidget):
    def __init__(self):
        super().__init__("Time")
        self.items = [
            {'name': 'Set Alarm', 'action': 'set_alarm'},
            {'name': 'World Clocks', 'action': 'world_clocks'},
            {'name': 'Start Timer', 'action': 'start_timer'},
            {'name': 'Stopwatch', 'action': 'stopwatch'},
            {'name': 'Time Settings', 'action': 'time_settings'}
        ]
    
    def get_summary_content(self):
        return "🕐 Time & Alarms\n⏰ Next alarm: 7:00 AM\n🌍 Multiple time zones\n⏱️ Timer & stopwatch\n\n👊 FIST to open menu"

class ActionableSmartMirror:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Core state
        self.camera_active = False
        self.show_camera_preview = True
        
        # Widgets
        self.widgets = {
            'time': TimeWidget(),
            'weather': WeatherWidget(),
            'news': NewsWidget(),
            'calendar': CalendarWidget()
        }
        self.widget_order = ['time', 'weather', 'news', 'calendar']
        self.current_widget_index = 0
        
        # Gesture components
        self.static_recognizer = SimpleGestureRecognizer()
        self.swipe_detector = ReliableSwipeDetector()
        
        # UI Management
        self.action_queue = queue.Queue()
        self.last_action_time = 0
        self.action_cooldown = 0.5
        
        # Gesture stability
        self.gesture_buffer = deque(maxlen=5)
        self.stable_gesture = None
        
        # Initialize
        self.create_layout()
        self.start_threads()
    
    def setup_window(self):
        self.root.title("Smart Mirror - ACTIONABLE")
        self.root.configure(bg='black')
        self.root.attributes('-fullscreen', False)
        self.root.geometry("1200x800")
        
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind('<KeyPress-c>', lambda e: self.toggle_camera())
        self.root.focus_set()
    
    def get_current_widget(self):
        widget_name = self.widget_order[self.current_widget_index]
        return self.widgets[widget_name]
    
    def create_layout(self):
        # Top section
        self.top_frame = tk.Frame(self.root, bg='black')
        self.top_frame.pack(fill='x', padx=20, pady=20)
        
        self.time_label = tk.Label(
            self.top_frame, 
            text="12:00", 
            font=("Arial", 48, "bold"),
            fg='white', 
            bg='black'
        )
        self.time_label.pack(side='left')
        
        self.weather_status = tk.Label(
            self.top_frame, 
            text="22°C\nSunny", 
            font=("Arial", 24),
            fg='white', 
            bg='black'
        )
        self.weather_status.pack(side='right')
        
        # Center content area
        self.center_frame = tk.Frame(self.root, bg='black')
        self.center_frame.pack(fill='both', expand=True, padx=20)
        
        # Widget indicator
        current_widget = self.get_current_widget()
        self.widget_indicator = tk.Label(
            self.center_frame,
            text=f">>> {current_widget.name.upper()} <<<",
            font=("Arial", 20, "bold"),
            fg='cyan',
            bg='black'
        )
        self.widget_indicator.pack(pady=15)
        
        # Main content area
        self.content_label = tk.Label(
            self.center_frame,
            text=current_widget.get_display_content(),
            font=("Arial", 16),
            fg='white',
            bg='black',
            justify='left',
            anchor='nw'
        )
        self.content_label.pack(fill='both', expand=True)
        
        # Bottom feedback
        self.bottom_frame = tk.Frame(self.root, bg='black')
        self.bottom_frame.pack(fill='x', side='bottom', padx=20, pady=20)
        
        self.gesture_label = tk.Label(
            self.bottom_frame,
            text="👋 Ready for gestures...",
            font=("Arial", 16),
            fg='yellow',
            bg='black'
        )
        self.gesture_label.pack()
        
        self.update_ui()
    
    def start_threads(self):
        self.camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
        self.camera_active = True
        self.camera_thread.start()
    
    def camera_loop(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        with mp_hands.Hands(
            static_image_mode=False,
            model_complexity=0,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6,
            max_num_hands=1
        ) as hands:
            
            frame_count = 0
            while self.camera_active:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                frame_count += 1
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)
                
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
                    self.process_gestures(hand_landmarks.landmark, w, h, frame_count)
                    self.queue_display_update("👋 Hand detected")
                else:
                    self.gesture_buffer.clear()
                    self.stable_gesture = None
                    self.queue_display_update("👋 Ready for gestures...")
                
                if self.show_camera_preview:
                    self.draw_debug_overlay(frame)
                    cv2.imshow('Gesture Recognition', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                time.sleep(0.033)
        
        cap.release()
        cv2.destroyAllWindows()
    
    def process_gestures(self, landmarks, width, height, frame_count):
        # Static gestures
        current_static = self.static_recognizer.recognize_gesture(landmarks)
        self.update_gesture_buffer(current_static)
        
        # Dynamic gestures
        self.swipe_detector.add_hand_position(landmarks, width, height)
        if frame_count % 5 == 0:
            swipe = self.swipe_detector.detect_swipe()
            if swipe:
                self.execute_gesture_action(swipe)
        
        # Execute stable static gesture
        if self.stable_gesture and self.stable_gesture not in ["NO_HAND", "OPEN_HAND", "FINGERS_2", "FINGERS_3", "FINGERS_4"]:
            self.execute_gesture_action(self.stable_gesture)
            self.stable_gesture = None
    
    def update_gesture_buffer(self, gesture):
        self.gesture_buffer.append(gesture)
        
        if len(self.gesture_buffer) == 5:
            if all(g == self.gesture_buffer[0] for g in self.gesture_buffer):
                if self.gesture_buffer[0] != self.stable_gesture:
                    self.stable_gesture = self.gesture_buffer[0]
    
    def execute_gesture_action(self, gesture):
        # Ignore non-actionable gestures
        if gesture in ["OPEN_HAND", "FINGERS_2", "FINGERS_3", "FINGERS_4"]:
            return
        
        current_time = time.time()
        if current_time - self.last_action_time < self.action_cooldown:
            return
        
        self.last_action_time = current_time
        current_widget = self.get_current_widget()
        
        print(f"EXECUTING ACTION: {gesture}")
        
        # Handle gestures based on current state
        if current_widget.is_expanded:
            # In menu mode - different gesture meanings
            if gesture == "SWIPE_UP":
                selected = current_widget.navigate_up()
                self.queue_display_update(f"⬆️ Selected: {selected}")
                self.update_content_display()
            elif gesture == "SWIPE_DOWN":
                selected = current_widget.navigate_down()
                self.queue_display_update(f"⬇️ Selected: {selected}")
                self.update_content_display()
            elif gesture == "FIST":
                self.select_menu_item()
            elif gesture == "PEACE":
                self.close_menu()
            elif gesture in ["SWIPE_LEFT", "SWIPE_RIGHT"]:
                self.queue_display_update("🚫 Use ✌️PEACE to close menu first")
        else:
            # In summary mode - normal navigation
            if gesture == "SWIPE_RIGHT":
                self.next_widget()
            elif gesture == "SWIPE_LEFT":
                self.prev_widget()
            elif gesture == "FIST":
                self.open_menu()
            elif gesture == "THUMBS_UP":
                self.like_current()
            elif gesture == "POINTING":
                self.show_info()
    
    def next_widget(self):
        self.current_widget_index = (self.current_widget_index + 1) % len(self.widget_order)
        widget_name = self.widget_order[self.current_widget_index]
        print(f"WIDGET CHANGE: → {widget_name}")
        self.update_content_display()
        self.queue_display_update(f"➡️ Switched to {widget_name}")
    
    def prev_widget(self):
        self.current_widget_index = (self.current_widget_index - 1) % len(self.widget_order)
        widget_name = self.widget_order[self.current_widget_index]
        print(f"WIDGET CHANGE: ← {widget_name}")
        self.update_content_display()
        self.queue_display_update(f"⬅️ Switched to {widget_name}")
    
    def open_menu(self):
        current_widget = self.get_current_widget()
        current_widget.toggle_expanded()
        print(f"MENU OPENED: {current_widget.name}")
        self.update_content_display()
        self.queue_display_update(f"📋 {current_widget.name} menu opened")
    
    def close_menu(self):
        current_widget = self.get_current_widget()
        current_widget.toggle_expanded()
        print(f"MENU CLOSED: {current_widget.name}")
        self.update_content_display()
        self.queue_display_update(f"📋 {current_widget.name} menu closed")
    
    def select_menu_item(self):
        current_widget = self.get_current_widget()
        selected_item = current_widget.select_current()
        
        if selected_item:
            print(f"MENU ITEM SELECTED: {selected_item['name']} ({selected_item['action']})")
            self.execute_menu_action(selected_item)
            self.queue_display_update(f"✅ Executed: {selected_item['name']}")
    
    def execute_menu_action(self, item):
        """Execute the selected menu item action"""
        action = item['action']
        name = item['name']
        
        # Simulate different actions
        action_messages = {
            'show_current': f"🌤️ Displaying current weather conditions",
            'show_hourly': f"📊 Loading hourly forecast...",
            'show_weekly': f"📅 Loading 7-day forecast...",
            'show_alerts': f"⚠️ Checking weather alerts...",
            'show_headlines': f"📰 Loading top news headlines...",
            'show_tech': f"💻 Loading technology news...",
            'show_local': f"🏠 Loading local news...",
            'show_today': f"📅 Displaying today's schedule...",
            'add_event': f"➕ Opening event creation...",
            'join_meeting': f"📹 Joining next meeting...",
            'set_alarm': f"⏰ Opening alarm settings...",
            'start_timer': f"⏱️ Starting timer interface...",
            'world_clocks': f"🌍 Showing world clocks..."
        }
        
        message = action_messages.get(action, f"🔧 Executing {name}...")
        print(f"ACTION RESULT: {message}")
        
        # You would integrate with real APIs/services here
        # For demo, we'll just show the action message
        self.queue_display_update(message)
    
    def like_current(self):
        current_widget = self.get_current_widget()
        self.queue_display_update(f"💖 Liked {current_widget.name}!")
    
    def show_info(self):
        current_widget = self.get_current_widget()
        self.queue_display_update(f"ℹ️ Info about {current_widget.name}")
    
    def update_content_display(self):
        """Update the main content area"""
        current_widget = self.get_current_widget()
        new_content = current_widget.get_display_content()
        
        def update_ui():
            self.content_label.config(text=new_content)
            self.widget_indicator.config(text=f">>> {current_widget.name.upper()} <<<")
        
        self.root.after(0, update_ui)
    
    def queue_display_update(self, message):
        try:
            self.action_queue.put_nowait(('display', message))
        except queue.Full:
            pass
    
    def update_ui(self):
        # Update time
        current_time = datetime.now().strftime("%H:%M")
        self.time_label.config(text=current_time)
        
        # Process action queue
        self.process_action_queue()
        
        self.root.after(100, self.update_ui)
    
    def process_action_queue(self):
        updates_processed = 0
        while updates_processed < 10:
            try:
                action_type, data = self.action_queue.get_nowait()
                if action_type == 'display':
                    self.gesture_label.config(text=data)
                updates_processed += 1
            except queue.Empty:
                break
    
    def draw_debug_overlay(self, frame):
        h, w = frame.shape[:2]
        current_widget = self.get_current_widget()
        
        # Widget state
        mode = "MENU" if current_widget.is_expanded else "SUMMARY"
        cv2.putText(frame, f"Widget: {current_widget.name} ({mode})", 
                   (10, h - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Selected item in menu mode
        if current_widget.is_expanded:
            selected_item = current_widget.items[current_widget.selected_index]['name']
            cv2.putText(frame, f"Selected: {selected_item}", 
                       (10, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Instructions
        instructions = "MENU: ⬆️⬇️=Navigate 👊=Select ✌️=Back" if current_widget.is_expanded else "NAV: ⬅️➡️=Switch 👊=Menu"
        cv2.putText(frame, instructions, 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def toggle_camera(self):
        self.show_camera_preview = not self.show_camera_preview
        status = "ON" if self.show_camera_preview else "OFF"
        print(f"Camera preview: {status}")
    
    def run(self):
        try:
            print("🪞 ACTIONABLE SMART MIRROR")
            print("\n🎯 NAVIGATION MODE (default):")
            print("  ⬅️ SWIPE LEFT/RIGHT → Switch widgets")
            print("  👊 FIST → Open current widget menu")
            print("  👍 THUMBS UP → Like current widget")
            print("  ☝️ POINTING → Show info")
            
            print("\n📋 MENU MODE (when menu is open):")
            print("  ⬆️ SWIPE UP/DOWN → Navigate menu items")
            print("  👊 FIST → Select highlighted item")
            print("  ✌️ PEACE → Close menu and return")
            
            print("\n⌨️ KEYBOARD:")
            print("  ESC → Exit")
            print("  C → Toggle camera preview")
            
            print("\n🚀 Try opening a menu with FIST gesture!")
            self.root.mainloop()
        finally:
            self.camera_active = False
            cv2.destroyAllWindows()

if __name__ == "__main__":
    app = ActionableSmartMirror()
    app.run()