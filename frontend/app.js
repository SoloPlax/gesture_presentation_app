/**
 * Presentation Engine Module
 * Handles slide loading, transitions, and gesture command execution
 */

class PresentationEngine {
    constructor() {
        this.slides = [];
        this.currentSlideIndex = 0;
        this.isPresenting = false;
        this.zoomLevel = 1;
        this.slideContainer = null;
        this.wsClient = null;
    }

    /**
     * Initialize the presentation engine
     */
    async init() {
        console.log('Initializing Presentation Engine...');
        
        // Get DOM elements
        this.slideContainer = document.getElementById('slide-container');
        this.statusIndicator = document.getElementById('status');
        this.slideCounter = document.getElementById('slide-counter');
        
        // Load slides
        await this.loadSlides();
        
        // Initialize WebSocket
        this.initWebSocket();
        
        // Setup keyboard controls (backup)
        this.setupKeyboardControls();
        
        // Show first slide
        this.showSlide(0);
        
        console.log('✓ Presentation Engine initialized');
    }

    /**
     * Load all slides from the slides directory
     */
    async loadSlides() {
        const slideFiles = ['slide1.html', 'slide2.html', 'slide3.html'];
        
        for (const file of slideFiles) {
            try {
                const response = await fetch(`slides/${file}`);
                const html = await response.text();
                this.slides.push(html);
            } catch (error) {
                console.error(`Failed to load ${file}:`, error);
            }
        }
        
        console.log(`✓ Loaded ${this.slides.length} slides`);
        this.updateSlideCounter();
    }

    /**
     * Initialize WebSocket connection
     */
    initWebSocket() {
        this.wsClient = new WebSocketClient('ws://localhost:8765');
        
        // Handle gesture commands
        this.wsClient.onCommand((command) => {
            console.log(`Executing command: ${command}`);
            this.handleCommand(command);
        });
        
        // Handle connection status
        this.wsClient.onStatus((status) => {
            this.updateStatus(status.status, status.message);
        });
        
        // Connect
        this.wsClient.connect();
    }

    /**
     * Handle incoming gesture commands
     * @param {string} command - The command to execute
     */
    handleCommand(command) {
        switch(command) {
            case 'next':
                this.nextSlide();
                break;
            case 'prev':
                this.prevSlide();
                break;
            case 'zoom_in':
                this.zoomIn();
                break;
            case 'zoom_out':
                this.zoomOut();
                break;
            case 'start':
                this.startPresentation();
                break;
            case 'pause':
                this.pausePresentation();
                break;
            default:
                console.warn(`Unknown command: ${command}`);
        }
    }

    /**
     * Show a specific slide
     * @param {number} index - Slide index
     */
    showSlide(index) {
        if (index < 0 || index >= this.slides.length) {
            console.warn('Invalid slide index:', index);
            return;
        }

        this.currentSlideIndex = index;
        
        // Add fade-out animation
        this.slideContainer.style.opacity = '0';
        
        setTimeout(() => {
            // Update slide content
            this.slideContainer.innerHTML = this.slides[index];
            
            // Apply zoom
            this.slideContainer.style.transform = `scale(${this.zoomLevel})`;
            
            // Fade in
            this.slideContainer.style.opacity = '1';
            
            // Update counter
            this.updateSlideCounter();
            
            console.log(`Showing slide ${index + 1}/${this.slides.length}`);
        }, 300);
    }

    /**
     * Go to next slide
     */
    nextSlide() {
        if (this.currentSlideIndex < this.slides.length - 1) {
            this.showSlide(this.currentSlideIndex + 1);
            this.showNotification('Next Slide →');
        } else {
            console.log('Already at last slide');
            this.showNotification('Last Slide');
        }
    }

    /**
     * Go to previous slide
     */
    prevSlide() {
        if (this.currentSlideIndex > 0) {
            this.showSlide(this.currentSlideIndex - 1);
            this.showNotification('← Previous Slide');
        } else {
            console.log('Already at first slide');
            this.showNotification('First Slide');
        }
    }

    /**
     * Zoom in
     */
    zoomIn() {
        if (this.zoomLevel < 2) {
            this.zoomLevel += 0.1;
            this.slideContainer.style.transform = `scale(${this.zoomLevel})`;
            this.showNotification(`Zoom: ${Math.round(this.zoomLevel * 100)}%`);
            console.log(`Zoom level: ${this.zoomLevel.toFixed(2)}`);
        }
    }

    /**
     * Zoom out
     */
    zoomOut() {
        if (this.zoomLevel > 0.5) {
            this.zoomLevel -= 0.1;
            this.slideContainer.style.transform = `scale(${this.zoomLevel})`;
            this.showNotification(`Zoom: ${Math.round(this.zoomLevel * 100)}%`);
            console.log(`Zoom level: ${this.zoomLevel.toFixed(2)}`);
        }
    }

    /**
     * Start presentation mode
     */
    startPresentation() {
        if (!this.isPresenting) {
            this.isPresenting = true;
            document.body.classList.add('presenting');
            this.showSlide(0);
            this.showNotification('Presentation Started 🎬');
            console.log('✓ Presentation started');
        }
    }

    /**
     * Pause/exit presentation
     */
    pausePresentation() {
        if (this.isPresenting) {
            this.isPresenting = false;
            document.body.classList.remove('presenting');
            this.showNotification('Presentation Paused ⏸');
            console.log('✓ Presentation paused');
        }
    }

    /**
     * Update slide counter display
     */
    updateSlideCounter() {
        if (this.slideCounter) {
            this.slideCounter.textContent = `${this.currentSlideIndex + 1} / ${this.slides.length}`;
        }
    }

    /**
     * Update connection status display
     * @param {string} status - Status type
     * @param {string} message - Status message
     */
    updateStatus(status, message) {
        if (this.statusIndicator) {
            this.statusIndicator.textContent = message;
            this.statusIndicator.className = `status ${status}`;
        }
    }

    /**
     * Show a temporary notification
     * @param {string} message - Notification message
     */
    showNotification(message) {
        const notification = document.getElementById('notification');
        if (notification) {
            notification.textContent = message;
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 2000);
        }
    }

    /**
     * Setup keyboard controls as backup
     */
    setupKeyboardControls() {
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowRight':
                case 'PageDown':
                    this.nextSlide();
                    break;
                case 'ArrowLeft':
                case 'PageUp':
                    this.prevSlide();
                    break;
                case '+':
                case '=':
                    this.zoomIn();
                    break;
                case '-':
                case '_':
                    this.zoomOut();
                    break;
                case 'Home':
                    this.showSlide(0);
                    break;
                case 'End':
                    this.showSlide(this.slides.length - 1);
                    break;
                case 'f':
                case 'F':
                    this.toggleFullscreen();
                    break;
                case 'Escape':
                    if (document.fullscreenElement) {
                        document.exitFullscreen();
                    }
                    break;
            }
        });
    }

    /**
     * Toggle fullscreen mode
     */
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
            this.showNotification('Fullscreen Mode');
        } else {
            document.exitFullscreen();
            this.showNotification('Exit Fullscreen');
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const engine = new PresentationEngine();
    engine.init();
    
    // Make engine globally accessible for debugging
    window.presentationEngine = engine;
});
