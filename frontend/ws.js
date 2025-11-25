/**
 * WebSocket Client Module
 * Handles connection to Python backend and receives gesture commands
 */

class WebSocketClient {
    constructor(url = 'ws://localhost:8765') {
        this.url = url;
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000; // 2 seconds
        this.onCommandCallback = null;
        this.onStatusCallback = null;
    }

    /**
     * Connect to the WebSocket server
     */
    connect() {
        console.log(`Connecting to ${this.url}...`);
        this.updateStatus('connecting', 'Connecting to gesture server...');

        try {
            this.socket = new WebSocket(this.url);

            this.socket.onopen = () => {
                console.log('✓ WebSocket connected');
                this.reconnectAttempts = 0;
                this.updateStatus('connected', 'Connected to gesture server');
            };

            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('Received command:', data);
                    
                    if (data.command && this.onCommandCallback) {
                        this.onCommandCallback(data.command);
                    }
                } catch (error) {
                    console.error('Error parsing message:', error);
                }
            };

            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateStatus('error', 'Connection error');
            };

            this.socket.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateStatus('disconnected', 'Disconnected from gesture server');
                this.attemptReconnect();
            };

        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.updateStatus('error', 'Failed to connect');
            this.attemptReconnect();
        }
    }

    /**
     * Attempt to reconnect to the server
     */
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${this.reconnectDelay/1000}s...`);
            this.updateStatus('reconnecting', `Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
        } else {
            console.log('Max reconnect attempts reached');
            this.updateStatus('failed', 'Connection failed. Please restart the backend server.');
        }
    }

    /**
     * Register callback for when commands are received
     * @param {Function} callback - Function to call with command string
     */
    onCommand(callback) {
        this.onCommandCallback = callback;
    }

    /**
     * Register callback for connection status updates
     * @param {Function} callback - Function to call with status info
     */
    onStatus(callback) {
        this.onStatusCallback = callback;
    }

    /**
     * Update connection status
     * @param {string} status - Status type (connecting, connected, disconnected, error, etc.)
     * @param {string} message - Status message
     */
    updateStatus(status, message) {
        if (this.onStatusCallback) {
            this.onStatusCallback({ status, message });
        }
    }

    /**
     * Send a message to the server
     * @param {Object} data - Data to send
     */
    send(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket is not connected');
        }
    }

    /**
     * Close the WebSocket connection
     */
    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }
}

// Export for use in app.js
window.WebSocketClient = WebSocketClient;
