<?php
// API Analytics pour site web
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Credentials: true');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Gérer les requêtes OPTIONS (preflight CORS)
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Credentials: true');
    header('Access-Control-Allow-Methods: POST, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, X-Tracker-Agent');
    exit();
}

// Vérifier que c'est une requête POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit();
}

// Lire les données JSON
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON data']);
    exit();
}

// Valider les données requises
if (!isset($data['type']) || !isset($data['session_id'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing required fields']);
    exit();
}

// Ajouter un timestamp si pas présent
if (!isset($data['timestamp'])) {
    $data['timestamp'] = date('Y-m-d H:i:s');
}

// Ajouter l'IP du client
$data['client_ip'] = $_SERVER['REMOTE_ADDR'] ?? 'unknown';

// Fonction pour récupérer la géolocalisation
function getGeolocation($ip) {
    // Debug: log l'IP reçue
    error_log("DEBUG: getGeolocation called with IP: " . $ip);
    
    // Ignore les IPs locales
    if (in_array($ip, ['127.0.0.1', '::1', 'unknown', 'localhost'])) {
        error_log("DEBUG: IP locale détectée, retourne valeurs par défaut");
        return [
            'country' => 'Non spécifié',
            'city' => 'Non spécifié',
            'latitude' => 0,
            'longitude' => 0
        ];
    }
    
    try {
        // Utilise ipinfo.io côté serveur (plus fiable)
        $url = "https://ipinfo.io/{$ip}/json";
        error_log("DEBUG: Appel de l'URL: " . $url);
        
        $response = file_get_contents($url);
        error_log("DEBUG: Réponse reçue: " . substr($response, 0, 200));
        
        if ($response) {
            $geoData = json_decode($response, true);
            if ($geoData && !isset($geoData['error'])) {
                // Parse les coordonnées depuis "loc" (format: "lat,lon")
                $latitude = 0;
                $longitude = 0;
                if (isset($geoData['loc'])) {
                    $coords = explode(',', $geoData['loc']);
                    $latitude = floatval($coords[0]) ?? 0;
                    $longitude = floatval($coords[1]) ?? 0;
                }
                
                $result = [
                    'country' => $geoData['country'] ?? 'Non spécifié',
                    'city' => $geoData['city'] ?? 'Non spécifié',
                    'latitude' => $latitude,
                    'longitude' => $longitude
                ];
                
                error_log("DEBUG: Géolocalisation réussie: " . json_encode($result));
                return $result;
            } else {
                error_log("DEBUG: Erreur dans la réponse JSON ou données invalides");
            }
        } else {
            error_log("DEBUG: Aucune réponse reçue de ipinfo.io");
        }
    } catch (Exception $e) {
        error_log("DEBUG: Exception dans getGeolocation: " . $e->getMessage());
    }
    
    error_log("DEBUG: Retourne valeurs par défaut");
    return [
        'country' => 'Non spécifié',
        'city' => 'Non spécifié',
        'latitude' => 0,
        'longitude' => 0
    ];
}

// Ajouter la géolocalisation si pas déjà présente
if (!isset($data['country']) || !isset($data['city'])) {
    // Si les données de géolocalisation sont envoyées par le client, les utilise
    if (isset($data['country']) && isset($data['city'])) {
        error_log("DEBUG: Utilise les données de géolocalisation du client");
    } else {
        // Sinon, essaie de récupérer côté serveur
        error_log("DEBUG: Ajout de géolocalisation pour IP: " . $data['client_ip']);
        $geoData = getGeolocation($data['client_ip']);
        $data['country'] = $geoData['country'];
        $data['city'] = $geoData['city'];
        $data['latitude'] = $geoData['latitude'];
        $data['longitude'] = $geoData['longitude'];
        error_log("DEBUG: Géolocalisation ajoutée: " . json_encode($geoData));
    }
}

// Chemin vers le fichier de données
$dataFile = 'analytics_data.json';

// Lire les données existantes
$existingData = [];
if (file_exists($dataFile)) {
    $fileContent = file_get_contents($dataFile);
    if ($fileContent) {
        $existingData = json_decode($fileContent, true) ?? [];
    }
}

// Ajouter les nouvelles données
$existingData[] = $data;

// Sauvegarder dans le fichier
$result = file_put_contents($dataFile, json_encode($existingData, JSON_PRETTY_PRINT));

if ($result === false) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to save data']);
    exit();
}

// Réponse de succès
echo json_encode([
    'success' => true,
    'message' => 'Data saved successfully',
    'data_type' => $data['type'],
    'session_id' => $data['session_id'],
    'debug_geo' => [
        'country' => $data['country'],
        'city' => $data['city'],
        'latitude' => $data['latitude'],
        'longitude' => $data['longitude']
    ]
]);
?>