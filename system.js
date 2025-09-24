// Tracker Analytics V6 - IP et GPS Separes
// Version compatible avec l'API corrigee

(function() {
    'use strict';
    
    // Configuration
    const API_URL = 'api.php';
    const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes
    
    // Variables globales
    let sessionId = null;
    let sessionStart = null;
    let clickCount = 0;
    let isTracking = false;
    
    // Initialisation
    function init() {
        startSession();
        setupEventListeners();
        isTracking = true;
    }
    
    // Demarrer une nouvelle session
    function startSession() {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        sessionStart = new Date().toISOString();
    }
    
    // Verifier si la session a expire
    function checkSessionExpiry() {
        if (sessionStart && (Date.now() - new Date(sessionStart).getTime()) > SESSION_TIMEOUT) {
            startSession();
        }
    }
    
    // Recuperer l'IP publique (desactive a cause de CORS)
    async function getPublicIP() {
        // L'IP sera recuperee par le serveur
        return 'Non specifie';
    }
    
    // Recuperer la geolocalisation IP
    async function getIPGeolocation(ip) {
        if (!ip || ip === 'Non specifie') return null;
        
        try {
            const response = await fetch(`https://ipapi.co/${ip}/json/`);
            const data = await response.json();
            return {
                country: data.country_name || 'Non specifie',
                city: data.city || 'Non specifie',
                latitude: data.latitude || 0,
                longitude: data.longitude || 0
            };
        } catch (error) {
            return null;
        }
    }
    
    // Recuperer la position GPS (priorite absolue)
    function getGPSLocation() {
        return new Promise((resolve) => {
            if (!navigator.geolocation) {
                resolve(null);
                return;
            }
            
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const coords = position.coords;
                    resolve({
                        latitude: coords.latitude,
                        longitude: coords.longitude,
                        accuracy: coords.accuracy
                    });
                },
                (error) => {
                    resolve(null);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0  // Toujours demander une position fraiche
                }
            );
        });
    }
    
    // Envoyer les donnees au serveur
    async function sendData(data) {
        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Tracker-Agent': 'TrackerV6/1.0'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                return true;
            } else {
                return false;
            }
        } catch (error) {
            return false;
        }
    }
    
    // Traiter un clic
    async function handleClick(event) {
        if (!isTracking) return;
        
        checkSessionExpiry();
        clickCount++;
        
        // Recuperer les informations de base
        const ip = 'Non specifie'; // L'IP sera recuperee par le serveur
        const ipGeo = null; // La geolocalisation sera faite par le serveur
        const gps = await getGPSLocation();
        
        // Preparer les donnees
        const clickData = {
            type: 'click',
            session_id: sessionId,
            timestamp: new Date().toISOString(),
            page: window.location.pathname,
            element_type: event.target.tagName.toLowerCase(),
            sequence_order: clickCount,
            x_coordinate: event.clientX,
            y_coordinate: event.clientY,
            client_ip: ip,
            ip_source: 'client',
            gps_latitude: gps ? gps.latitude : 0,
            gps_longitude: gps ? gps.longitude : 0,
            gps_accuracy: gps ? gps.accuracy : 0,
            gps_source: gps ? 'browser' : 'none',
            user_agent: navigator.userAgent,
            screen_resolution: screen.width + 'x' + screen.height,
            viewport_size: window.innerWidth + 'x' + window.innerHeight,
            referrer: document.referrer || '',
            language: navigator.language || 'fr',
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Europe/Paris'
        };
        
        // Ajouter les donnees de geolocalisation IP si disponibles
        if (ipGeo) {
            clickData.geo_country = ipGeo.country;
            clickData.geo_city = ipGeo.city;
            clickData.geo_latitude = ipGeo.latitude;
            clickData.geo_longitude = ipGeo.longitude;
        }
        
        // Envoyer les donnees
        const success = await sendData(clickData);
        
        if (success) {
            // Emettre un evenement personnalise pour le debug
            window.dispatchEvent(new CustomEvent('trackerClick', { detail: clickData }));
        }
    }
    
    // Configurer les ecouteurs d'evenements
    function setupEventListeners() {
        // Clics sur tous les elements cliquables
        document.addEventListener('click', handleClick, true);
        
        // Navigation (pour detecter les changements de page)
        window.addEventListener('popstate', () => {
            startSession();
        });
        
        // Visibilite de la page (pour detecter les retours)
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                checkSessionExpiry();
            }
        });
        
        // Avant de quitter la page
        window.addEventListener('beforeunload', () => {
            // Envoyer un evenement de fin de session
            if (sessionId) {
                sendData({
                    type: 'session_end',
                    session_id: sessionId,
                    timestamp: new Date().toISOString(),
                    duration: Date.now() - new Date(sessionStart).getTime(),
                    click_count: clickCount
                });
            }
        });
    }
    
    // Demarrer le tracker quand le DOM est pret
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Exposer des fonctions pour le debug
    window.TrackerV6 = {
        getSessionId: () => sessionId,
        getClickCount: () => clickCount,
        getSessionStart: () => sessionStart,
        isTracking: () => isTracking,
        forceNewSession: startSession,
        testClick: (x = 100, y = 100) => {
            const event = new MouseEvent('click', { clientX: x, clientY: y });
            handleClick(event);
        }
    };
    
})(); 