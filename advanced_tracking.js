// Système de tracking avancé pour site web
class AdvancedTracker {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.startTime = Date.now();
        this.clickSequence = 0;
        this.userJourney = [];
        this.lastActivity = Date.now();
        this.apiEndpoint = 'https://christellelusso.nexgate.ch/api.php'; // Adaptez selon votre API
        
        this.init();
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    async init() {
        // Démarre la session
        await this.startSession();
        
        // Configure les event listeners
        this.setupEventListeners();
        
        // Surveille l'activité utilisateur
        this.setupActivityMonitoring();
        
        // Gère la fermeture de session
        this.setupSessionEnd();
    }
    
    async startSession() {
        const location = await this.getGeolocation();
        const userAgent = navigator.userAgent;
        
        const sessionData = {
            type: 'session_start',
            session_id: this.sessionId,
            user_agent: userAgent,
            start_time: new Date().toISOString(),
            url: window.location.href,
            referrer: document.referrer,
            screen_resolution: `${screen.width}x${screen.height}`,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            language: navigator.language,
            ...location
        };
        
        await this.sendData(sessionData);
    }
    
    async getGeolocation() {
        try {
            // Utilise l'API de géolocalisation du navigateur
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    timeout: 5000,
                    enableHighAccuracy: false
                });
            });
            
            return {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy
            };
        } catch (error) {
            // Fallback vers l'IP géolocalisation
            try {
                console.log('DEBUG: Données envoyées:', data);
                console.log('DEBUG: Endpoint:', this.apiEndpoint);
                const response = await fetch('https://ipapi.co/json/');
                const data = await response.json();
                return {
                    latitude: data.latitude,
                    longitude: data.longitude,
                    country: data.country_name,
                    city: data.city,
                    ip: data.ip
                };
            } catch (ipError) {
                console.log('Géolocalisation non disponible');
                return {};
            }
        }
    }
    
    setupEventListeners() {
        // Tracking des clics
        document.addEventListener('click', (event) => {
            this.trackClick(event);
        });
        
        // Tracking des téléchargements de fichiers
        document.addEventListener('click', (event) => {
            if (event.target.tagName === 'A' && event.target.href) {
                this.trackFileDownload(event.target.href, event.target);
            }
        });
        
        // Tracking du scroll
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                this.trackScroll();
            }, 1000);
        });
        
        // Tracking des changements de page (SPA)
        window.addEventListener('popstate', () => {
            this.trackPageChange();
        });
      
      	window.addEventListener('click', function(event) {
    		console.log('🖱️ Clic détecté sur WINDOW:', event.target.tagName);
		});
      
    }
    
    trackClick(event) {
        this.clickSequence++;
        this.lastActivity = Date.now();
        
        const element = event.target;
        const elementInfo = this.getElementInfo(element);
        
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
            y_coordinate: event.clientY
        };
        
        // Ajoute au parcours utilisateur
        this.userJourney.push({
            action: 'click',
            element: elementInfo.id || elementInfo.type,
            page: window.location.pathname,
            timestamp: Date.now()
        });
        
        this.sendData(clickData);
    }
    
    trackFileDownload(url, element) {
        const fileName = url.split('/').pop().split('?')[0];
        const fileExtension = fileName.split('.').pop().toLowerCase();
        
        const downloadData = {
            type: 'file_download',
            session_id: this.sessionId,
            file_url: url,
            file_name: fileName,
            file_extension: fileExtension,
            element_text: element.textContent || element.title,
            page: window.location.pathname,
            timestamp: new Date().toISOString(),
            sequence_order: this.clickSequence
        };
        
        this.sendData(downloadData);
    }
    
    trackScroll() {
        const scrollPercent = Math.round(
            (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
        );
        
        const scrollData = {
            type: 'scroll',
            session_id: this.sessionId,
            scroll_percent: scrollPercent,
            page: window.location.pathname,
            timestamp: new Date().toISOString()
        };
        
        this.sendData(scrollData);
    }
    
    trackPageChange() {
        const pageData = {
            type: 'page_change',
            session_id: this.sessionId,
            from_page: this.currentPage || '/',
            to_page: window.location.pathname,
            timestamp: new Date().toISOString()
        };
        
        this.currentPage = window.location.pathname;
        this.sendData(pageData);
    }
    
    getElementInfo(element) {
        return {
            id: element.id || '',
            type: element.tagName.toLowerCase(),
            className: element.className || '',
            text: element.textContent?.substring(0, 100) || '',
            href: element.href || '',
            src: element.src || ''
        };
    }
    
    setupActivityMonitoring() {
        // Surveille l'inactivité
        setInterval(() => {
            const inactiveTime = Date.now() - this.lastActivity;
            if (inactiveTime > 300000) { // 5 minutes d'inactivité
                this.trackInactivity();
            }
        }, 60000); // Vérifie chaque minute
        
        // Met à jour l'activité sur les mouvements de souris
        document.addEventListener('mousemove', () => {
            this.lastActivity = Date.now();
        });
        
        // Met à jour l'activité sur les touches clavier
        document.addEventListener('keypress', () => {
            this.lastActivity = Date.now();
        });
    }
    
    trackInactivity() {
        const inactivityData = {
            type: 'inactivity',
            session_id: this.sessionId,
            inactive_duration: Date.now() - this.lastActivity,
            page: window.location.pathname,
            timestamp: new Date().toISOString()
        };
        
        this.sendData(inactivityData);
    }
    
    setupSessionEnd() {
        // Gère la fermeture de la page
        window.addEventListener('beforeunload', () => {
            this.endSession();
        });
        
        // Gère la fermeture de l'onglet
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.endSession();
            }
        });
    }
    
    endSession() {
        const sessionDuration = Date.now() - this.startTime;
        
        const endData = {
            type: 'session_end',
            session_id: this.sessionId,
            end_time: new Date().toISOString(),
            duration_seconds: Math.round(sessionDuration / 1000),
            total_clicks: this.clickSequence,
            user_journey: JSON.stringify(this.userJourney),
            pages_visited: [...new Set(this.userJourney.map(j => j.page))].length
        };
        
        // Utilise sendBeacon pour s'assurer que les données sont envoyées
        if (navigator.sendBeacon) {
            navigator.sendBeacon(
                this.apiEndpoint,
                JSON.stringify(endData)
            );
        } else {
            this.sendData(endData);
        }
    }
    
    async sendData(data) {
        try {
            console.log('DEBUG: Données envoyées:', data);
            console.log('DEBUG: Endpoint:', this.apiEndpoint);
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Erreur lors de l\'envoi des données:', response.status, errorText);
            }
        } catch (error) {
            console.error('Erreur réseau:', error);
            this.storeOfflineData(data);
        }
    }
    
    storeOfflineData(data) {
        try {
            const offlineData = JSON.parse(localStorage.getItem('offline_tracking') || '[]');
            offlineData.push(data);
            localStorage.setItem('offline_tracking', JSON.stringify(offlineData));
        } catch (error) {
            console.error('Erreur stockage offline:', error);
        }
    }
    
    async retryOfflineData() {
        try {
            const offlineData = JSON.parse(localStorage.getItem('offline_tracking') || '[]');
            if (offlineData.length > 0) {
                for (const data of offlineData) {
                    await this.sendData(data);
                }
                localStorage.removeItem('offline_tracking');
            }
        } catch (error) {
            console.error('Erreur retry offline:', error);
        }
    }
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    window.tracker = new AdvancedTracker();
    
    // Retry des données offline au chargement
    window.tracker.retryOfflineData();
});

// API publique pour tracking personnalisé
window.trackCustomEvent = function(eventName, eventData) {
    const customData = {
        type: 'custom_event',
        session_id: window.tracker.sessionId,
        event_name: eventName,
        event_data: eventData,
        page: window.location.pathname,
        timestamp: new Date().toISOString()
    };
    
    window.tracker.sendData(customData);
};

// Exemples d'utilisation :
// trackCustomEvent('video_play', { video_id: 'intro_video', duration: 120 });
// trackCustomEvent('form_submit', { form_name: 'contact_form', success: true });

// Ajoute ce code dans la console du navigateur pour tester
fetch('https://christellelusso.nexgate.ch/api.php', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ type: 'test_manual', timestamp: new Date().toISOString() })
}).then(r => r.json()).then(console.log).catch(console.error);