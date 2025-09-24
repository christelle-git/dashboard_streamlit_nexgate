// Script de diagnostic pour le tracking analytics
console.log('🔍 Démarrage du diagnostic de tracking...');

// Vérifier si le script de tracking est chargé
if (typeof AdvancedTracker === 'undefined') {
    console.error('❌ Le script advanced_tracking.js n\'est pas chargé');
} else {
    console.log('✅ Script advanced_tracking.js détecté');
}

// Vérifier si le tracker est initialisé
if (window.tracker) {
    console.log('✅ Tracker initialisé:', window.tracker);
    console.log('Session ID:', window.tracker.sessionId);
} else {
    console.error('❌ Tracker non initialisé');
}

// Test de connexion à l'API
console.log('🌐 Test de connexion à l\'API...');
fetch('https://christellelusso.nexgate.ch/api.php', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        type: 'diagnostic_test',
        session_id: 'diagnostic_' + Date.now(),
        timestamp: new Date().toISOString(),
        user_agent: navigator.userAgent,
        page: window.location.href
    })
})
.then(response => {
    console.log('📡 Réponse API:', response.status, response.statusText);
    return response.json();
})
.then(data => {
    console.log('✅ Données reçues:', data);
})
.catch(error => {
    console.error('❌ Erreur API:', error);
});

// Surveiller les clics sur la page
document.addEventListener('click', function(event) {
    console.log('🖱️ Clic détecté:', {
        element: event.target.tagName,
        id: event.target.id,
        class: event.target.className,
        href: event.target.href
    });
});

// Surveiller les téléchargements
document.addEventListener('click', function(event) {
    if (event.target.tagName === 'A' && event.target.href) {
        console.log('📁 Lien cliqué:', event.target.href);
    }
});

console.log('🔍 Diagnostic terminé - vérifiez la console pour les résultats'); 