"""
Main Server Entry Point
Runs webcam gesture detection and WebSocket server for real-time presentation control
"""
import asyncio
import websockets
import json
import threading
from webcam_reader import WebcamReader
from gesture_classifier import GestureClassifier


class GestureServer:
    """Main server orchestrating gesture detection and WebSocket communication."""
    
    def __init__(self, host="localhost", port=8765):
        """
        Initialize the gesture server.
        
        Args:
            host: WebSocket server host (default: localhost)
            port: WebSocket server port (default: 8765)
        """
        self.host = host
        self.port = port
        self.webcam = WebcamReader()
        self.classifier = GestureClassifier()
        self.connected_clients = set()
        self.running = True
        
    async def handle_client(self, websocket):
        """
        Handle a new WebSocket client connection.
        
        Args:
            websocket: The WebSocket connection
        """
        self.connected_clients.add(websocket)
        print(f"✓ Client connected. Total clients: {len(self.connected_clients)}")
        
        try:
            # Keep connection alive
            async for message in websocket:
                # Echo back or handle client messages if needed
                print(f"Received from client: {message}")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected_clients.remove(websocket)
            print(f"✗ Client disconnected. Total clients: {len(self.connected_clients)}")
    
    async def broadcast_command(self, command):
        """
        Broadcast a command to all connected WebSocket clients.
        
        Args:
            command: The command string to broadcast
        """
        if not self.connected_clients:
            return
        
        message = json.dumps({"command": command})
        
        # Send to all connected clients
        disconnected = set()
        for client in self.connected_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
        
        # Remove disconnected clients
        self.connected_clients -= disconnected
    
    async def websocket_server(self):
        """Start the WebSocket server."""
        print(f"🚀 WebSocket server starting on ws://{self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"✓ WebSocket server running on ws://{self.host}:{self.port}")
            print("💡 Open frontend/index.html in your browser to connect")
            await asyncio.Future()  # Run forever
    
    async def gesture_detection_loop(self):
        """Main loop for gesture detection and command broadcasting."""
        print("📹 Starting webcam and gesture detection...")
        print("👋 Improved Gesture Controls:")
        print("   - Thumbs Up 👍 → Start Presentation")
        print("   - Open Palm ✋ → Pause/Hold")
        print("   - Two Fingers Pointing Right → → Next Slide")
        print("   - One Finger Pointing Left ← → Previous Slide (Go Back)")
        print("   - Two Hands Frame (👌+👌) → Zoom In")
        print("   - Two Hands 3 Fingers Moving Together → Zoom Out")
        print("   - Press 'q' to quit\n")
        
        while self.webcam.is_running and self.running:
            # Read frame from webcam
            success, frame, landmarks_list = self.webcam.read_frame()
            
            if not success:
                print("⚠ Failed to read from webcam")
                break
            
            # Classify gesture
            command = self.classifier.classify_gesture(landmarks_list)
            
            if command:
                gesture_info = self.classifier.get_gesture_info(command)
                print(f"✓ Detected: {gesture_info}")
                
                # Broadcast to all connected clients
                await self.broadcast_command(command)
            
            # Display frame with hand landmarks
            self.webcam.display_frame(frame)
            
            # Small delay to prevent CPU overload
            await asyncio.sleep(0.01)
        
        print("\n🛑 Shutting down gesture detection...")
        self.webcam.release()
    
    async def run(self):
        """Run both WebSocket server and gesture detection concurrently."""
        print("=" * 60)
        print("GESTURE-CONTROLLED PRESENTATION SERVER")
        print("=" * 60)
        print()
        
        try:
            # Run both tasks concurrently
            await asyncio.gather(
                self.websocket_server(),
                self.gesture_detection_loop()
            )
        except KeyboardInterrupt:
            print("\n\n⚠ Interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
        finally:
            self.running = False
            self.webcam.release()
            print("\n✓ Server stopped")


def main():
    """Main entry point."""
    server = GestureServer(host="localhost", port=8765)
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\n\n✓ Gracefully shutting down...")


if __name__ == "__main__":
    main()
