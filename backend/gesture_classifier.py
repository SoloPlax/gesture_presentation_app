"""
Gesture Classifier Module
Interprets hand landmarks into presentation control commands
Improved with debouncing and filtering to prevent false positives:
- Hold Duration: Gesture must be stable for 0.4s before triggering
- Transition Guard: Requires neutral state between different gestures
- Stricter Thumbs-Up: More precise detection with orientation checks
"""
import numpy as np
from collections import deque
import time
import math


class GestureClassifier:
    """Classifies hand gestures into presentation commands with advanced filtering."""
    
    def __init__(self):
        """Initialize gesture classifier with tracking variables."""
        self.previous_positions = deque(maxlen=10)
        self.last_command_time = 0
        self.command_cooldown = 1.0  # Seconds between commands
        self.gesture_threshold = 0.15
        self.zoom_threshold = 0.1
        
        # Gesture stability tracking (Hold Duration) - Reduced for faster response
        self.current_gesture = None
        self.gesture_start_time = None
        self.gesture_hold_duration = 0.2  # Seconds to hold before triggering (reduced from 0.4)
        self.gesture_frame_buffer = deque(maxlen=15)  # Track recent gesture detections
        
        # Transition guard
        self.last_confirmed_gesture = None
        self.neutral_frame_count = 0
        self.required_neutral_frames = 2  # Frames of "no gesture" required between commands (reduced from 3)
        
    def classify_gesture(self, landmarks_list):
        """
        Classify detected hand landmarks with stability filtering.
        
        Args:
            landmarks_list: List of hand landmarks from webcam_reader
            
        Returns:
            str or None: Command string after stability checks
        """
        if not landmarks_list:
            # No hands detected - increment neutral counter
            self.neutral_frame_count += 1
            self.gesture_frame_buffer.append(None)
            self.current_gesture = None
            self.gesture_start_time = None
            return None
        
        current_time = time.time()
        
        # Detect what gesture is currently being shown (raw detection)
        detected_gesture = self._detect_current_gesture(landmarks_list)
        
        # Add to frame buffer for stability analysis
        self.gesture_frame_buffer.append(detected_gesture)
        
        # Check if this is a new gesture
        if detected_gesture != self.current_gesture:
            self.current_gesture = detected_gesture
            self.gesture_start_time = current_time
            return None  # Don't trigger yet, wait for stability
        
        # Gesture is same as before - check hold duration
        if detected_gesture and self.gesture_start_time:
            hold_time = current_time - self.gesture_start_time
            
            # Check if gesture has been held long enough
            if hold_time >= self.gesture_hold_duration:
                # Verify gesture stability in frame buffer
                if self._is_gesture_stable(detected_gesture):
                    # Check transition guard: need neutral frames between different gestures
                    if self.last_confirmed_gesture and detected_gesture != self.last_confirmed_gesture:
                        if self.neutral_frame_count < self.required_neutral_frames:
                            return None  # Not enough neutral frames yet
                    
                    # Check cooldown
                    if current_time - self.last_command_time < self.command_cooldown:
                        return None
                    
                    # All checks passed - trigger command
                    self.last_command_time = current_time
                    self.last_confirmed_gesture = detected_gesture
                    self.neutral_frame_count = 0  # Reset neutral counter
                    self.gesture_start_time = None  # Reset for next detection
                    return detected_gesture
        
        # If no gesture detected, increment neutral frame count
        if not detected_gesture:
            self.neutral_frame_count += 1
        else:
            self.neutral_frame_count = 0
        
        return None
    
    def _is_gesture_stable(self, gesture):
        """Check if gesture has been consistently detected in recent frames."""
        if len(self.gesture_frame_buffer) < 6:
            return False
        
        # Count how many recent frames show this gesture
        recent_frames = list(self.gesture_frame_buffer)[-6:]
        gesture_count = sum(1 for g in recent_frames if g == gesture)
        
        # Require 67% consistency (4 out of 6 frames) - reduced for faster response
        return gesture_count >= 4
    
    def _detect_current_gesture(self, landmarks_list):
        """Detect the current gesture without stability checks."""
        num_hands = len(landmarks_list)
        
        # Two-hand gestures (check first as they're more specific)
        if num_hands == 2:
            if self._detect_frame_gesture(landmarks_list):
                return "zoom_in"
            
            if self._detect_zoom_out_gesture(landmarks_list):
                return "zoom_out"
        
        # Single hand gestures
        if num_hands == 1:
            landmarks = landmarks_list[0]
            
            # Check in order of specificity (most specific first)
            # Two fingers pointing is more specific than thumbs up
            if self._detect_two_fingers_right(landmarks):
                return "next"
            
            if self._detect_one_finger_left(landmarks):
                return "prev"
            
            # Thumbs up with stricter detection (checked later)
            if self._detect_thumbs_up_strict(landmarks):
                return "start"
            
            # Open palm last (least specific)
            if self._detect_open_palm(landmarks):
                return "pause"
        
        return None
    
    def _detect_thumbs_up_strict(self, landmarks):
        """
        Detect thumbs up with stricter criteria to prevent false positives.
        Requires thumb to be vertical and properly oriented.
        """
        # Thumb should be extended upward (tip above base)
        thumb_tip_y = landmarks[4]['y']
        thumb_base_y = landmarks[2]['y']
        thumb_extended = thumb_tip_y < thumb_base_y
        
        # Check thumb is roughly vertical (not angled too much)
        thumb_tip_x = landmarks[4]['x']
        thumb_base_x = landmarks[2]['x']
        thumb_horizontal_distance = abs(thumb_tip_x - thumb_base_x)
        thumb_vertical_distance = abs(thumb_tip_y - thumb_base_y)
        
        # Thumb should be more vertical than horizontal (angle check)
        # Allow some angle tolerance but require mostly vertical
        is_vertical = thumb_vertical_distance > thumb_horizontal_distance * 0.8
        
        # Thumb must be significantly higher than palm center
        palm_center_y = landmarks[0]['y']
        thumb_significantly_higher = thumb_tip_y < palm_center_y - 0.15
        
        # Other fingers should be curled (tips below middle joints)
        index_curled = landmarks[8]['y'] > landmarks[6]['y']
        middle_curled = landmarks[12]['y'] > landmarks[10]['y']
        ring_curled = landmarks[16]['y'] > landmarks[14]['y']
        pinky_curled = landmarks[20]['y'] > landmarks[18]['y']
        
        # All 4 fingers must be curled
        curled_count = sum([index_curled, middle_curled, ring_curled, pinky_curled])
        all_fingers_curled = curled_count == 4
        
        return (thumb_extended and is_vertical and thumb_significantly_higher and 
                all_fingers_curled)
    
    def _detect_open_palm(self, landmarks):
        """Detect open palm (all fingers extended)."""
        thumb_extended = landmarks[4]['y'] < landmarks[3]['y']
        index_extended = landmarks[8]['y'] < landmarks[6]['y']
        middle_extended = landmarks[12]['y'] < landmarks[10]['y']
        ring_extended = landmarks[16]['y'] < landmarks[14]['y']
        pinky_extended = landmarks[20]['y'] < landmarks[18]['y']
        
        return (thumb_extended and index_extended and middle_extended and 
                ring_extended and pinky_extended)
    
    def _detect_two_fingers_right(self, landmarks):
        """Detect index and middle fingers pointing to the right."""
        index_extended = landmarks[8]['y'] < landmarks[6]['y']
        middle_extended = landmarks[12]['y'] < landmarks[10]['y']
        ring_curled = landmarks[16]['y'] > landmarks[14]['y']
        pinky_curled = landmarks[20]['y'] > landmarks[18]['y']
        
        # Check pointing direction
        wrist_x = landmarks[0]['x']
        index_tip_x = landmarks[8]['x']
        middle_tip_x = landmarks[12]['x']
        
        pointing_right = (index_tip_x > wrist_x + 0.1 and 
                         middle_tip_x > wrist_x + 0.1)
        
        return (index_extended and middle_extended and 
                ring_curled and pinky_curled and pointing_right)
    
    def _detect_one_finger_left(self, landmarks):
        """Detect single index finger pointing to the left."""
        index_extended = landmarks[8]['y'] < landmarks[6]['y']
        middle_curled = landmarks[12]['y'] > landmarks[10]['y']
        ring_curled = landmarks[16]['y'] > landmarks[14]['y']
        pinky_curled = landmarks[20]['y'] > landmarks[18]['y']
        thumb_curled = landmarks[4]['x'] < landmarks[3]['x'] + 0.05
        
        wrist_x = landmarks[0]['x']
        index_tip_x = landmarks[8]['x']
        pointing_left = index_tip_x < wrist_x - 0.1
        
        return (index_extended and middle_curled and ring_curled and 
                pinky_curled and pointing_left)
    
    def _detect_frame_gesture(self, landmarks_list):
        """Detect two hands making a frame gesture."""
        if len(landmarks_list) != 2:
            return False
        
        def is_frame_hand(landmarks):
            thumb_extended = abs(landmarks[4]['x'] - landmarks[2]['x']) > 0.05
            index_extended = landmarks[8]['y'] < landmarks[6]['y']
            middle_curled = landmarks[12]['y'] > landmarks[10]['y']
            ring_curled = landmarks[16]['y'] > landmarks[14]['y']
            pinky_curled = landmarks[20]['y'] > landmarks[18]['y']
            
            return (thumb_extended and index_extended and 
                   middle_curled and ring_curled and pinky_curled)
        
        return is_frame_hand(landmarks_list[0]) and is_frame_hand(landmarks_list[1])
    
    def _detect_zoom_out_gesture(self, landmarks_list):
        """Detect two hands with 3 fingers moving together."""
        if len(landmarks_list) != 2:
            return False
        
        def is_three_finger_hand(landmarks):
            thumb_extended = abs(landmarks[4]['x'] - landmarks[2]['x']) > 0.04
            index_extended = landmarks[8]['y'] < landmarks[6]['y']
            middle_extended = landmarks[12]['y'] < landmarks[10]['y']
            ring_curled = landmarks[16]['y'] > landmarks[14]['y']
            pinky_curled = landmarks[20]['y'] > landmarks[18]['y']
            
            return (thumb_extended and index_extended and middle_extended and
                   ring_curled and pinky_curled)
        
        if not (is_three_finger_hand(landmarks_list[0]) and 
                is_three_finger_hand(landmarks_list[1])):
            return False
        
        # Track hand distance
        hand1_wrist = np.array([landmarks_list[0][0]['x'], landmarks_list[0][0]['y']])
        hand2_wrist = np.array([landmarks_list[1][0]['x'], landmarks_list[1][0]['y']])
        current_distance = np.linalg.norm(hand1_wrist - hand2_wrist)
        
        self.previous_positions.append(current_distance)
        
        if len(self.previous_positions) < 5:
            return False
        
        start_distance = self.previous_positions[0]
        end_distance = self.previous_positions[-1]
        moving_together = (start_distance - end_distance) > self.zoom_threshold
        
        if moving_together:
            self.previous_positions.clear()
            return True
        
        return False
    
    def get_gesture_info(self, command):
        """Get human-readable information about a gesture command."""
        gesture_info = {
            'next': 'Next Slide (Two Fingers Pointing Right)',
            'prev': 'Previous Slide (One Finger Pointing Left)',
            'start': 'Start Presentation (Thumbs Up)',
            'pause': 'Pause/Hold (Open Palm)',
            'zoom_in': 'Zoom In (Two Hands Frame Gesture)',
            'zoom_out': 'Zoom Out (Two Hands 3 Fingers Moving Together)'
        }
        
        return gesture_info.get(command, 'Unknown Command')
