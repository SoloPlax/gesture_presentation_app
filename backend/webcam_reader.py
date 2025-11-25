"""
Webcam Reader Module
Handles webcam capture and frame processing with MediaPipe Hands
"""
import cv2
import mediapipe as mp
import numpy as np


class WebcamReader:
    """Manages webcam capture and hand landmark detection."""
    
    def __init__(self, camera_index=0):
        """
        Initialize webcam and MediaPipe Hands.
        
        Args:
            camera_index: Index of the camera to use (default: 0 for primary webcam)
        """
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        self.is_running = True
        
    def read_frame(self):
        """
        Capture a single frame from the webcam.
        
        Returns:
            tuple: (success, frame, landmarks_list)
                - success: boolean indicating if frame was captured
                - frame: the captured frame
                - landmarks_list: list of detected hand landmarks
        """
        success, frame = self.cap.read()
        
        if not success:
            return False, None, None
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with MediaPipe
        results = self.hands.process(rgb_frame)
        
        landmarks_list = []
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks on frame
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Convert landmarks to list format
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z
                    })
                landmarks_list.append(landmarks)
        
        return True, frame, landmarks_list
    
    def get_hand_info(self, results):
        """
        Extract hand information from MediaPipe results.
        
        Args:
            results: MediaPipe hand detection results
            
        Returns:
            list: List of hand information dictionaries
        """
        hands_info = []
        
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_info = {
                    'label': handedness.classification[0].label,  # 'Left' or 'Right'
                    'score': handedness.classification[0].score,
                    'landmarks': []
                }
                
                for landmark in hand_landmarks.landmark:
                    hand_info['landmarks'].append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z
                    })
                
                hands_info.append(hand_info)
        
        return hands_info
    
    def display_frame(self, frame, window_name="Gesture Control - Press 'q' to quit"):
        """
        Display the frame in a window.
        
        Args:
            frame: The frame to display
            window_name: Name of the display window
        """
        cv2.imshow(window_name, frame)
        
        # Check for 'q' key press to quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            self.is_running = False
    
    def release(self):
        """Release webcam and close all windows."""
        self.cap.release()
        cv2.destroyAllWindows()
        self.hands.close()
