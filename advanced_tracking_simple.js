class SimpleTracker {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.clickSequence = 0;
        this.apiEndpoint = 'https://christellelusso.nexgate.ch/api.php';
        this.lastSendTime = 0;
        this.minSendInterval = 2000;
        
        this.init();
    }

    generateSessionId() {
        const timestamp = Date.now();
        const randomId = Math.random().toString(36).substring(2, 15);
        return `session_${timestamp}_${randomId}`;
    }

    async getGeolocation() {
        try {
            // Utilise l'API de géolocalisation du navigateur si disponible
            if (navigator.geolocation) {
                return new Promise((resolve) => {
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            resolve({
                                latitude: position.coords.latitude,
                                longitude: position.coords.longitude,
                                country: 'France', // Valeur par défaut
                                city: 'Non spécifié',
                                ip: '127.0.0.1'
                            });
                        },
                        (error) => {
                            console.log('Géolocalisation navigateur refusée:', error.message);
                            resolve({
                                latitude: 0,
                                longitude: 0,
                                country: 'France',
                                city: 'Non spécifié',
                                ip: '127.0.0.1'
                            });
                        },
                        { timeout: 5000 }
                    );
                });
            }
        } catch (error) {
            console.log('Géolocalisation non disponible:', error.message);
        }
        
        // Valeurs par défaut
        return {
            latitude: 0,
            longitude: 0,
            country: 'France',
            city: 'Non spécifié',
            ip: '127.0.0.1'
        };
    }

    init() {
        this.setupEventListeners();
        this.trackSessionStart();
    }

    setupEventListeners() {
        document.addEventListener('click', async (event) => {
            try {
                await this.trackClick(event);
            } catch (error) {
                console.error('Erreur lors du tracking du clic:', error);
            }
        });

        window.addEventListener('beforeunload', () => {
            this.trackSessionEnd();
        });
    }

    trackSessionStart() {
        const sessionData = {
            type: 'session_start',
            session_id: this.sessionId,
            start_time: new Date().toISOString(),
            user_agent: navigator.userAgent,
            page: window.location.pathname,
            timestamp: new Date().toISOString(),
            client_ip: '127.0.0.1',
            country: 'France',
            city: 'Non spécifié',
            latitude: 0,
            longitude: 0
        };
        
        this.sendData(sessionData);
    }

    trackSessionEnd() {
        const sessionData = {
            type: 'session_end',
            session_id: this.sessionId,
            end_time: new Date().toISOString(),
            duration_seconds: 1,
            total_clicks: this.clickSequence,
            user_journey: '[]',
            pages_visited: 1,
            timestamp: new Date().toISOString(),
            client_ip: '127.0.0.1',
            country: 'France',
            city: 'Non spécifié',
            latitude: 0,
            longitude: 0
        };
        
        this.sendData(sessionData);
    }

    async trackClick(event) {
        const now = Date.now();
        if (now - this.lastSendTime < this.minSendInterval) {
            return;
        }
        this.lastSendTime = now;

        this.clickSequence++;
        
        const element = event.target;
        const elementInfo = {
            id: element.id || '',
            type: element.tagName.toLowerCase(),
            className: element.className || '',
            text: element.textContent ? element.textContent.substring(0, 50) : ''
        };

        let fileClicked = null;
        if (element.tagName === 'A' && element.href) {
            const fileName = element.href.split('/').pop();
            if (fileName && fileName.includes('.')) {
                fileClicked = fileName;
            }
        }
        
        // Récupère la géolocalisation
        const locationData = await this.getGeolocation();
        
        const clickData = {
            type: 'click',
            session_id: this.sessionId,
            element_id: elementInfo.id,
            element_type: elementInfo.type,
            element_class: elementInfo.className,
            element_text: elementInfo.text,
            page: window.location.pathname,
            timestamp: new Date().toISOString(),
            sequence_order: this.clickSequence,
            x_coordinate: event.clientX,
            y_coordinate: event.clientY,
            client_ip: locationData.ip,
            country: locationData.country,
            city: locationData.city,
            latitude: locationData.latitude,
            longitude: locationData.longitude
        };

        if (fileClicked) {
            clickData.file_clicked = fileClicked;
        }

        this.sendData(clickData);
    }

    async sendData(data) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);

            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Tracker-Agent': 'SimpleTracker/1.0'
                },
                body: JSON.stringify(data),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (response.ok) {
                console.log('✔ Données envoyées avec succès');
            } else {
                console.error('❌ Erreur lors de l\'envoi:', response.status, response.statusText);
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                console.log('⏱️ Requête annulée (timeout/navigation)');
            } else {
                console.error('❌ Erreur réseau:', error.message);
            }
        }
    }
}

// Initialise le tracker
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.simpleTracker = new SimpleTracker();
    });
} else {
    window.simpleTracker = new SimpleTracker();
} 