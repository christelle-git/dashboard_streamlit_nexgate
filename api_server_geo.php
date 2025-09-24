<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-Tracker-Agent');
header('Access-Control-Allow-Credentials: true');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Méthode non autorisée']);
    exit();
}

// Récupère l'IP du client
function getClientIP() {
    $ipKeys = ['HTTP_CLIENT_IP', 'HTTP_X_FORWARDED_FOR', 'HTTP_X_FORWARDED', 'HTTP_X_CLUSTER_CLIENT_IP', 'HTTP_FORWARDED_FOR', 'HTTP_FORWARDED', 'REMOTE_ADDR'];
    
    foreach ($ipKeys as $key) {
        if (array_key_exists($key, $_SERVER) === true) {
            foreach (explode(',', $_SERVER[$key]) as $ip) {
                $ip = trim($ip);
                if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE) !== false) {
                    return $ip;
                }
            }
        }
    }
    
    return $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
}

// Fonction de géolocalisation côté serveur
function getGeolocation($ip) {
    // Si c'est une IP locale, retourne des valeurs par défaut
    if ($ip === '127.0.0.1' || $ip === '::1' || strpos($ip, '192.168.') === 0 || strpos($ip, '10.') === 0) {
        return [
            'country' => 'France',
            'city' => 'Non spécifié',
            'latitude' => 48.8566,
            'longitude' => 2.3522
        ];
    }
    
    try {
        // Utilise ipinfo.io pour la géolocalisation
        $context = stream_context_create([
            'http' => [
                'timeout' => 5,
                'user_agent' => 'Mozilla/5.0 (compatible; AnalyticsTracker/1.0)'
            ]
        ]);
        
        $response = @file_get_contents("https://ipinfo.io/{$ip}/json", false, $context);
        
        if ($response !== false) {
            $data = json_decode($response, true);
            
            if ($data && isset($data['country']) && isset($data['city'])) {
                // Parse les coordonnées si disponibles
                $lat = 0;
                $lon = 0;
                if (isset($data['loc'])) {
                    $coords = explode(',', $data['loc']);
                    if (count($coords) === 2) {
                        $lat = floatval($coords[0]);
                        $lon = floatval($coords[1]);
                    }
                }
                
                return [
                    'country' => $data['country'],
                    'city' => $data['city'],
                    'latitude' => $lat,
                    'longitude' => $lon
                ];
            }
        }
    } catch (Exception $e) {
        error_log("Erreur géolocalisation: " . $e->getMessage());
    }
    
    // Fallback si la géolocalisation échoue
    return [
        'country' => 'Non spécifié',
        'city' => 'Non spécifié',
        'latitude' => 0,
        'longitude' => 0
    ];
}

// Récupère les données JSON
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(['error' => 'Données JSON invalides']);
    exit();
}

// Récupère l'IP du client
$clientIP = getClientIP();

// Récupère la géolocalisation
$geoData = getGeolocation($clientIP);

// Ajoute les données de géolocalisation et l'IP
$data['client_ip'] = $clientIP;
$data['country'] = $geoData['country'];
$data['city'] = $geoData['city'];
$data['latitude'] = $geoData['latitude'];
$data['longitude'] = $geoData['longitude'];

// Ajoute un timestamp si pas présent
if (!isset($data['timestamp'])) {
    $data['timestamp'] = date('Y-m-d H:i:s');
}

// Charge les données existantes
$jsonFile = 'analytics_data.json';
$existingData = [];

if (file_exists($jsonFile)) {
    $existingContent = file_get_contents($jsonFile);
    if ($existingContent !== false) {
        $existingData = json_decode($existingContent, true) ?? [];
    }
}

// Ajoute les nouvelles données
$existingData[] = $data;

// Sauvegarde les données
$result = file_put_contents($jsonFile, json_encode($existingData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

if ($result === false) {
    http_response_code(500);
    echo json_encode(['error' => 'Erreur lors de la sauvegarde']);
    exit();
}

// Réponse de succès
echo json_encode([
    'success' => true,
    'message' => 'Données enregistrées avec succès',
    'session_id' => $data['session_id'] ?? null,
    'geo_data' => $geoData,
    'total_records' => count($existingData)
]);
?> 