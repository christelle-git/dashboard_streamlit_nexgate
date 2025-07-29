// Tracker Analytics V2 - Version sans cache
(function() {
    'use strict';
    
    let sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 15);
    let clickCount = 0;
    let lastClickTime = 0;
    
    // Fonction simple pour envoyer les données
    function sendData(data) {
        try {
            fetch('https://christellelusso.nexgate.ch/api.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            }).then(response => {
                if (response.ok) {
                    console.log('✅ Données envoyées avec succès');
                }
            }).catch(error => {
                console.log('⏱️ Requête annulée (normal)');
            });
        } catch (e) {
            // Ignore silencieusement les erreurs
        }
    }
    
    // Tracker de session
    function trackSession() {
        const sessionData = {
            type: 'session_start',
            session_id: sessionId,
            timestamp: new Date().toISOString(),
            client_ip: '127.0.0.1',
            country: 'France',
            city: 'Paris',
            latitude: 48.8566,
            longitude: 2.3522
        };
        sendData(sessionData);
    }
    
    // Tracker de clic
    function trackClick(event) {
        const now = Date.now();
        if (now - lastClickTime < 2000) return; // Anti-spam 2 secondes
        lastClickTime = now;
        
        clickCount++;
        
        const element = event.target;
        const clickData = {
            type: 'click',
            session_id: sessionId,
            element_type: element.tagName.toLowerCase(),
            page: window.location.pathname,
            timestamp: new Date().toISOString(),
            sequence_order: clickCount,
            x_coordinate: event.clientX,
            y_coordinate: event.clientY,
            client_ip: '127.0.0.1',
            country: 'France',
            city: 'Paris',
            latitude: 48.8566,
            longitude: 2.3522
        };
        
        sendData(clickData);
    }
    
    // Initialisation
    function init() {
        console.log('🚀 Tracker Analytics V2 initialisé');
        
        // Démarrer la session
        trackSession();
        
        // Écouter les clics
        document.addEventListener('click', trackClick, true);
        
        // Session de fin
        window.addEventListener('beforeunload', function() {
            const endData = {
                type: 'session_end',
                session_id: sessionId,
                timestamp: new Date().toISOString(),
                total_clicks: clickCount,
                client_ip: '127.0.0.1',
                country: 'France',
                city: 'Paris',
                latitude: 48.8566,
                longitude: 2.3522
            };
            sendData(endData);
        });
    }
    
    // Démarrer quand le DOM est prêt
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})(); 