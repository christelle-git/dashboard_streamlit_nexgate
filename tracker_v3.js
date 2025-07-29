// Tracker Analytics V3 - Version avec géolocalisation dynamique
(function() {
    'use strict';
    
    let sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 15);
    let clickCount = 0;
    let lastClickTime = 0;
    let locationData = {
        country: 'France',
        city: 'Non spécifié',
        latitude: 48.8566,
        longitude: 2.3522
    };
    
    // Fonction pour récupérer la vraie géolocalisation avec plusieurs APIs
    async function getRealLocation() {
        const apis = [
            'https://ipapi.co/json/',
            'https://api.myip.com',
            'https://ipinfo.io/json'
        ];
        
        for (let api of apis) {
            try {
                console.log('🔍 Tentative avec:', api);
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 3000);
                
                const response = await fetch(api, { 
                    signal: controller.signal,
                    headers: {
                        'Accept': 'application/json'
                    }
                });
                clearTimeout(timeoutId);
                
                const data = await response.json();
                
                if (data && data.country && data.city) {
                    locationData = {
                        country: data.country,
                        city: data.city,
                        latitude: data.latitude || data.lat || 48.8566,
                        longitude: data.longitude || data.lon || 2.3522
                    };
                    console.log('📍 Géolocalisation récupérée:', locationData.city, locationData.country);
                    return; // On s'arrête dès qu'on a une réponse
                }
            } catch (error) {
                console.log('⚠️ API échouée:', api, error.message);
                continue;
            }
        }
        
        // Fallback si toutes les APIs échouent
        console.log('📍 Utilisation des valeurs par défaut (géolocalisation échouée)');
    }
    
    // Fonction pour extraire le chemin du fichier cliqué
    function getClickedFilePath(element) {
        console.log('🔍 Élément cliqué:', element.tagName, element);
        
        // Si c'est une image
        if (element.tagName.toLowerCase() === 'img') {
            const src = element.src || element.getAttribute('src');
            console.log('📷 Image src:', src);
            if (src) {
                // Extrait le chemin relatif depuis l'URL complète
                const url = new URL(src, window.location.href);
                const path = url.pathname;
                console.log('📷 Chemin extrait:', path);
                return path;
            }
        }
        
        // Si c'est un lien
        if (element.tagName.toLowerCase() === 'a') {
            const href = element.href || element.getAttribute('href');
            console.log('🔗 Lien href:', href);
            if (href) {
                // Extrait le chemin relatif depuis l'URL complète
                const url = new URL(href, window.location.href);
                const path = url.pathname;
                console.log('🔗 Chemin extrait:', path);
                return path;
            }
        }
        
        // Si c'est un bouton avec un lien
        if (element.tagName.toLowerCase() === 'button') {
            const link = element.querySelector('a');
            if (link) {
                const href = link.href || link.getAttribute('href');
                console.log('🔘 Bouton avec lien:', href);
                if (href) {
                    const url = new URL(href, window.location.href);
                    const path = url.pathname;
                    console.log('🔘 Chemin extrait:', path);
                    return path;
                }
            }
        }
        
        // Cherche dans les parents
        let parent = element.parentElement;
        let depth = 0;
        while (parent && parent !== document.body && depth < 5) {
            console.log('🔍 Parent niveau', depth, ':', parent.tagName);
            
            if (parent.tagName.toLowerCase() === 'a') {
                const href = parent.href || parent.getAttribute('href');
                console.log('🔗 Parent lien:', href);
                if (href) {
                    const url = new URL(href, window.location.href);
                    const path = url.pathname;
                    console.log('🔗 Parent chemin extrait:', path);
                    return path;
                }
            }
            if (parent.tagName.toLowerCase() === 'img') {
                const src = parent.src || parent.getAttribute('src');
                console.log('📷 Parent image:', src);
                if (src) {
                    const url = new URL(src, window.location.href);
                    const path = url.pathname;
                    console.log('📷 Parent chemin extrait:', path);
                    return path;
                }
            }
            
            parent = parent.parentElement;
            depth++;
        }
        
        // Fallback: page courante
        console.log('⚠️ Fallback vers page courante:', window.location.pathname);
        return window.location.pathname;
    }
    
    // Fonction simple pour envoyer les données
    function sendData(data) {
        try {
            console.log('📤 Envoi des données:', data);
            fetch('https://christellelusso.nexgate.ch/api.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            }).then(response => {
                if (response.ok) {
                    console.log('✅ Données envoyées avec succès');
                } else {
                    console.log('❌ Erreur serveur:', response.status);
                }
            }).catch(error => {
                console.log('❌ Erreur réseau:', error.message);
            });
        } catch (e) {
            console.log('❌ Erreur générale:', e.message);
        }
    }
    
    // Tracker de session
    function trackSession() {
        const sessionData = {
            type: 'session_start',
            session_id: sessionId,
            timestamp: new Date().toISOString(),
            client_ip: '127.0.0.1',
            country: locationData.country,
            city: locationData.city,
            latitude: locationData.latitude,
            longitude: locationData.longitude
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
        const clickedPath = getClickedFilePath(element);
        
        const clickData = {
            type: 'click',
            session_id: sessionId,
            element_type: element.tagName.toLowerCase(),
            page: clickedPath,
            timestamp: new Date().toISOString(),
            sequence_order: clickCount,
            x_coordinate: event.clientX,
            y_coordinate: event.clientY,
            client_ip: '127.0.0.1',
            country: locationData.country,
            city: locationData.city,
            latitude: locationData.latitude,
            longitude: locationData.longitude
        };
        
        sendData(clickData);
    }
    
    // Initialisation
    async function init() {
        console.log('🚀 Tracker Analytics V3 initialisé');
        
        // Récupère la vraie géolocalisation
        await getRealLocation();
        
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
                country: locationData.country,
                city: locationData.city,
                latitude: locationData.latitude,
                longitude: locationData.longitude
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