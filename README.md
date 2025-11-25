# Gesture-Controlled Presentation App
Fully self-contained HTML + Python mediapipe gesture controller.
TODO: Add documentation.
# Gesture-Controlled HTML Presentation App
### A Fully Self-Contained, Offline, AI-Driven Presentation System

This project implements a **gesture-controlled presentation engine** that uses the **laptop's webcam**, **Python**, **MediaPipe**, **OpenCV**, and **WebSockets** to navigate through a fully animated **HTML/JavaScript slideshow**.

The system is designed to run **entirely offline** and **locally on a laptop**, making it ideal for conferences, classrooms, or environments where internet connectivity is unreliable.

It replaces tools like PowerPoint with a completely customizable, animated, browser-based presentation — controlled using nothing but hand gestures.

---

# 🔥 Key Features

### ✔ Fully Offline  
No dependency on online services — everything runs on your laptop.

### ✔ AI-Based Gesture Recognition  
Uses:
- **MediaPipe Hands** (local landmark detection)
- **OpenCV** (webcam feed)
- **Custom Gesture Classifier** (Python)

### ✔ Real-Time Slide Control via Gestures  
You can control the presentation with:
- **Thumbs Up 👍** → Start presentation  
- **Open Palm ✋** → Pause/Hold  
- **Two Fingers Pointing Right →** → Next slide  
- **One Finger Pointing Left ←** → Previous slide (Go Back)  
- **Two Hands Frame Gesture (👌+👌)** → Zoom In  
- **Two Hands 3 Fingers Moving Together** → Zoom Out  

(These gestures are customizable and adjustable in `gesture_classifier.py`.)

### ✔ Modern Animated HTML Presentation  
The browser loads:
- `index.html`  
- Dynamic slide templates from `/slides/`  
- JavaScript slide engine with smooth transitions  
- WebSocket listener for incoming commands  

### ✔ Fully Modular  
The backend and frontend are decoupled:
- Python → Gesture Engine & WebSocket Server  
- HTML/JS → Slide Rendering & Animation  

This makes future upgrades easy.

---

# 🧠 System Architecture

      ┌──────────────────────────────┐
      │     Laptop Webcam (Local)    │
      └──────────────┬───────────────┘
                     │
                     ▼
          ┌────────────────────┐
          │ Python Backend     │
          │ - OpenCV           │
          │ - MediaPipe        │
          │ - Gesture Classifier
          │ - WebSocket Server │
          └──────────┬─────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Browser Frontend     │
          │ - index.html         │
          │ - app.js             │
          │ - ws.js              │
          │ - Animated Slides    │
          └──────────────────────┘

---

# 📁 Project Folder Structure

gesture_presentation_app/
│
├── backend/
│ ├── run_server.py # Main entry point (webcam + websocket)
│ ├── gesture_classifier.py # Contains gesture interpretation logic
│ ├── webcam_reader.py # Handles webcam capture and frame processing
│ ├── requirements.txt # Python dependencies
│
├── frontend/
│ ├── index.html # Loads the slide container and scripts
│ ├── styles.css # Core presentation styling
│ ├── app.js # Slide engine logic and transitions
│ ├── ws.js # WebSocket client listening for commands
│ ├── slides/
│ │ ├── slide1.html # Individual slide templates
│ │ ├── slide2.html
│ │ └── slide3.html
│
└── README.md # Documentation (this file)


---

# ⚙️ Installation & Setup

### 1. Create a Python environment

```bash
cd gesture_presentation_app/backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

2. Launch the backend (gesture engine + WebSocket server)
python run_server.py


This will:

Start the webcam

Detect gestures

Open a WebSocket server on ws://localhost:8765

3. Open the frontend (presentation)

Open in your browser:

file:///path/to/gesture_presentation_app/frontend/index.html


Or serve it locally using Python:

python -m http.server 8000


Then visit:

http://localhost:8000

🧭 Gestures & Commands (Improved Controls)
Gesture Detected	Command Sent	Presentation Action
Thumbs Up 👍	"start"	Start presentation
Open Palm ✋	"pause"	Pause / Hold
Two Fingers Pointing Right →	"next"	Next slide
One Finger Pointing Left ←	"prev"	Previous slide (Go Back)
Two Hands Frame (👌+👌)	"zoom_in"	Zoom In
Two Hands 3 Fingers Moving Together	"zoom_out"	Zoom Out

These gestures are fully customizable and can be modified inside `gesture_classifier.py`.

🧩 How Communication Works
Python → Browser

The Python backend sends structured JSON:

{"command": "next"}

Browser → Slide Engine

The frontend listens in ws.js:

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.command === "next") nextSlide();
};


Everything is real-time and local.

💡 Customizing Your Presentation

Modify or add slides inside:

frontend/slides/


Each file (e.g., slide1.html) contains:

<div class="slide">
   <h1>My Title</h1>
   <p>Slide content here.</p>
</div>


The app.js file dynamically loads and animates slides.

You can include:

Images

Charts

CSS animations

GSAP transitions

Videos

Interactive elements

🛠 Recommended Enhancements (Future Versions)
1. Gesture Calibration Screen

Allow tuning sensitivity for different lighting.

2. Visual Debug Overlay

Show hand landmarks and detected gestures.

3. More Gestures

Rotate hand → rotate object on screen

Pinch gesture → scroll vertically

Two-finger drag → pan slide

4. Multi-Presenter Mode

Multiple gesture engines connected to the same presentation.

5. Voice Commands Integration

“Next slide”, “Zoom in”, etc.

📜 License

MIT License — free for personal and commercial use.

👨‍💻 Author

Solomon Smit
Founder & CEO — ALPHA TOWER Solutions (Pty) Ltd.
Innovator in AI-driven EdTech, engineering systems, and digital transformation.

🎤 Final Notes

This system is purpose-built for:

High-profile presentations

Academic conferences

Product demos

Educational workshops

Hands-free teaching environments

It provides a modern, cinematic, AI-powered alternative to PowerPoint — running entirely offline.
