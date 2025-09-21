<?php
// Script pour vérifier les nouvelles sessions et envoyer des alertes
header('Content-Type: application/json');

// 🚨 URGENT : DÉSACTIVATION COMPLÈTE POUR ÉVITER LE DÉRÉFÉRENCEMENT
echo json_encode([
    'success' => false,
    'message' => 'Système d\'alerte DÉSACTIVÉ pour éviter le déréférencement',
    'status' => 'DISABLED_FOR_SEO',
    'reason' => 'Protection contre le déréférencement Google'
]);
exit;

// Fichier pour stocker les sessions déjà notifiées
$notifiedFile = 'notified_sessions.json';
$lastCheckFile = 'last_check.json';

// Protection contre les appels trop fréquents (minimum 2 minutes entre les vérifications)
if (file_exists($lastCheckFile)) {
    $lastCheck = json_decode(file_get_contents($lastCheckFile), true);
    $timeSinceLastCheck = time() - $lastCheck['timestamp'];
    
    if ($timeSinceLastCheck < 120) { // 2 minutes = 120 secondes
        echo json_encode([
            'success' => true,
            'message' => 'Vérification trop récente, attendez 2 minutes',
            'next_check_in' => 120 - $timeSinceLastCheck . ' secondes',
            'debug' => 'Protection anti-spam activée'
        ]);
        exit;
    }
}

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

// Vérifier les nouvelles sessions (seulement celles des dernières 24h)
$newSessions = [];
$yesterday = date('Y-m-d', strtotime('-1 day'));

foreach ($sessions as $sessionId => $session) {
    // Vérifier si la session est récente (dernières 24h)
    $sessionDate = date('Y-m-d', strtotime($session['timestamp']));
    
    if ($sessionDate >= $yesterday && !in_array($sessionId, $notifiedSessions)) {
        $newSessions[] = $session;
        $notifiedSessions[] = $sessionId;
    }
}

// Sauvegarder les sessions notifiées
file_put_contents($notifiedFile, json_encode($notifiedSessions));

// Sauvegarder le timestamp de la dernière vérification
file_put_contents($lastCheckFile, json_encode(['timestamp' => time()]));

// Envoyer UN SEUL email de résumé pour toutes les nouvelles sessions
$alertsSent = 0;
$debugInfo = [];

if (count($newSessions) > 0) {
    $debugInfo[] = "Nouvelles sessions détectées: " . count($newSessions);
    
    // Créer un résumé de toutes les nouvelles sessions
    $summary = [
        'count' => count($newSessions),
        'sessions' => $newSessions,
        'timestamp' => date('Y-m-d H:i:s'),
        'type' => 'summary',
        'debug' => 'Email de résumé unique'
    ];
    
    $debugInfo[] = "Résumé créé avec " . count($newSessions) . " sessions";
    
    // Envoyer l'alerte de résumé
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, 'https://christellelusso.nexgate.ch/send_alert.php');
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($summary));
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    
    $result = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    $debugInfo[] = "CURL HTTP Code: " . $httpCode;
    $debugInfo[] = "CURL Result: " . substr($result, 0, 100);
    
    if ($httpCode === 200) {
        $alertsSent = 1; // Un seul email envoyé
        $debugInfo[] = "Email envoyé avec succès";
    } else {
        $debugInfo[] = "Erreur envoi email: " . $httpCode;
    }
} else {
    $debugInfo[] = "Aucune nouvelle session détectée";
}

echo json_encode([
    'success' => true,
    'new_sessions' => count($newSessions),
    'alerts_sent' => $alertsSent,
    'total_external_sessions' => count($sessions),
    'message' => "$alertsSent email(s) de résumé envoyé(s) pour " . count($newSessions) . " nouvelle(s) session(s).",
    'debug' => $debugInfo,
    'timestamp' => date('Y-m-d H:i:s'),
    'protection' => '30 minutes entre les vérifications'
]);
?>
