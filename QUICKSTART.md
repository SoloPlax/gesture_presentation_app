# 🚀 Quick Start Guide

## Gesture-Controlled Presentation App

### Step 1: Install Python Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Start the Backend Server

```bash
# From the backend directory
python run_server.py
```

You should see:
```
============================================================
GESTURE-CONTROLLED PRESENTATION SERVER
============================================================

🚀 WebSocket server starting on ws://localhost:8765
✓ WebSocket server running on ws://localhost:8765
💡 Open frontend/index.html in your browser to connect
📹 Starting webcam and gesture detection...
```

### Step 3: Open the Frontend

**Option A: Direct File Access**
- Navigate to `frontend/index.html`
- Open it in your browser (double-click or right-click → Open With → Browser)

**Option B: Local Server (Recommended)**
```bash
# From the frontend directory
python -m http.server 8000
```
Then visit: `http://localhost:8000`

### Step 4: Test Your Gestures! 👋

Once both are running:
1. Allow webcam access when prompted
2. Position yourself in front of the camera
3. Try these improved gestures:
   - **Thumbs Up 👍** → Start presentation
   - **Open Palm ✋** → Pause/Hold
   - **Two Fingers Pointing Right →** → Next slide
   - **One Finger Pointing Left ←** → Previous slide (Go Back)
   - **Two Hands Frame (👌+👌)** → Zoom In
   - **Two Hands 3 Fingers Moving Together** → Zoom Out

### Keyboard Backup Controls

- `Arrow Right/Left` - Navigate slides
- `+/-` - Zoom in/out
- `F` - Toggle fullscreen
- `Home/End` - First/last slide
- `Esc` - Exit fullscreen

### Troubleshooting

**Webcam not detected?**
- Check camera permissions in your browser
- Ensure no other app is using the webcam

**WebSocket connection failed?**
- Verify the backend server is running
- Check the console for error messages
- Ensure port 8765 is not blocked

**Gestures not responding?**
- Ensure good lighting
- Position hand 1-2 feet from camera
- Move gestures slowly and deliberately
- Check terminal for detection messages

### Customizing Your Presentation

**Add More Slides:**
1. Create `slideX.html` in `frontend/slides/`
2. Update `app.js` slideFiles array
3. Follow the same HTML structure

**Adjust Gesture Sensitivity:**
Edit `backend/gesture_classifier.py`:
- `command_cooldown` - Time between commands
- `gesture_threshold` - Swipe distance needed

**Change Styling:**
Edit `frontend/styles.css` to customize appearance

---

**Enjoy your gesture-controlled presentation! 🎉**
