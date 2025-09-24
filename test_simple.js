// Test simple du tracking
console.log('🚀 Script de tracking chargé !');

document.addEventListener('click', function(event) {
    console.log('🖱️ Clic détecté sur:', event.target.tagName);
    
    // Test d'envoi vers l'API
    fetch('https://christellelusso.nexgate.ch/api.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            type: 'test_click',
            session_id: 'test_' + Date.now(),
            element: event.target.tagName,
            timestamp: new Date().toISOString(),
            test: true
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('✅ Données envoyées avec succès:', data);
    })
    .catch(error => {
        console.error('❌ Erreur envoi:', error);
    });
});

console.log('🎯 Tracking configuré et prêt !'); 