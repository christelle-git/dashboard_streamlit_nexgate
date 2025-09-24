class AdvancedTracker {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.clickSequence = 0;
        this.apiEndpoint = 'https://christellelusso.nexgate.ch/api.php'; // API web
        this.lastSendTime = 0;
        this.minSendInterval = 2000; // Minimum 2 secondes entre les envois
        this.locationData = null; // Stockage des données de géolocalisation
        
        this.init();
    }

    generateSessionId() {
        const timestamp = Date.now();
        const randomId = Math.random().toString(36).substring(2, 15);
        return `session_${timestamp}_${randomId}`;
    }

    async getGeolocation() {
        try {
            // Utilise une API plus simple et fiable
            const response = await fetch('https://api.ipify.org?format=json');
            const ipData = await response.json();
            
            // Utilise l'API de géolocalisation gratuite
            const geoResponse = await fetch(`https://ipapi.co/${ipData.ip}/json/`);
            const geoData = await geoResponse.json();
            
            if (geoData && geoData.country) {
                const locationData = {
                    latitude: geoData.latitude || 0,
                    longitude: geoData.longitude || 0,
                    country: geoData.country_name || 'Non spécifié',
                    city: geoData.city || 'Non spécifié',
                    ip: ipData.ip
                };
                
                console.log('�� Géolocalisation récupérée:', locationData);
                return locationData;
            }
        } catch (error) {
            console.log('Géolocalisation non disponible:', error.message);
        }
        
        return {
            latitude: 0,
            longitude: 0,
            country: 'Non spécifié',
            city: 'Non spécifié',
            ip: '127.0.0.1'
        };
    }

    init() {
        this.setupEventListeners();
        this.trackSessionStart();
    }

    setupEventListeners() {
        // Écoute tous les clics
        document.addEventListener('click', async (event) => {
            try {
                await this.trackClick(event);
            } catch (error) {
                console.error('Erreur lors du tracking du clic:', error);
            }
        });

        // Écoute les changements de page
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
            timestamp: new Date().toISOString()
        };
        
        this.sendData(sessionData);
    }

    trackSessionEnd() {
        const sessionData = {
            type: 'session_end',
            session_id: this.sessionId,
            end_time: new Date().toISOString(),
            duration_seconds: Math.floor((Date.now() - this.sessionStartTime) / 1000),
            total_clicks: this.clickSequence,
            user_journey: JSON.stringify(this.userJourney),
            pages_visited: this.pagesVisited,
            timestamp: new Date().toISOString()
        };
        
        this.sendData(sessionData);
    }

    async trackClick(event) {
        // Vérifie l'intervalle minimum entre les envois
        const now = Date.now();
        if (now - this.lastSendTime < this.minSendInterval) {
            return;
        }
        this.lastSendTime = now;

        this.clickSequence++;
        
        // Récupère les informations sur l'élément cliqué
        const element = event.target;
        const elementInfo = {
            id: element.id || '',
            type: element.tagName.toLowerCase(),
            className: element.className || '',
            text: element.textContent ? element.textContent.substring(0, 50) : ''
        };

        // Détecte les clics sur les fichiers
        let fileClicked = null;
        if (element.tagName === 'A' && element.href) {
            const fileName = element.href.split('/').pop();
            if (fileName && fileName.includes('.')) {
                fileClicked = fileName;
            }
        }
        
        // Récupère les données de géolocalisation si pas encore fait
        if (!this.locationData) {
            this.locationData = await this.getGeolocation();
        }
        
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
            client_ip: this.locationData.ip || '127.0.0.1',
            country: this.locationData.country,
            city: this.locationData.city,
            latitude: this.locationData.latitude,
            longitude: this.locationData.longitude
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
                    'X-Tracker-Agent': 'AdvancedTracker/1.0'
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

// Initialise le tracker quand le DOM est chargé
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.advancedTracker = new AdvancedTracker();
    });
} else {
    window.advancedTracker = new AdvancedTracker();
}