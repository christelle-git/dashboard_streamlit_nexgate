<?php
// Script pour vérifier les nouvelles sessions et envoyer des alertes
header('Content-Type: application/json');

// Fichier pour stocker les sessions déjà notifiées
$notifiedFile = 'notified_sessions.json';

// Charger les sessions déjà notifiées
$notifiedSessions = [];
if (file_exists($notifiedFile)) {
    $notifiedSessions = json_decode(file_get_contents($notifiedFile), true) ?: [];
}

// Récupérer toutes les sessions
$data = json_decode(file_get_contents('https://christellelusso.nexgate.ch/analytics_data.json'), true);

if (!$data) {
    http_response_code(500);
    echo json_encode(['error' => 'Impossible de récupérer les données']);
    exit;
}

// Filtrer les sessions externes (pas notre IP)
$externalSessions = array_filter($data, function($session) {
    return isset($session['client_ip']) && $session['client_ip'] !== '82.66.151.2';
});

// Grouper par session_id
$sessions = [];
foreach ($externalSessions as $event) {
    $sessionId = $event['session_id'] ?? 'unknown';
    if (!isset($sessions[$sessionId])) {
        $sessions[$sessionId] = $event;
    } else {
        // Mettre à jour avec les données les plus récentes
        if ($event['timestamp'] > $sessions[$sessionId]['timestamp']) {
            $sessions[$sessionId] = $event;
        }
    }
}

// Vérifier les nouvelles sessions
$newSessions = [];
foreach ($sessions as $sessionId => $session) {
    if (!in_array($sessionId, $notifiedSessions)) {
        $newSessions[] = $session;
        $notifiedSessions[] = $sessionId;
    }
}

// Sauvegarder les sessions notifiées
file_put_contents($notifiedFile, json_encode($notifiedSessions));

// Envoyer des alertes pour les nouvelles sessions
$alertsSent = 0;
foreach ($newSessions as $session) {
    // Envoyer l'alerte
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, 'https://christellelusso.nexgate.ch/send_alert.php');
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($session));
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    
    $result = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode === 200) {
        $alertsSent++;
    }
}

echo json_encode([
    'success' => true,
    'new_sessions' => count($newSessions),
    'alerts_sent' => $alertsSent,
    'total_external_sessions' => count($sessions)
]);
?>
