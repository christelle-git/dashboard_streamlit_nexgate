<?php
// Script pour envoyer une alerte par mail lors d'une nouvelle session
header('Content-Type: application/json');

// Configuration email
$to = 'christelle.lusso@gmail.com'; // Remplacez par votre email
$subject = '🚨 Nouvelle session détectée sur votre site';
$from = 'noreply@christellelusso.nexgate.ch';

// Récupérer les données de la session
$sessionData = json_decode(file_get_contents('php://input'), true);

if (!$sessionData) {
    http_response_code(400);
    echo json_encode(['error' => 'Données de session manquantes']);
    exit;
}

// Vérifier si c'est un résumé de sessions
if (isset($sessionData['type']) && $sessionData['type'] === 'summary') {
    // Envoyer un email de résumé
    $sessionCount = $sessionData['count'];
    $sessions = $sessionData['sessions'];
    
    if ($sessionCount === 0) {
        echo json_encode(['message' => 'Aucune nouvelle session']);
        exit;
    }
    
    // Préparer le contenu de l'email de résumé
    $message = "
    <html>
    <head>
        <title>Résumé des nouvelles sessions</title>
    </head>
    <body>
        <h2>📊 Résumé des nouvelles sessions détectées</h2>
        
        <p><strong>Nombre de nouvelles sessions :</strong> $sessionCount</p>
        <p><strong>Date de vérification :</strong> " . htmlspecialchars($sessionData['timestamp']) . "</p>
        
        <h3>Détails des sessions :</h3>
        <ul>";
    
    foreach ($sessions as $session) {
        $message .= "
        <li>
            <strong>Session :</strong> " . htmlspecialchars($session['session_id']) . "<br>
            <strong>Date :</strong> " . htmlspecialchars($session['timestamp']) . "<br>
            <strong>Pays :</strong> " . htmlspecialchars($session['country']) . "<br>
            <strong>Ville :</strong> " . htmlspecialchars($session['city']) . "<br>
            <strong>IP :</strong> " . htmlspecialchars($session['client_ip']) . "<br>
            <strong>Coordonnées :</strong> " . htmlspecialchars($session['latitude']) . ", " . htmlspecialchars($session['longitude']) . "<br>
            <hr>
        </li>";
    }
    
    $message .= "
        </ul>
        
        <p><a href='https://christellelusso.nexgate.ch/dashboard_php.php'>Voir le dashboard</a></p>
        
        <hr>
        <p><small>Email automatique envoyé par votre système de tracking</small></p>
    </body>
    </html>";
    
    $subject = "📊 $sessionCount nouvelle(s) session(s) détectée(s) sur votre site";
    
} else {
    // Vérifier si c'est une nouvelle session (pas de notre IP)
    if ($sessionData['client_ip'] === '82.66.151.2') {
        echo json_encode(['message' => 'Session de votre IP ignorée']);
        exit;
    }
    
    // Préparer le contenu de l'email pour une session unique
    $message = "
    <html>
    <head>
        <title>Nouvelle session détectée</title>
    </head>
    <body>
        <h2>🚨 Nouvelle session détectée sur votre site</h2>
        
        <h3>Informations de la session :</h3>
        <ul>
            <li><strong>ID de session :</strong> " . htmlspecialchars($sessionData['session_id']) . "</li>
            <li><strong>Date et heure :</strong> " . htmlspecialchars($sessionData['timestamp']) . "</li>
            <li><strong>Pays :</strong> " . htmlspecialchars($sessionData['country']) . "</li>
            <li><strong>Ville :</strong> " . htmlspecialchars($sessionData['city']) . "</li>
            <li><strong>IP :</strong> " . htmlspecialchars($sessionData['client_ip']) . "</li>
            <li><strong>User Agent :</strong> " . htmlspecialchars($sessionData['user_agent']) . "</li>
        </ul>
        
        <h3>Coordonnées GPS :</h3>
        <ul>
            <li><strong>Latitude :</strong> " . htmlspecialchars($sessionData['latitude']) . "</li>
            <li><strong>Longitude :</strong> " . htmlspecialchars($sessionData['longitude']) . "</li>
        </ul>
        
        <p><a href='https://christellelusso.nexgate.ch/dashboard_php.php'>Voir le dashboard</a></p>
        
        <hr>
        <p><small>Email automatique envoyé par votre système de tracking</small></p>
    </body>
    </html>";
    
    $subject = "🚨 Nouvelle session détectée sur votre site";
}

// Headers pour l'email HTML
$headers = "MIME-Version: 1.0" . "\r\n";
$headers .= "Content-type:text/html;charset=UTF-8" . "\r\n";
$headers .= "From: " . $from . "\r\n";
$headers .= "Reply-To: " . $from . "\r\n";

// Envoyer l'email
if (mail($to, $subject, $message, $headers)) {
    echo json_encode(['success' => true, 'message' => 'Alerte envoyée avec succès']);
} else {
    http_response_code(500);
    echo json_encode(['error' => 'Erreur lors de l\'envoi de l\'alerte']);
}
?>
