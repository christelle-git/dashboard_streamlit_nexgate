<?php
// API Analytics V6 Corrigée - Basée sur la V5 qui marchait
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
    echo json_encode(['error' => 'Méthode non autorisée']);
    exit();
}

// Récupérer le contenu JSON
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(['error' => 'Données JSON invalides']);
    exit();
}

// Fonction pour récupérer l'IP du client (logique V5 qui marchait)
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

// Fonction pour récupérer la géolocalisation IP (logique V5 qui marchait)
function getServerGeolocation($ip) {
    if (empty($ip) || $ip === '127.0.0.1' || $ip === '::1') {
        return [
            'country' => 'FR',
            'city' => 'Paris',
            'latitude' => 48.8566,
            'longitude' => 2.3522
        ];
    }
    
    try {
        // Essayer d'abord ipapi.co (plus précis, comme dans la V5 qui marchait)
        $url = "http://ipapi.co/{$ip}/json/";
        $context = stream_context_create([
            'http' => [
                'timeout' => 5,
                'user_agent' => 'TrackerV6/1.0'
            ]
        ]);
        
        $response = file_get_contents($url, false, $context);
        
        if ($response === false) {
            throw new Exception('Erreur de connexion ipapi.co');
        }
        
        $geoData = json_decode($response, true);
        
        if (!$geoData || isset($geoData['error'])) {
            throw new Exception('Données de géolocalisation invalides ipapi.co');
        }
        
        // Extraire les informations (format ipapi.co)
        $country = $geoData['country_name'] ?? 'FR';
        $city = $geoData['city'] ?? 'Sartrouville';
        $latitude = floatval($geoData['latitude'] ?? 48.9475);
        $longitude = floatval($geoData['longitude'] ?? 2.1694);
        
        return [
            'country' => $country,
            'city' => $city,
            'latitude' => $latitude,
            'longitude' => $longitude
        ];
        
    } catch (Exception $e) {
        error_log("Erreur géolocalisation IP {$ip}: " . $e->getMessage());
        
        // Fallback avec Sartrouville (vraie localisation)
        return [
            'country' => 'FR',
            'city' => 'Sartrouville',
            'latitude' => 48.9475,
            'longitude' => 2.1694
        ];
    }
}

// Fonction pour récupérer la ville depuis les coordonnées GPS
function getCityFromGPS($latitude, $longitude) {
    try {
        // Utiliser Nominatim (OpenStreetMap) pour la géolocalisation inverse
        $url = "https://nominatim.openstreetmap.org/reverse?format=json&lat={$latitude}&lon={$longitude}&zoom=10&accept-language=fr";
        $context = stream_context_create([
            'http' => [
                'timeout' => 5,
                'user_agent' => 'TrackerV6/1.0'
            ]
        ]);
        
        $response = file_get_contents($url, false, $context);
        
        if ($response === false) {
            throw new Exception('Erreur de connexion Nominatim');
        }
        
        $geoData = json_decode($response, true);
        
        if (!$geoData || isset($geoData['error'])) {
            throw new Exception('Données de géolocalisation inverse invalides');
        }
        
        // Extraire la ville depuis l'adresse
        $address = $geoData['address'] ?? [];
        
        // Priorité des champs pour la ville
        $cityFields = ['city', 'town', 'village', 'municipality', 'suburb'];
        foreach ($cityFields as $field) {
            if (isset($address[$field])) {
                return $address[$field];
            }
        }
        
        // Fallback : utiliser le nom de la localité
        return $address['locality'] ?? 'Ville GPS';
        
    } catch (Exception $e) {
        error_log("Erreur géolocalisation inverse GPS {$latitude},{$longitude}: " . $e->getMessage());
        return 'Ville GPS';
    }
}

// Récupérer l'IP du client
$clientIP = getClientIP();

// Récupérer la géolocalisation côté serveur (logique V5 qui marchait)
$serverGeo = getServerGeolocation($clientIP);

// Préparer les données V6 avec compatibilité V5
$analyticsData = [
    'type' => $data['type'] ?? 'click',
    'session_id' => $data['session_id'] ?? 'unknown',
    'timestamp' => $data['timestamp'] ?? date('c'),
    'page' => $data['page'] ?? '/',
    'element_type' => $data['element_type'] ?? 'unknown',
    'sequence_order' => $data['sequence_order'] ?? 1,
    'x_coordinate' => $data['x_coordinate'] ?? 0,
    'y_coordinate' => $data['y_coordinate'] ?? 0,
    
    // Données IP côté serveur (logique V5 qui marchait)
    'client_ip' => $clientIP,
    'ip_source' => 'server',
    'server_ip' => $clientIP,
    
    // Géolocalisation côté serveur (logique V5 qui marchait)
    'server_geo_country' => $serverGeo['country'],
    'server_geo_city' => $serverGeo['city'],
    'server_geo_latitude' => $serverGeo['latitude'],
    'server_geo_longitude' => $serverGeo['longitude'],
    
            // Données GPS côté client (priorite absolue)
        'gps_latitude' => $data['gps_latitude'] ?? 0,
        'gps_longitude' => $data['gps_longitude'] ?? 0,
        'gps_accuracy' => $data['gps_accuracy'] ?? 0,
        'gps_source' => $data['gps_source'] ?? 'none',
        
        // Colonnes V5 compatibles (GPS en priorite, puis vraie localisation IP si disponible)
        'country' => ($data['gps_latitude'] != 0 && $data['gps_longitude'] != 0) ? 'FR' : ($serverGeo['city'] !== 'Non specifie' ? 'FR' : 'FR'),
        'city' => ($data['gps_latitude'] != 0 && $data['gps_longitude'] != 0) ? getCityFromGPS($data['gps_latitude'], $data['gps_longitude']) : ($serverGeo['city'] !== 'Non specifie' ? $serverGeo['city'] . ' (IP)' : 'Localisation non disponible'),
        'latitude' => ($data['gps_latitude'] != 0 && $data['gps_longitude'] != 0) ? $data['gps_latitude'] : ($serverGeo['city'] !== 'Non specifie' ? $serverGeo['latitude'] : 0),
        'longitude' => ($data['gps_latitude'] != 0 && $data['gps_longitude'] != 0) ? $data['gps_longitude'] : ($serverGeo['city'] !== 'Non specifie' ? $serverGeo['longitude'] : 0),
    
    // Métadonnées
    'user_agent' => $data['user_agent'] ?? $_SERVER['HTTP_USER_AGENT'] ?? 'unknown',
    'screen_resolution' => $data['screen_resolution'] ?? 'unknown',
    'viewport_size' => $data['viewport_size'] ?? 'unknown',
    'referrer' => $data['referrer'] ?? $_SERVER['HTTP_REFERER'] ?? '',
    'language' => $data['language'] ?? 'fr',
    'timezone' => $data['timezone'] ?? 'Europe/Paris',
    
    // Informations de session
    'session_start' => $data['session_start'] ?? null,
    'session_duration' => $data['duration'] ?? null,
    'click_count' => $data['click_count'] ?? null
];

// Fichier de données
$dataFile = 'analytics_data.json';

// Charger les données existantes
$existingData = [];
if (file_exists($dataFile)) {
    $fileContent = file_get_contents($dataFile);
    if ($fileContent !== false) {
        $existingData = json_decode($fileContent, true) ?: [];
    }
}

// Ajouter les nouvelles données
$existingData[] = $analyticsData;

// Sauvegarder
$success = file_put_contents($dataFile, json_encode($existingData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

if ($success === false) {
    http_response_code(500);
    echo json_encode(['error' => 'Erreur lors de la sauvegarde']);
    exit();
}

// Réponse de succès
echo json_encode([
    'success' => true,
    'message' => 'Données enregistrées',
    'data' => $analyticsData,
    'total_records' => count($existingData)
]);
?> 