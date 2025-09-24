<?php
// API Analytics V6 - Version avec IP et GPS séparés
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

// Récupérer l'IP du client côté serveur (plus fiable)
$serverIP = $_SERVER['REMOTE_ADDR'] ?? 'unknown';

// Fonction pour récupérer la géolocalisation par IP côté serveur
function getServerGeolocation($ip) {
    // Debug: log l'IP reçue
    error_log("DEBUG V6: getServerGeolocation called with IP: " . $ip);
    
    // Ignore les IPs locales
    if (in_array($ip, ['127.0.0.1', '::1', 'unknown', 'localhost'])) {
        error_log("DEBUG V6: IP locale détectée, retourne valeurs par défaut");
        return [
            'country' => 'Non spécifié',
            'city' => 'Non spécifié',
            'latitude' => 0,
            'longitude' => 0,
            'source' => 'server_default'
        ];
    }
    
    try {
        // Utilise ipinfo.io côté serveur (plus fiable)
        $url = "https://ipinfo.io/{$ip}/json";
        error_log("DEBUG V6: Appel de l'URL: " . $url);
        
        $context = stream_context_create([
            'http' => [
                'timeout' => 5,
                'user_agent' => 'Mozilla/5.0 (compatible; AnalyticsTracker/1.0)'
            ]
        ]);
        
        $response = @file_get_contents($url, false, $context);
        error_log("DEBUG V6: Réponse reçue: " . substr($response, 0, 200));
        
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
                    'longitude' => $longitude,
                    'source' => 'server_ipinfo'
                ];
                
                error_log("DEBUG V6: Géolocalisation serveur réussie: " . json_encode($result));
                return $result;
            } else {
                error_log("DEBUG V6: Erreur dans la réponse JSON ou données invalides");
            }
        } else {
            error_log("DEBUG V6: Aucune réponse reçue de ipinfo.io");
        }
    } catch (Exception $e) {
        error_log("DEBUG V6: Exception dans getServerGeolocation: " . $e->getMessage());
    }
    
    error_log("DEBUG V6: Retourne valeurs par défaut");
    return [
        'country' => 'Non spécifié',
        'city' => 'Non spécifié',
        'latitude' => 0,
        'longitude' => 0,
        'source' => 'server_fallback'
    ];
}

// Traitement des données avec séparation IP/GPS
$processedData = [
    'type' => $data['type'],
    'session_id' => $data['session_id'],
    'timestamp' => $data['timestamp'],
    
    // Données IP (priorité au client, fallback serveur)
    'client_ip' => $data['client_ip'] ?? $serverIP,
    'ip_source' => $data['ip_source'] ?? 'server_detected',
    'server_ip' => $serverIP,
    
    // Données GPS (uniquement du client)
    'gps_latitude' => $data['gps_latitude'] ?? 0,
    'gps_longitude' => $data['gps_longitude'] ?? 0,
    'gps_accuracy' => $data['gps_accuracy'] ?? 0,
    'gps_source' => $data['gps_source'] ?? 'none',
    
    // Données géolocalisation par IP (client + serveur)
    'geo_country' => $data['geo_country'] ?? 'Non spécifié',
    'geo_city' => $data['geo_city'] ?? 'Non spécifié',
    'geo_source' => $data['geo_source'] ?? 'default',
    
    // Géolocalisation serveur (pour comparaison)
    'server_geo_country' => 'Non spécifié',
    'server_geo_city' => 'Non spécifié',
    'server_geo_latitude' => 0,
    'server_geo_longitude' => 0,
    'server_geo_source' => 'none'
];

// Ajouter les données spécifiques selon le type
if ($data['type'] === 'click') {
    $processedData['element_type'] = $data['element_type'] ?? 'unknown';
    $processedData['page'] = $data['page'] ?? '/';
    $processedData['sequence_order'] = $data['sequence_order'] ?? 0;
    $processedData['x_coordinate'] = $data['x_coordinate'] ?? 0;
    $processedData['y_coordinate'] = $data['y_coordinate'] ?? 0;
} elseif ($data['type'] === 'session_end') {
    $processedData['total_clicks'] = $data['total_clicks'] ?? 0;
}

// Récupérer la géolocalisation serveur pour comparaison
$serverGeo = getServerGeolocation($processedData['client_ip']);
$processedData['server_geo_country'] = $serverGeo['country'];
$processedData['server_geo_city'] = $serverGeo['city'];
$processedData['server_geo_latitude'] = $serverGeo['latitude'];
$processedData['server_geo_longitude'] = $serverGeo['longitude'];
$processedData['server_geo_source'] = $serverGeo['source'];

// Ajouter des métadonnées de comparaison
$processedData['location_consistency'] = 'unknown';
if ($processedData['gps_source'] !== 'none' && $processedData['server_geo_source'] !== 'none') {
    // Comparer GPS et géolocalisation IP
    $gpsLat = $processedData['gps_latitude'];
    $gpsLon = $processedData['gps_longitude'];
    $serverLat = $processedData['server_geo_latitude'];
    $serverLon = $processedData['server_geo_longitude'];
    
    if ($gpsLat != 0 && $gpsLon != 0 && $serverLat != 0 && $serverLon != 0) {
        // Calculer la distance approximative (formule de Haversine simplifiée)
        $latDiff = abs($gpsLat - $serverLat);
        $lonDiff = abs($gpsLon - $serverLon);
        $distance = sqrt($latDiff * $latDiff + $lonDiff * $lonDiff) * 111000; // km approximatif
        
        if ($distance < 50) {
            $processedData['location_consistency'] = 'high';
        } elseif ($distance < 200) {
            $processedData['location_consistency'] = 'medium';
        } else {
            $processedData['location_consistency'] = 'low';
        }
        
        $processedData['location_distance_km'] = round($distance, 2);
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
$existingData[] = $processedData;

// Sauvegarder dans le fichier
$result = file_put_contents($dataFile, json_encode($existingData, JSON_PRETTY_PRINT));

if ($result === false) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to save data']);
    exit();
}

// Réponse de succès avec résumé
$response = [
    'success' => true,
    'message' => 'Data saved successfully',
    'summary' => [
        'ip_client' => $processedData['client_ip'],
        'ip_source' => $processedData['ip_source'],
        'gps_available' => $processedData['gps_source'] !== 'none',
        'geo_client' => $processedData['geo_city'] . ', ' . $processedData['geo_country'],
        'geo_server' => $processedData['server_geo_city'] . ', ' . $processedData['server_geo_country'],
        'location_consistency' => $processedData['location_consistency']
    ]
];

echo json_encode($response);
?> 