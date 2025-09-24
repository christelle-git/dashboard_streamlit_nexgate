<?php
// Script pour vérifier les nouvelles sessions (session_start) et envoyer UNE alerte récapitulative
header('Content-Type: application/json');

// Configuration
$DATA_URL = 'https://christellelusso.nexgate.ch/analytics_data.json';
$FIXED_IP = '82.66.151.2';
// Cooldown par défaut 10 min, mais personnalisable par ?cooldown=SECONDES (borné 60..3600)
$COOLDOWN_SECONDS = 600; // 10 minutes par défaut (sécurité SEO)
if (isset($_GET['cooldown'])) {
    $cd = intval($_GET['cooldown']);
    if ($cd >= 60 && $cd <= 3600) { $COOLDOWN_SECONDS = $cd; }
}
// Fenêtre temporelle personnalisable ?window_hours=H (bornée 1..48)
$WINDOW_HOURS = 24; // fenêtre d'observation
if (isset($_GET['window_hours'])) {
    $wh = intval($_GET['window_hours']);
    if ($wh >= 1 && $wh <= 48) { $WINDOW_HOURS = $wh; }
}
// Mode test: inclure l'IP fixe si ?include_my_ip=1
$INCLUDE_FIXED_IP_FOR_TEST = isset($_GET['include_my_ip']) && $_GET['include_my_ip'] == '1';

// Fichiers d'état
$notifiedFile = 'notified_sessions.json';
$lastCheckFile = 'last_check.json';
$lockFile = 'alerts.lock';

// Verrouillage simple pour éviter les appels concurrents
$lockHandle = fopen($lockFile, 'c+');
if ($lockHandle !== false && !flock($lockHandle, LOCK_EX | LOCK_NB)) {
    echo json_encode(['success' => false, 'message' => 'Vérification déjà en cours']);
    exit;
}

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
$data = json_decode(file_get_contents($DATA_URL), true);

if (!$data) {
    http_response_code(500);
    echo json_encode(['error' => 'Impossible de récupérer les données']);
    exit;
}

// Filtrer: seulement session_start; exclure IP fixe sauf en mode test
$externalSessions = array_filter($data, function($event) use ($FIXED_IP, $INCLUDE_FIXED_IP_FOR_TEST) {
    if (!isset($event['type']) || $event['type'] !== 'session_start') return false;
    if (!isset($event['client_ip'])) return false;
    if ($INCLUDE_FIXED_IP_FOR_TEST) return true; // autoriser pour les tests manuels
    return $event['client_ip'] !== $FIXED_IP;
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
$yesterdayTs = time() - ($WINDOW_HOURS * 3600);

foreach ($sessions as $sessionId => $session) {
    $sessionTs = strtotime($session['timestamp']);
    if ($sessionTs !== false && $sessionTs >= $yesterdayTs && !in_array($sessionId, $notifiedSessions)) {
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
    $debugInfo[] = "CURL Result: " . substr((string)$result, 0, 100);
    
    if ($httpCode === 200) {
        $alertsSent = 1; // Un seul email envoyé
        $debugInfo[] = "Email envoyé avec succès";
    } else {
        $debugInfo[] = "Erreur envoi email: " . $httpCode;
    }
} else {
    $debugInfo[] = "Aucune nouvelle session détectée";
}

if ($lockHandle) { flock($lockHandle, LOCK_UN); fclose($lockHandle); }

echo json_encode([
    'success' => true,
    'new_sessions' => count($newSessions),
    'alerts_sent' => $alertsSent,
    'total_external_sessions' => count($sessions),
    'message' => "$alertsSent email(s) de résumé envoyé(s) pour " . count($newSessions) . " nouvelle(s) session(s).",
    'debug' => $debugInfo,
    'timestamp' => date('Y-m-d H:i:s'),
    'cooldown_minutes' => $COOLDOWN_SECONDS / 60,
    'include_fixed_ip_for_test' => $INCLUDE_FIXED_IP_FOR_TEST
]);
?>
