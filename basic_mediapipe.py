import cv2
import mediapipe as mp
import numpy as np
import math
import time

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

import cv2
import mediapipe as mp
import matplotlib.pyplot as plt

# Initialize MediaPipe hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def detect_hands_in_image(image_path):
    """Detect hands in a static image"""
    
    # Initialize the hand detector
    with mp_hands.Hands(
        static_image_mode=True,      # For static images
        max_num_hands=2,             # Detect up to 2 hands
        min_detection_confidence=0.5  # Minimum confidence threshold
    ) as hands:
        
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Could not read image: {image_path}")
            return
        
        # Convert BGR to RGB (MediaPipe uses RGB)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image
        results = hands.process(rgb_image)
        
        # Draw hand landmarks if detected
        if results.multi_hand_landmarks:
            print(f"Detected {len(results.multi_hand_landmarks)} hand(s)")
            
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks and connections
                mp_drawing.draw_landmarks(
                    image, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
        else:
            print("No hands detected")
        
        # Display the result
        cv2.imshow('Hand Detection', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return results

# Usage (create a test image or use webcam capture)
# detect_hands_in_image('thumbs-up.png')

def basic_webcam_detection():
    """Basic real-time hand detection from webcam"""
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Initialize MediaPipe hands
    with mp_hands.Hands(
        model_complexity=0,          # Faster but less accurate
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        max_num_hands=2
    ) as hands:
        
        print("Starting hand detection. Press 'q' to quit.")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = hands.process(rgb_frame)
            
            # Draw landmarks
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        mp_hands.HAND_CONNECTIONS
                    )
            
            # Display FPS
            fps = cap.get(cv2.CAP_PROP_FPS)
            cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display the frame
            cv2.imshow('Basic Hand Detection', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()

# Run the basic detection
# basic_webcam_detection()

# Define landmark names for better understanding
LANDMARK_NAMES = [
    'WRIST',           # 0
    'THUMB_CMC',       # 1
    'THUMB_MCP',       # 2
    'THUMB_IP',        # 3
    'THUMB_TIP',       # 4
    'INDEX_FINGER_MCP', # 5
    'INDEX_FINGER_PIP', # 6
    'INDEX_FINGER_DIP', # 7
    'INDEX_FINGER_TIP', # 8
    'MIDDLE_FINGER_MCP', # 9
    'MIDDLE_FINGER_PIP', # 10
    'MIDDLE_FINGER_DIP', # 11
    'MIDDLE_FINGER_TIP', # 12
    'RING_FINGER_MCP',  # 13
    'RING_FINGER_PIP',  # 14
    'RING_FINGER_DIP',  # 15
    'RING_FINGER_TIP',  # 16
    'PINKY_MCP',       # 17
    'PINKY_PIP',       # 18
    'PINKY_DIP',       # 19
    'PINKY_TIP'        # 20
]

# Finger tip indices for easy access
FINGER_TIPS = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
FINGER_MCP = [1, 5, 9, 13, 17]    # Metacarpophalangeal joints

def extract_landmarks(hand_landmarks, image_width, image_height):
    """Extract landmark coordinates from MediaPipe results"""
    landmarks = []
    
    for i, landmark in enumerate(hand_landmarks.landmark):
        # Convert normalized coordinates to pixel coordinates
        x = int(landmark.x * image_width)
        y = int(landmark.y * image_height)
        z = landmark.z  # Relative depth
        
        landmarks.append({
            'id': i,
            'name': LANDMARK_NAMES[i],
            'x': x,
            'y': y,
            'z': z,
            'normalized': {
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z
            }
        })
    
    return landmarks

def print_landmark_info(landmarks):
    """Print landmark information for debugging"""
    print("\nHand Landmarks:")
    print("-" * 50)
    for landmark in landmarks:
        print(f"{landmark['id']:2d} {landmark['name']:20s} "
              f"({landmark['x']:3d}, {landmark['y']:3d}) "
              f"z:{landmark['z']:6.3f}")

def visualize_landmarks_detailed():
    """Detailed landmark visualization with labels"""
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    with mp_hands.Hands(
        model_complexity=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
        max_num_hands=1  # Focus on one hand for clarity
    ) as hands:
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Extract landmark data
                    h, w, c = frame.shape
                    landmarks = extract_landmarks(hand_landmarks, w, h)
                    
                    # Draw connections
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                    )
                    
                    # Draw landmark numbers and names for finger tips
                    for landmark in landmarks:
                        if landmark['id'] in FINGER_TIPS:  # Only finger tips
                            cv2.putText(frame, 
                                      f"{landmark['id']}", 
                                      (landmark['x'] + 10, landmark['y'] - 10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    # Display finger tip coordinates
                    y_offset = 30
                    for tip_id in FINGER_TIPS:
                        tip = landmarks[tip_id]
                        cv2.putText(frame,
                                  f"{tip['name']}: ({tip['x']}, {tip['y']})",
                                  (10, y_offset),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                        y_offset += 25
            
            cv2.imshow('Detailed Landmarks', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()

# visualize_landmarks_detailed()

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
        
def real_time_gesture_recognition():
    """Real-time gesture recognition with simple patterns"""
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    gesture_recognizer = SimpleGestureRecognizer()
    
    # Variables for gesture stability
    gesture_buffer = []
    buffer_size = 5
    stable_gesture = "NONE"
    
    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
        max_num_hands=1
    ) as hands:
        
        print("Gesture Recognition Active. Try these gestures:")
        print("- FIST: Close your hand")
        print("- OPEN_HAND: Open all fingers")
        print("- POINTING: Point with index finger")
        print("- PEACE: Peace sign (index + middle)")
        print("- THUMBS_UP: Thumbs up")
        print("- ROCK_ON: Rock and roll sign")
        print("Press 'q' to quit")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            current_gesture = "NO_HAND"
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Recognize gesture
                    current_gesture = gesture_recognizer.recognize_gesture(
                        hand_landmarks.landmark
                    )
                    
                    # Display finger states for debugging
                    fingers_up, total = gesture_recognizer.count_fingers(
                        hand_landmarks.landmark
                    )
                    
                    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
                    y_offset = 50
                    for i, (finger, is_up) in enumerate(zip(finger_names, fingers_up)):
                        color = (0, 255, 0) if is_up else (0, 0, 255)
                        status = "UP" if is_up else "DOWN"
                        cv2.putText(frame, f"{finger}: {status}",
                                  (10, y_offset + i * 25),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Gesture smoothing using buffer
            gesture_buffer.append(current_gesture)
            if len(gesture_buffer) > buffer_size:
                gesture_buffer.pop(0)
            
            # Update stable gesture if buffer is consistent
            if len(set(gesture_buffer)) == 1 and len(gesture_buffer) == buffer_size:
                stable_gesture = gesture_buffer[0]
            
            # Display current and stable gesture
            cv2.putText(frame, f"Current: {current_gesture}",
                       (10, frame.shape[0] - 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            cv2.putText(frame, f"Stable: {stable_gesture}",
                       (10, frame.shape[0] - 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
            
            # Draw gesture instruction box
            cv2.rectangle(frame, (frame.shape[1] - 300, 10), 
                         (frame.shape[1] - 10, 200), (0, 0, 0), -1)
            cv2.putText(frame, "Gestures:", (frame.shape[1] - 290, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            instructions = [
                "FIST - Close hand",
                "OPEN_HAND - All fingers",
                "POINTING - Index only",
                "PEACE - Index + Middle",
                "THUMBS_UP - Thumb only",
                "ROCK_ON - Thumb+Index+Pinky"
            ]
            
            for i, instruction in enumerate(instructions):
                cv2.putText(frame, instruction, 
                           (frame.shape[1] - 290, 70 + i * 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            
            cv2.imshow('Gesture Recognition', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()

# real_time_gesture_recognition()
import math

class AdvancedGestureAnalyzer:
    def __init__(self):
        self.finger_tips = [4, 8, 12, 16, 20]
        self.finger_mcps = [1, 5, 9, 13, 17]
        
        # Gesture history for temporal analysis
        self.gesture_history = []
        self.history_size = 10
        
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def calculate_angle(self, p1, p2, p3):
        """Calculate angle between three points (p2 is the vertex)"""
        # Vector from p2 to p1
        v1 = (p1.x - p2.x, p1.y - p2.y)
        # Vector from p2 to p3
        v2 = (p3.x - p2.x, p3.y - p2.y)
        
        # Dot product and magnitudes
        dot_product = v1[0]*v2[0] + v1[1]*v2[1]
        mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
        mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
        
        if mag1 == 0 or mag2 == 0:
            return 0
        
        # Calculate angle in degrees
        cos_angle = dot_product / (mag1 * mag2)
        cos_angle = max(-1, min(1, cos_angle))  # Clamp to valid range
        angle = math.acos(cos_angle) * 180 / math.pi
        
        return angle
    
    def get_finger_curl(self, landmarks, finger_idx):
        """Calculate how much a finger is curled (0 = straight, 1 = fully curled)"""
        if finger_idx == 0:  # Thumb - different calculation
            tip = landmarks[4]
            mcp = landmarks[1]
            wrist = landmarks[0]
            
            # Angle between wrist->mcp and mcp->tip
            angle = self.calculate_angle(wrist, mcp, tip)
            # Normalize to 0-1 (assuming 180° = fully curled)
            return min(1.0, angle / 180.0)
        else:
            # For other fingers, use tip, pip, mcp
            tip_idx = self.finger_tips[finger_idx]
            mcp_idx = self.finger_mcps[finger_idx]
            
            # Use pip (proximal interphalangeal joint)
            pip_idx = tip_idx - 2
            
            tip = landmarks[tip_idx]
            pip = landmarks[pip_idx]
            mcp = landmarks[mcp_idx]
            
            # Calculate angle at PIP joint
            angle = self.calculate_angle(mcp, pip, tip)
            
            # Normalize (straight finger ≈ 180°, curled ≈ 0°)
            return 1.0 - (angle / 180.0)
    
    def detect_pointing_direction(self, landmarks):
        """Detect pointing direction for index finger"""
        wrist = landmarks[0]
        index_tip = landmarks[8]
        
        # Calculate direction vector
        dx = index_tip.x - wrist.x
        dy = index_tip.y - wrist.y
        
        # Calculate angle from horizontal (right = 0°)
        angle = math.atan2(-dy, dx) * 180 / math.pi  # Negative dy for screen coords
        
        # Classify direction
        if -45 <= angle <= 45:
            return "RIGHT", angle
        elif 45 < angle <= 135:
            return "UP", angle
        elif -135 <= angle < -45:
            return "DOWN", angle
        else:
            return "LEFT", angle
    
    def detect_hand_orientation(self, landmarks):
        """Detect if hand is facing camera or sideways"""
        # Use thumb and pinky relationship
        thumb_tip = landmarks[4]
        pinky_tip = landmarks[20]
        wrist = landmarks[0]
        
        # Calculate relative positions
        thumb_to_wrist = self.calculate_distance(thumb_tip, wrist)
        pinky_to_wrist = self.calculate_distance(pinky_tip, wrist)
        
        # If thumb is much closer to camera (higher z), hand might be facing away
        z_diff = thumb_tip.z - pinky_tip.z
        
        if abs(z_diff) > 0.1:
            return "SIDEWAYS"
        else:
            return "FRONTAL"
    
    def recognize_advanced_gesture(self, landmarks):
        """Advanced gesture recognition using geometric analysis"""
        
        # Calculate finger curl values
        finger_curls = []
        for i in range(5):
            curl = self.get_finger_curl(landmarks, i)
            finger_curls.append(curl)
        
        # Hand orientation
        orientation = self.detect_hand_orientation(landmarks)
        
        # Advanced gesture patterns
        gesture_info = {
            'curl_values': finger_curls,
            'orientation': orientation,
            'confidence': 0.0
        }
        
        # Gesture classification based on curl patterns
        thumb_curl, index_curl, middle_curl, ring_curl, pinky_curl = finger_curls
        
        # Closed fist - all fingers curled
        if all(curl > 0.6 for curl in finger_curls):
            gesture_info.update({
                'name': 'FIST',
                'confidence': min(finger_curls)
            })
        
        # Open hand - all fingers extended
        elif all(curl < 0.3 for curl in finger_curls):
            gesture_info.update({
                'name': 'OPEN_HAND',
                'confidence': 1.0 - max(finger_curls)
            })
        
        # Pointing - only index extended
        elif (index_curl < 0.3 and 
              all(curl > 0.6 for i, curl in enumerate(finger_curls) if i != 1)):
            direction, angle = self.detect_pointing_direction(landmarks)
            gesture_info.update({
                'name': f'POINT_{direction}',
                'direction': direction,
                'angle': angle,
                'confidence': 1.0 - index_curl
            })
        
        # Peace sign - index and middle extended
        elif (index_curl < 0.3 and middle_curl < 0.3 and 
              thumb_curl > 0.5 and ring_curl > 0.6 and pinky_curl > 0.6):
            gesture_info.update({
                'name': 'PEACE',
                'confidence': 1.0 - max(index_curl, middle_curl)
            })
        
        # Thumbs up - only thumb extended
        elif (thumb_curl < 0.3 and 
              all(curl > 0.6 for i, curl in enumerate(finger_curls) if i != 0)):
            gesture_info.update({
                'name': 'THUMBS_UP',
                'confidence': 1.0 - thumb_curl
            })
        
        # OK sign - thumb and index form circle, others extended
        elif self.is_ok_gesture(landmarks):
            gesture_info.update({
                'name': 'OK_SIGN',
                'confidence': 0.8
            })
        
        else:
            gesture_info.update({
                'name': 'UNKNOWN',
                'confidence': 0.0
            })
        
        # Add to history for temporal analysis
        self.gesture_history.append(gesture_info)
        if len(self.gesture_history) > self.history_size:
            self.gesture_history.pop(0)
        
        return gesture_info
    
    def is_ok_gesture(self, landmarks):
        """Detect OK sign (thumb and index finger forming circle)"""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        # Check if thumb and index finger are close
        distance = self.calculate_distance(thumb_tip, index_tip)
        
        # Also check that other fingers are relatively extended
        middle_curl = self.get_finger_curl(landmarks, 2)
        ring_curl = self.get_finger_curl(landmarks, 3)
        pinky_curl = self.get_finger_curl(landmarks, 4)
        
        return (distance < 0.05 and 
                middle_curl < 0.4 and 
                ring_curl < 0.4 and 
                pinky_curl < 0.4)
    
    def get_stable_gesture(self, confidence_threshold=0.6):
        """Get stable gesture from recent history"""
        if len(self.gesture_history) < 3:
            return None
        
        # Get recent gestures with good confidence
        recent_gestures = [
            g for g in self.gesture_history[-5:] 
            if g['confidence'] >= confidence_threshold
        ]
        
        if not recent_gestures:
            return None
        
        # Find most common gesture
        gesture_names = [g['name'] for g in recent_gestures]
        most_common = max(set(gesture_names), key=gesture_names.count)
        
        # Return if it appears in majority of recent frames
        if gesture_names.count(most_common) >= len(gesture_names) * 0.6:
            return most_common
        
        return None
    
def advanced_gesture_demo():
    """Demo of advanced gesture recognition with detailed analysis"""
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    analyzer = AdvancedGestureAnalyzer()
    
    with mp_hands.Hands(
        model_complexity=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
        max_num_hands=1
    ) as hands:
        
        print("Advanced Gesture Recognition")
        print("Try: FIST, OPEN_HAND, POINTING, PEACE, THUMBS_UP, OK_SIGN")
        print("Press 'q' to quit, 's' to save debug info")
        
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            frame_count += 1
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2),
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                    )
                    
                    # Advanced gesture analysis
                    gesture_info = analyzer.recognize_advanced_gesture(
                        hand_landmarks.landmark
                    )
                    
                    stable_gesture = analyzer.get_stable_gesture()
                    
                    # Display gesture information
                    y_offset = 30
                    
                    # Current gesture
                    cv2.putText(frame, 
                              f"Gesture: {gesture_info['name']}", 
                              (10, y_offset),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                    y_offset += 35
                    
                    # Confidence
                    cv2.putText(frame, 
                              f"Confidence: {gesture_info['confidence']:.2f}", 
                              (10, y_offset),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                    y_offset += 30
                    
                    # Stable gesture
                    if stable_gesture:
                        cv2.putText(frame, 
                                  f"Stable: {stable_gesture}", 
                                  (10, y_offset),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                    y_offset += 40
                    
                    # Finger curl values
                    cv2.putText(frame, "Finger Curl Values:", 
                              (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
                    y_offset += 25
                    
                    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
                    for i, (name, curl) in enumerate(zip(finger_names, gesture_info['curl_values'])):
                        color = (0, 255, 0) if curl < 0.3 else (0, 255, 255) if curl < 0.6 else (0, 0, 255)
                        cv2.putText(frame, 
                                  f"{name}: {curl:.2f}", 
                                  (10, y_offset),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                        y_offset += 20
                    
                    # Special gesture information
                    if 'direction' in gesture_info:
                        cv2.putText(frame, 
                                  f"Direction: {gesture_info['direction']} ({gesture_info['angle']:.1f}°)", 
                                  (10, frame.shape[0] - 60),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
                    
                    # Orientation
                    cv2.putText(frame, 
                              f"Orientation: {gesture_info['orientation']}", 
                              (10, frame.shape[0] - 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
            
            else:
                cv2.putText(frame, "No hand detected", (10, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Display frame info
            cv2.putText(frame, f"Frame: {frame_count}", 
                       (frame.shape[1] - 150, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('Advanced Gesture Recognition', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save current gesture history for analysis
                print(f"\nGesture History (last 10 frames):")
                for i, gesture in enumerate(analyzer.gesture_history[-10:]):
                    print(f"Frame {frame_count-10+i}: {gesture['name']} "
                          f"(confidence: {gesture['confidence']:.2f})")
    
    cap.release()
    cv2.destroyAllWindows()

# advanced_gesture_demo()

import threading
import queue
import time
from collections import deque

class OptimizedGestureProcessor:
    def __init__(self, config=None):
        self.config = config or {}
        
        # Performance settings
        self.target_fps = self.config.get('target_fps', 15)
        self.frame_skip = self.config.get('frame_skip', 1)
        self.roi_enabled = self.config.get('roi_enabled', True)
        self.roi_size = self.config.get('roi_size', 0.6)
        
        # MediaPipe settings
        self.min_detection_confidence = self.config.get('min_detection_confidence', 0.7)
        self.min_tracking_confidence = self.config.get('min_tracking_confidence', 0.5)
        self.model_complexity = self.config.get('model_complexity', 0)
        
        # Processing state
        self.frame_count = 0
        self.last_process_time = 0
        self.fps_history = deque(maxlen=30)
        
        # Gesture state
        self.current_gesture = None
        self.gesture_start_time = 0
        self.gesture_duration_threshold = 0.5  # 500ms
        self.gesture_callback = None
        
        # Threading
        self.frame_queue = queue.Queue(maxsize=2)
        self.result_queue = queue.Queue(maxsize=5)
        self.processing_thread = None
        self.running = False
        
        # Initialize gesture analyzer
        self.analyzer = AdvancedGestureAnalyzer()
        
    def set_gesture_callback(self, callback):
        """Set callback function for gesture events"""
        self.gesture_callback = callback
    
    def extract_roi(self, frame):
        """Extract region of interest from frame"""
        if not self.roi_enabled:
            return frame
        
        h, w = frame.shape[:2]
        roi_h = int(h * self.roi_size)
        roi_w = int(w * self.roi_size)
        
        start_y = (h - roi_h) // 2
        start_x = (w - roi_w) // 2
        
        return frame[start_y:start_y + roi_h, start_x:start_x + roi_w]
    
    def resize_frame(self, frame, max_width=640):
        """Resize frame for processing while maintaining aspect ratio"""
        h, w = frame.shape[:2]
        if w > max_width:
            ratio = max_width / w
            new_w = max_width
            new_h = int(h * ratio)
            return cv2.resize(frame, (new_w, new_h))
        return frame
    
    def should_process_frame(self):
        """Determine if current frame should be processed"""
        # Skip frames based on target FPS
        current_time = time.time()
        if current_time - self.last_process_time < (1.0 / self.target_fps):
            return False
        
        # Frame skipping
        self.frame_count += 1
        if self.frame_count % (self.frame_skip + 1) != 0:
            return False
        
        return True
    
    def process_frame_threaded(self, frame):
        """Process frame in separate thread"""
        if not self.should_process_frame():
            return None
        
        # Add frame to processing queue (non-blocking)
        try:
            self.frame_queue.put_nowait(frame.copy())
        except queue.Full:
            pass  # Skip frame if queue is full
        
        # Get latest result if available
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None
    
    def _processing_worker(self):
        """Worker thread for gesture processing"""
        
        with mp_hands.Hands(
            model_complexity=self.model_complexity,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
            max_num_hands=1
        ) as hands:
            
            while self.running:
                try:
                    # Get frame from queue
                    frame = self.frame_queue.get(timeout=0.1)
                    
                    # Performance optimization
                    start_time = time.time()
                    
                    # Extract ROI and resize
                    roi_frame = self.extract_roi(frame)
                    small_frame = self.resize_frame(roi_frame)
                    
                    # Convert to RGB
                    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                    
                    # Process with MediaPipe
                    results = hands.process(rgb_frame)
                    
                    # Analyze gesture
                    gesture_result = None
                    if results.multi_hand_landmarks:
                        hand_landmarks = results.multi_hand_landmarks[0]
                        gesture_info = self.analyzer.recognize_advanced_gesture(
                            hand_landmarks.landmark
                        )
                        
                        stable_gesture = self.analyzer.get_stable_gesture()
                        
                        gesture_result = {
                            'landmarks': hand_landmarks,
                            'gesture_info': gesture_info,
                            'stable_gesture': stable_gesture,
                            'timestamp': time.time()
                        }
                        
                        # Check for gesture events
                        self._check_gesture_event(stable_gesture)
                    
                    # Calculate processing time
                    process_time = time.time() - start_time
                    fps = 1.0 / process_time if process_time > 0 else 0
                    self.fps_history.append(fps)
                    
                    # Add result to queue
                    result = {
                        'gesture': gesture_result,
                        'processing_time': process_time,
                        'fps': fps,
                        'timestamp': time.time()
                    }
                    
                    try:
                        self.result_queue.put_nowait(result)
                    except queue.Full:
                        # Remove oldest result and add new one
                        try:
                            self.result_queue.get_nowait()
                            self.result_queue.put_nowait(result)
                        except queue.Empty:
                            pass
                    
                    self.last_process_time = time.time()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Processing error: {e}")
                    continue
    
    def _check_gesture_event(self, stable_gesture):
        """Check for gesture events and trigger callbacks"""
        current_time = time.time()
        
        if stable_gesture and stable_gesture != self.current_gesture:
            # New gesture detected
            self.current_gesture = stable_gesture
            self.gesture_start_time = current_time
            
        elif stable_gesture == self.current_gesture and self.current_gesture:
            # Same gesture continued
            gesture_duration = current_time - self.gesture_start_time
            
            if (gesture_duration >= self.gesture_duration_threshold and 
                self.gesture_callback):
                # Trigger gesture event
                self.gesture_callback(stable_gesture, gesture_duration)
                
                # Reset to prevent repeated triggers
                self.current_gesture = None
        
        elif not stable_gesture:
            # No gesture detected
            self.current_gesture = None
    
    def start_processing(self):
        """Start the gesture processing thread"""
        self.running = True
        self.processing_thread = threading.Thread(target=self._processing_worker)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def stop_processing(self):
        """Stop the gesture processing thread"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
    
    def get_average_fps(self):
        """Get average processing FPS"""
        if self.fps_history:
            return sum(self.fps_history) / len(self.fps_history)
        return 0
    

def optimized_gesture_demo():
    """Demo of optimized real-time gesture processing"""
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Configuration for optimal performance
    config = {
        'target_fps': 15,
        'frame_skip': 1,
        'roi_enabled': True,
        'roi_size': 0.6,
        'min_detection_confidence': 0.7,
        'min_tracking_confidence': 0.5,
        'model_complexity': 0  # Fastest model
    }
    
    processor = OptimizedGestureProcessor(config)
    
    # Gesture event handler
    def on_gesture_detected(gesture, duration):
        print(f"GESTURE EVENT: {gesture} (duration: {duration:.2f}s)")
    
    processor.set_gesture_callback(on_gesture_detected)
    processor.start_processing()
    
    print("Optimized Gesture Processing")
    print("Performance optimizations enabled:")
    print(f"- Target FPS: {config['target_fps']}")
    print(f"- ROI enabled: {config['roi_enabled']}")
    print(f"- Model complexity: {config['model_complexity']}")
    print("Press 'q' to quit")
    
    try:
        last_result = None
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            
            # Process frame (threaded)
            result = processor.process_frame_threaded(frame)
            
            if result:
                last_result = result
            
            # Draw results on frame
            if last_result and last_result.get('gesture'):
                gesture_data = last_result['gesture']
                
                if gesture_data['landmarks']:
                    # Draw landmarks
                    mp_drawing.draw_landmarks(
                        frame, 
                        gesture_data['landmarks'], 
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
                        mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                    )
                
                # Display gesture information
                gesture_info = gesture_data['gesture_info']
                stable_gesture = gesture_data['stable_gesture']
                
                cv2.putText(frame, f"Current: {gesture_info['name']}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                
                cv2.putText(frame, f"Confidence: {gesture_info['confidence']:.2f}", 
                           (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                if stable_gesture:
                    cv2.putText(frame, f"Stable: {stable_gesture}", 
                               (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            # Display performance metrics
            if last_result:
                processing_fps = last_result['fps']
                avg_fps = processor.get_average_fps()
                
                cv2.putText(frame, f"Processing FPS: {processing_fps:.1f}", 
                           (frame.shape[1] - 250, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                cv2.putText(frame, f"Average FPS: {avg_fps:.1f}", 
                           (frame.shape[1] - 250, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Display camera FPS
            camera_fps = cap.get(cv2.CAP_PROP_FPS)
            cv2.putText(frame, f"Camera FPS: {camera_fps:.1f}", 
                       (frame.shape[1] - 250, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Draw ROI indicator
            if config['roi_enabled']:
                h, w = frame.shape[:2]
                roi_h = int(h * config['roi_size'])
                roi_w = int(w * config['roi_size'])
                start_y = (h - roi_h) // 2
                start_x = (w - roi_w) // 2
                
                cv2.rectangle(frame, 
                             (start_x, start_y), 
                             (start_x + roi_w, start_y + roi_h), 
                             (0, 255, 255), 2)
                cv2.putText(frame, "ROI", (start_x, start_y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            cv2.imshow('Optimized Gesture Recognition', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        processor.stop_processing()
        cap.release()
        cv2.destroyAllWindows()

# optimized_gesture_demo()

class SmartMirrorGestureController:
    def __init__(self, mirror_app=None):
        self.mirror_app = mirror_app
        self.processor = OptimizedGestureProcessor({
            'target_fps': 12,
            'roi_enabled': True,
            'roi_size': 0.5,
            'min_detection_confidence': 0.75,
            'model_complexity': 0
        })
        
        # Gesture to action mapping
        self.gesture_actions = {
            'POINT_RIGHT': self.navigate_next,
            'POINT_LEFT': self.navigate_previous,
            'OPEN_HAND': self.show_menu,
            'FIST': self.select_current,
            'THUMBS_UP': self.like_current,
            'PEACE': self.settings_mode
        }
        
        # State management
        self.menu_visible = False
        self.settings_mode = False
        self.last_action_time = 0
        self.action_cooldown = 1.0  # 1 second between actions
        
        self.processor.set_gesture_callback(self.handle_gesture)
    
    def start(self):
        """Start gesture recognition"""
        self.processor.start_processing()
        print("Smart Mirror Gesture Controller started")
        print("Available gestures:")
        print("- Point Right: Next widget")
        print("- Point Left: Previous widget")
        print("- Open Hand: Show/hide menu")
        print("- Fist: Select current item")
        print("- Thumbs Up: Like/favorite")
        print("- Peace: Settings mode")
    
    def stop(self):
        """Stop gesture recognition"""
        self.processor.stop_processing()
        print("Smart Mirror Gesture Controller stopped")
    
    def handle_gesture(self, gesture, duration):
        """Handle detected gestures"""
        current_time = time.time()
        
        # Cooldown check
        if current_time - self.last_action_time < self.action_cooldown:
            return
        
        # Execute gesture action
        if gesture in self.gesture_actions:
            print(f"Executing action for gesture: {gesture}")
            self.gesture_actions[gesture]()
            self.last_action_time = current_time
        else:
            print(f"Unknown gesture: {gesture}")
    
    def navigate_next(self):
        """Navigate to next widget"""
        if self.mirror_app:
            self.mirror_app.next_widget()
        print("Action: Navigate Next")
    
    def navigate_previous(self):
        """Navigate to previous widget"""
        if self.mirror_app:
            self.mirror_app.previous_widget()
        print("Action: Navigate Previous")
    
    def show_menu(self):
        """Show/hide menu"""
        self.menu_visible = not self.menu_visible
        if self.mirror_app:
            self.mirror_app.toggle_menu(self.menu_visible)
        print(f"Action: Menu {'visible' if self.menu_visible else 'hidden'}")
    
    def select_current(self):
        """Select current item/widget"""
        if self.mirror_app:
            self.mirror_app.select_current()
        print("Action: Select Current")
    
    def like_current(self):
        """Like/favorite current item"""
        if self.mirror_app:
            self.mirror_app.like_current()
        print("Action: Like Current")
    
    def settings_mode(self):
        """Toggle settings mode"""
        self.settings_mode = not self.settings_mode
        if self.mirror_app:
            self.mirror_app.toggle_settings(self.settings_mode)
        print(f"Action: Settings {'enabled' if self.settings_mode else 'disabled'}")
    
    def get_status(self):
        """Get controller status"""
        return {
            'running': self.processor.running,
            'average_fps': self.processor.get_average_fps(),
            'menu_visible': self.menu_visible,
            'settings_mode': self.settings_mode,
            'last_action_time': self.last_action_time
        }

# Mock Mirror App for testing
class MockMirrorApp:
    def __init__(self):
        self.current_widget = 0
        self.widgets = ['Weather', 'Calendar', 'News', 'Clock']
        self.menu_visible = False
        self.settings_mode = False
    
    def next_widget(self):
        self.current_widget = (self.current_widget + 1) % len(self.widgets)
        print(f"Switched to widget: {self.widgets[self.current_widget]}")
    
    def previous_widget(self):
        self.current_widget = (self.current_widget - 1) % len(self.widgets)
        print(f"Switched to widget: {self.widgets[self.current_widget]}")
    
    def toggle_menu(self, visible):
        self.menu_visible = visible
        print(f"Menu is now {'visible' if visible else 'hidden'}")
    
    def select_current(self):
        print(f"Selected widget: {self.widgets[self.current_widget]}")
    
    def like_current(self):
        print(f"Liked widget: {self.widgets[self.current_widget]}")
    
    def toggle_settings(self, enabled):
        self.settings_mode = enabled
        print(f"Settings mode {'enabled' if enabled else 'disabled'}")

def fixed_smart_mirror_gesture_demo():
    """Fixed version of Smart Mirror gesture control"""
    
    # Create mock mirror app
    mirror_app = MockMirrorApp()
    
    # Setup camera - KEEP CONSISTENT RESOLUTION
    cap = cv2.VideoCapture(0)
    FRAME_WIDTH = 1280
    FRAME_HEIGHT = 720
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    
    # SIMPLIFIED gesture recognizer (no threading for now)
    gesture_recognizer = SimpleGestureRecognizer()
    
    # Simple MediaPipe setup - NO COMPLEX OPTIMIZATION YET
    with mp_hands.Hands(
        static_image_mode=False,
        model_complexity=0,              # Fastest model
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
        max_num_hands=1                 # Single hand
    ) as hands:
        
        print("\nFixed Smart Mirror Gesture Control")
        print("Current widget:", mirror_app.widgets[mirror_app.current_widget])
        print("Try basic gestures:")
        print("- FIST: Close your hand")
        print("- OPEN_HAND: Open all fingers")
        print("- POINTING: Point with index finger")
        print("Press 'q' to quit, 'n' for next widget, 'p' for previous")
        
        # Simple gesture tracking
        gesture_buffer = []
        buffer_size = 5
        last_action_time = 0
        action_cooldown = 2.0  # 2 seconds between actions
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Keep it simple - no ROI, no resizing, no threading
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = hands.process(rgb_frame)
            
            current_gesture = "NO_HAND"
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    
                    # Draw landmarks - THIS SHOULD NOW BE ALIGNED
                    mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
                    # Simple gesture recognition
                    current_gesture = gesture_recognizer.recognize_gesture(hand_landmarks.landmark)
                    
                    # Basic action handling (simplified)
                    current_time = time.time()
                    if current_time - last_action_time > action_cooldown:
                        if current_gesture == "POINTING":
                            mirror_app.next_widget()
                            last_action_time = current_time
                            print(f"Next widget: {mirror_app.widgets[mirror_app.current_widget]}")
                        elif current_gesture == "FIST":
                            print(f"Selected: {mirror_app.widgets[mirror_app.current_widget]}")
                            last_action_time = current_time
            
            # Display current state
            cv2.putText(frame, f"Gesture: {current_gesture}", 
                       (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            cv2.putText(frame, f"Widget: {mirror_app.widgets[mirror_app.current_widget]}", 
                       (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Fixed Smart Mirror Gesture Control', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('n'):  # Manual next for testing
                mirror_app.next_widget()
                print(f"Manual next: {mirror_app.widgets[mirror_app.current_widget]}")
            elif key == ord('p'):  # Manual previous for testing
                mirror_app.previous_widget()
                print(f"Manual previous: {mirror_app.widgets[mirror_app.current_widget]}")
    
    cap.release()
    cv2.destroyAllWindows()

class AdvancedSmartMirrorGestures:
    def __init__(self):
        self.finger_tips = [4, 8, 12, 16, 20]
        
        # Dynamic gesture tracking
        self.hand_positions = deque(maxlen=10)
        self.gesture_start_time = 0
        self.min_gesture_duration = 0.3
        
        # Gesture thresholds
        self.swipe_threshold = 150
        self.tap_threshold = 30
        self.hold_duration = 1.5
        
        # State tracking
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.8
        
    def update_hand_position(self, landmarks, frame_width, frame_height):
        """Track hand movement over time"""
        if landmarks:
            index_tip = landmarks[8]
            x = int(index_tip.x * frame_width)
            y = int(index_tip.y * frame_height)
            
            current_time = time.time()
            self.hand_positions.append({
                'x': x, 'y': y, 'time': current_time
            })
            return (x, y)
        return None
    
    def detect_swipe(self):
        """Detect horizontal and vertical swipes"""
        if len(self.hand_positions) < 5:
            return None
        
        start_pos = self.hand_positions[0]
        end_pos = self.hand_positions[-1]
        
        dx = end_pos['x'] - start_pos['x']
        dy = end_pos['y'] - start_pos['y']
        
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > self.swipe_threshold:
            if abs(dx) > abs(dy):  # Horizontal swipe
                if dx > 0:
                    return "SWIPE_RIGHT"
                else:
                    return "SWIPE_LEFT"
            else:  # Vertical swipe
                if dy > 0:
                    return "SWIPE_DOWN"
                else:
                    return "SWIPE_UP"
        
        return None
    
    def detect_hover(self, current_pos):
        """Detect hovering over the same area"""
        if not current_pos or len(self.hand_positions) < 5:
            return None
        
        recent_positions = list(self.hand_positions)[-5:]
        
        x_positions = [pos['x'] for pos in recent_positions]
        y_positions = [pos['y'] for pos in recent_positions]
        
        x_variance = np.var(x_positions)
        y_variance = np.var(y_positions)
        
        if x_variance < 500 and y_variance < 500:
            hover_duration = recent_positions[-1]['time'] - recent_positions[0]['time']
            if hover_duration > self.hold_duration:
                return "HOVER_SELECT"
        
        return None
    
    def recognize_dynamic_gesture(self, landmarks, frame_width, frame_height):
        """Main function to recognize all dynamic gestures"""
        current_time = time.time()
        
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return None
        
        current_pos = self.update_hand_position(landmarks, frame_width, frame_height)
        
        swipe = self.detect_swipe()
        if swipe:
            self.last_gesture_time = current_time
            self.hand_positions.clear()
            return swipe
        
        hover = self.detect_hover(current_pos)
        if hover:
            self.last_gesture_time = current_time
            self.hand_positions.clear()
            return hover
        
        return None

# fixed_smart_mirror_gesture_demo()
import cv2
import mediapipe as mp
import numpy as np
import math
import time
from collections import deque

class InteractiveSmartMirror:
    def __init__(self):
        self.current_widget = 0
        self.widgets = [
            {'name': 'Weather', 'items': ['Today', 'Tomorrow', 'Weekly', 'Hourly']},
            {'name': 'Calendar', 'items': ['Today\'s Events', 'Upcoming', 'Add Event']},
            {'name': 'News', 'items': ['Headlines', 'Tech', 'Sports', 'Local']},
            {'name': 'Music', 'items': ['Play/Pause', 'Next Track', 'Volume']},
            {'name': 'Smart Home', 'items': ['Lights', 'Temperature', 'Security']}
        ]
        
        self.selected_item = 0
        self.menu_mode = False
        self.brightness = 80
        self.volume = 50
        
        # For visual feedback
        self.last_action = "Ready"
        self.last_action_time = 0
        
    def get_current_widget(self):
        return self.widgets[self.current_widget]
    
    def navigate_widget(self, direction):
        if direction == "next":
            self.current_widget = (self.current_widget + 1) % len(self.widgets)
            self.last_action = f"Switched to {self.get_current_widget()['name']}"
        elif direction == "prev":
            self.current_widget = (self.current_widget - 1) % len(self.widgets)
            self.last_action = f"Switched to {self.get_current_widget()['name']}"
        
        self.selected_item = 0
        self.last_action_time = time.time()
        print(f"📱 Widget: {self.get_current_widget()['name']}")
    
    def navigate_items(self, direction):
        current_items = self.get_current_widget()['items']
        if direction == "down":
            self.selected_item = (self.selected_item + 1) % len(current_items)
            self.last_action = f"Selected: {current_items[self.selected_item]}"
        elif direction == "up":
            self.selected_item = (self.selected_item - 1) % len(current_items)
            self.last_action = f"Selected: {current_items[self.selected_item]}"
        
        self.last_action_time = time.time()
        print(f"🔍 Selected: {current_items[self.selected_item]}")
    
    def select_item(self):
        widget = self.get_current_widget()
        item = widget['items'][self.selected_item]
        self.last_action = f"ACTIVATED: {widget['name']} → {item}"
        self.last_action_time = time.time()
        print(f"✅ ACTIVATED: {widget['name']} → {item}")
        
        # Simulate action feedback
        if widget['name'] == 'Music' and item == 'Play/Pause':
            self.last_action = "🎵 Music toggled!"
            print("🎵 Music toggled!")
        elif widget['name'] == 'Smart Home' and item == 'Lights':
            self.last_action = "💡 Lights toggled!"
            print("💡 Lights toggled!")
        elif widget['name'] == 'Weather':
            self.last_action = f"🌤️ Showing {item} forecast"
            print(f"🌤️ Showing {item} forecast")
    
    def toggle_menu(self):
        self.menu_mode = not self.menu_mode
        self.last_action = f"📋 Menu: {'ON' if self.menu_mode else 'OFF'}"
        self.last_action_time = time.time()
        print(f"📋 Menu: {'ON' if self.menu_mode else 'OFF'}")
    
    def like_action(self):
        self.last_action = "💖 Liked!"
        self.last_action_time = time.time()
        print("💖 Liked!")
    
    def info_action(self):
        self.last_action = "ℹ️ Showing info..."
        self.last_action_time = time.time()
        print("ℹ️ Showing info...")

def draw_enhanced_ui(frame, mirror, current_gesture, dynamic_gesture, w, h):
    """Draw comprehensive UI with gesture feedback"""
    
    # Create semi-transparent overlay
    overlay = frame.copy()
    
    # Main info panel (top)
    cv2.rectangle(overlay, (0, 0), (w, 200), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
    
    # Current widget (large, prominent)
    widget = mirror.get_current_widget()
    cv2.putText(frame, f"📱 {widget['name']}", 
               (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    
    # Widget items
    for i, item in enumerate(widget['items']):
        color = (0, 255, 255) if i == mirror.selected_item else (200, 200, 200)
        prefix = "→" if i == mirror.selected_item else " "
        cv2.putText(frame, f"{prefix} {item}", 
                   (20, 90 + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    # Gesture detection panel (right side)
    gesture_panel_x = w - 400
    cv2.rectangle(overlay, (gesture_panel_x, 0), (w, 250), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
    
    # Current gesture
    gesture_color = (0, 255, 0) if current_gesture != "NO_HAND" else (100, 100, 100)
    cv2.putText(frame, "GESTURE:", 
               (gesture_panel_x + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, current_gesture, 
               (gesture_panel_x + 10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.8, gesture_color, 2)
    
    # Dynamic gesture
    if dynamic_gesture:
        cv2.putText(frame, "DYNAMIC:", 
                   (gesture_panel_x + 10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, dynamic_gesture, 
                   (gesture_panel_x + 10, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
    
    # Last action feedback
    action_age = time.time() - mirror.last_action_time
    if action_age < 3.0:  # Show for 3 seconds
        action_alpha = max(0.3, 1.0 - (action_age / 3.0))
        action_color = tuple(int(c * action_alpha + 100 * (1-action_alpha)) for c in (0, 255, 255))
        
        cv2.putText(frame, "LAST ACTION:", 
                   (gesture_panel_x + 10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, mirror.last_action, 
                   (gesture_panel_x + 10, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.6, action_color, 2)
    
    # Gesture guide (bottom)
    guide_y = h - 150
    cv2.rectangle(overlay, (0, guide_y), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    cv2.putText(frame, "GESTURE CONTROLS:", 
               (20, guide_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    controls = [
        "👊 FIST=Select  ✌️ PEACE=Menu  👍 THUMBS=Like  ☝️ POINT=Info",
        "⬅️ SWIPE LEFT=Prev Widget  ➡️ SWIPE RIGHT=Next Widget",
        "⬆️ SWIPE UP=Menu Up  ⬇️ SWIPE DOWN=Menu Down"
    ]
    
    for i, control in enumerate(controls):
        cv2.putText(frame, control, 
                   (20, guide_y + 55 + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    # Menu mode indicator
    if mirror.menu_mode:
        cv2.putText(frame, "🟢 MENU MODE", 
                   (w - 200, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

def visual_feedback_smart_mirror():
    """Smart Mirror with comprehensive visual feedback"""
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Initialize gesture recognizers
    static_recognizer = SimpleGestureRecognizer()
    dynamic_recognizer = AdvancedSmartMirrorGestures()
    
    # Initialize smart mirror
    mirror = InteractiveSmartMirror()
    
    with mp_hands.Hands(
        static_image_mode=False,
        model_complexity=0,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
        max_num_hands=1
    ) as hands:
        
        print("🪞 Visual Feedback Smart Mirror Started!")
        print("All gesture feedback now appears on screen!")
        
        current_gesture = "NO_HAND"
        dynamic_gesture = None
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            # Reset gestures
            current_gesture = "NO_HAND"
            dynamic_gesture = None
            
            # Process gestures
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                
                # Draw hand landmarks
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Recognize static gestures
                current_gesture = static_recognizer.recognize_gesture(hand_landmarks.landmark)
                
                # Recognize dynamic gestures
                dynamic_gesture = dynamic_recognizer.recognize_dynamic_gesture(
                    hand_landmarks.landmark, w, h
                )
                
                # Handle gestures with visual feedback
                if dynamic_gesture:
                    if dynamic_gesture == "SWIPE_LEFT":
                        mirror.navigate_widget("prev")
                    elif dynamic_gesture == "SWIPE_RIGHT":
                        mirror.navigate_widget("next")
                    elif dynamic_gesture == "SWIPE_UP":
                        mirror.navigate_items("up")
                    elif dynamic_gesture == "SWIPE_DOWN":
                        mirror.navigate_items("down")
                    elif dynamic_gesture == "HOVER_SELECT":
                        mirror.info_action()
                
                elif current_gesture:
                    if current_gesture == "FIST":
                        mirror.select_item()
                    elif current_gesture == "PEACE":
                        mirror.toggle_menu()
                    elif current_gesture == "THUMBS_UP":
                        mirror.like_action()
                    elif current_gesture == "POINTING":
                        mirror.info_action()
            
            # Draw comprehensive UI with gesture feedback
            draw_enhanced_ui(frame, mirror, current_gesture, dynamic_gesture, w, h)
            
            cv2.imshow('Smart Mirror - Visual Feedback', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    visual_feedback_smart_mirror()

