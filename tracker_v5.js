// Tracker Analytics V5 - Version avec Beacon API
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
    
    console.log('🚀 Tracker Analytics V5 initialisé avec Beacon API');
    
    // Fonction pour récupérer la géolocalisation
    async function getRealLocation() {
        try {
            console.log('🔍 Récupération de la géolocalisation...');
            const response = await fetch('https://ipapi.co/json/', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data && data.country && data.city) {
                    locationData = {
                        country: data.country,
                        city: data.city,
                        latitude: data.latitude || 48.8566,
                        longitude: data.longitude || 2.3522
                    };
                    console.log('📍 Géolocalisation récupérée:', locationData.city, locationData.country);
                } else {
                    console.log('📍 Données de géolocalisation incomplètes, utilisation des valeurs par défaut');
                }
            } else {
                console.log('📍 Erreur API géolocalisation, utilisation des valeurs par défaut');
            }
        } catch (error) {
            console.log('📍 Erreur géolocalisation:', error.message, '- utilisation des valeurs par défaut');
        }
    }
    
    // Fonction pour extraire le chemin du fichier cliqué
    function getClickedFilePath(element) {
        console.log('🔍 Élément cliqué:', element.tagName);
        
        // Si c'est une image
        if (element.tagName.toLowerCase() === 'img') {
            const src = element.src || element.getAttribute('src');
            console.log('📷 Image src:', src);
            if (src) {
                try {
                    const url = new URL(src, window.location.href);
                    const path = url.pathname;
                    console.log('📷 Chemin extrait:', path);
                    return path;
                } catch (e) {
                    console.log('📷 Erreur URL, retourne src:', src);
                    return src;
                }
            }
        }
        
        // Si c'est un lien
        if (element.tagName.toLowerCase() === 'a') {
            const href = element.href || element.getAttribute('href');
            console.log('🔗 Lien href:', href);
            if (href) {
                try {
                    const url = new URL(href, window.location.href);
                    const path = url.pathname;
                    console.log('🔗 Chemin extrait:', path);
                    return path;
                } catch (e) {
                    console.log('🔗 Erreur URL, retourne href:', href);
                    return href;
                }
            }
        }
        
        // Cherche dans les parents
        let parent = element.parentElement;
        let depth = 0;
        while (parent && parent !== document.body && depth < 3) {
            console.log('🔍 Parent niveau', depth, ':', parent.tagName);
            
            if (parent.tagName.toLowerCase() === 'a') {
                const href = parent.href || parent.getAttribute('href');
                if (href) {
                    try {
                        const url = new URL(href, window.location.href);
                        const path = url.pathname;
                        console.log('🔗 Parent chemin:', path);
                        return path;
                    } catch (e) {
                        return href;
                    }
                }
            }
            if (parent.tagName.toLowerCase() === 'img') {
                const src = parent.src || parent.getAttribute('src');
                if (src) {
                    try {
                        const url = new URL(src, window.location.href);
                        const path = url.pathname;
                        console.log('📷 Parent chemin:', path);
                        return path;
                    } catch (e) {
                        return src;
                    }
                }
            }
            
            parent = parent.parentElement;
            depth++;
        }
        
        console.log('⚠️ Fallback vers page courante:', window.location.pathname);
        return window.location.pathname;
    }
    
    // Fonction pour envoyer les données avec Beacon API
    function sendData(data) {
        console.log('📤 Envoi des données avec Beacon:', data);
        
        try {
            // Utilise Beacon API si disponible
            if (navigator.sendBeacon) {
                const blob = new Blob([JSON.stringify(data)], {type: 'application/json'});
                const success = navigator.sendBeacon('https://christellelusso.nexgate.ch/api.php', blob);
                
                if (success) {
                    console.log('✅ Données envoyées avec succès via Beacon');
                } else {
                    console.log('❌ Échec de l\'envoi via Beacon, fallback vers fetch');
                    sendDataFallback(data);
                }
            } else {
                console.log('⚠️ Beacon non disponible, utilisation de fetch');
                sendDataFallback(data);
            }
        } catch (e) {
            console.log('❌ Erreur Beacon:', e.message);
            sendDataFallback(data);
        }
    }
    
    // Fallback avec fetch
    function sendDataFallback(data) {
        fetch('https://christellelusso.nexgate.ch/api.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            keepalive: true // Garde la requête active même si la page se ferme
        }).then(response => {
            if (response.ok) {
                console.log('✅ Données envoyées avec succès via fetch');
            } else {
                console.log('❌ Erreur serveur:', response.status);
            }
        }).catch(error => {
            console.log('❌ Erreur réseau:', error.message);
        });
    }
    
    // Tracker de clic
    function trackClick(event) {
        const now = Date.now();
        if (now - lastClickTime < 1000) return; // Anti-spam 1 seconde
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
        // Récupère la géolocalisation
        await getRealLocation();
        
        // Écouter les clics
        document.addEventListener('click', trackClick, true);
    }
    
    // Démarrer l'initialisation
    init();
    
})(); 