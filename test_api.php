<?php
// Script de test pour l'API analytics
echo "=== Test de l'API Analytics ===\n";

// Test 1: Vérifier si le fichier api.php existe
if (file_exists('api.php')) {
    echo "✅ api.php existe\n";
} else {
    echo "❌ api.php n'existe pas\n";
}

// Test 2: Vérifier si le fichier analytics_data.json existe
if (file_exists('analytics_data.json')) {
    echo "✅ analytics_data.json existe\n";
    $content = file_get_contents('analytics_data.json');
    $data = json_decode($content, true);
    echo "📊 Nombre d'entrées: " . count($data) . "\n";
} else {
    echo "❌ analytics_data.json n'existe pas\n";
}

// Test 3: Simuler une requête POST vers l'API
echo "\n=== Test de requête POST ===\n";

$testData = [
    'type' => 'test_event',
    'session_id' => 'test_session_' . time(),
    'timestamp' => date('Y-m-d H:i:s'),
    'test' => true
];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, 'https://christellelusso.nexgate.ch/api.php');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($testData));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'Content-Length: ' . strlen(json_encode($testData))
]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

echo "Code HTTP: $httpCode\n";
echo "Réponse: $response\n";
if ($error) {
    echo "Erreur cURL: $error\n";
}

// Test 4: Vérifier le contenu après la requête
if (file_exists('analytics_data.json')) {
    $content = file_get_contents('analytics_data.json');
    $data = json_decode($content, true);
    echo "📊 Nombre d'entrées après test: " . count($data) . "\n";
    
    if (count($data) > 0) {
        $lastEntry = end($data);
        echo "Dernière entrée: " . json_encode($lastEntry, JSON_PRETTY_PRINT) . "\n";
    }
}

echo "\n=== Test terminé ===\n";
?> 