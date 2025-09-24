// Tracker Analytics V4 - Version ultra-simplifiée
(function() {
    'use strict';
    
    let sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 15);
    let clickCount = 0;
    let lastClickTime = 0;
    
    console.log('🚀 Tracker Analytics V4 initialisé');
    
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
    
    // Fonction simple pour envoyer les données
    function sendData(data) {
        console.log('📤 Envoi des données:', data);
        
        // Utilise XMLHttpRequest au lieu de fetch pour éviter les problèmes
        const xhr = new XMLHttpRequest();
        xhr.open('POST', 'https://christellelusso.nexgate.ch/api.php', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    console.log('✅ Données envoyées avec succès');
                } else {
                    console.log('❌ Erreur serveur:', xhr.status, xhr.statusText);
                }
            }
        };
        
        xhr.onerror = function() {
            console.log('❌ Erreur réseau');
        };
        
        try {
            xhr.send(JSON.stringify(data));
        } catch (e) {
            console.log('❌ Erreur envoi:', e.message);
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
            city: 'Non spécifié',
            latitude: 48.8566,
            longitude: 2.3522
        };
        sendData(sessionData);
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
            country: 'France',
            city: 'Non spécifié',
            latitude: 48.8566,
            longitude: 2.3522
        };
        
        sendData(clickData);
    }
    
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
            city: 'Non spécifié',
            latitude: 48.8566,
            longitude: 2.3522
        };
        sendData(endData);
    });
    
})(); 