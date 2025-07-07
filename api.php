<?php
// API Analytics pour site web
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Gérer les requêtes OPTIONS (preflight CORS)
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
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
    'session_id' => $data['session_id']
]);
?>