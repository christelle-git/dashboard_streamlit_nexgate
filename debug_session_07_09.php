<?php
// Script de debug pour la session du 07/09
header('Content-Type: text/plain; charset=utf-8');

echo "=== DEBUG SESSION 07/09 ===\n\n";

// Récupérer les données
$data = json_decode(file_get_contents('https://christellelusso.nexgate.ch/analytics_data.json'), true);

if (!$data) {
    echo "❌ Erreur : Impossible de récupérer les données\n";
    exit;
}

echo "📊 Total d'événements : " . count($data) . "\n\n";

// Filtrer les événements du 07/09
$events_07_09 = array_filter($data, function($event) {
    return isset($event['timestamp']) && strpos($event['timestamp'], '2025-09-07') === 0;
});

echo "📅 Événements du 07/09 : " . count($events_07_09) . "\n\n";

// Grouper par session_id
$sessions = [];
foreach ($events_07_09 as $event) {
    $sessionId = $event['session_id'] ?? 'unknown';
    if (!isset($sessions[$sessionId])) {
        $sessions[$sessionId] = [
            'session_id' => $sessionId,
            'events' => [],
            'types' => [],
            'cities' => [],
            'countries' => [],
            'latitudes' => [],
            'longitudes' => [],
            'click_count' => 0,
            'session_duration' => 0
        ];
    }
    
    $sessions[$sessionId]['events'][] = $event;
    $sessions[$sessionId]['types'][] = $event['type'] ?? 'unknown';
    
    if (isset($event['city'])) {
        $sessions[$sessionId]['cities'][] = $event['city'];
    }
    if (isset($event['country'])) {
        $sessions[$sessionId]['countries'][] = $event['country'];
    }
    if (isset($event['latitude'])) {
        $sessions[$sessionId]['latitudes'][] = $event['latitude'];
    }
    if (isset($event['longitude'])) {
        $sessions[$sessionId]['longitudes'][] = $event['longitude'];
    }
    if (isset($event['click_count'])) {
        $sessions[$sessionId]['click_count'] = max($sessions[$sessionId]['click_count'], $event['click_count']);
    }
    if (isset($event['session_duration'])) {
        $sessions[$sessionId]['session_duration'] = max($sessions[$sessionId]['session_duration'], $event['session_duration']);
    }
}

echo "🔍 Sessions trouvées : " . count($sessions) . "\n\n";

foreach ($sessions as $sessionId => $session) {
    echo "=== SESSION: $sessionId ===\n";
    echo "Types d'événements : " . implode(', ', array_unique($session['types'])) . "\n";
    echo "Villes : " . implode(', ', array_unique($session['cities'])) . "\n";
    echo "Pays : " . implode(', ', array_unique($session['countries'])) . "\n";
    echo "Latitudes : " . implode(', ', array_unique($session['latitudes'])) . "\n";
    echo "Longitudes : " . implode(', ', array_unique($session['longitudes'])) . "\n";
    echo "Nombre de clics : " . $session['click_count'] . "\n";
    echo "Durée : " . $session['session_duration'] . "ms\n";
    echo "Nombre d'événements : " . count($session['events']) . "\n";
    
    // Vérifier si cette session sera visible sur la carte
    $lat = !empty($session['latitudes']) ? max($session['latitudes']) : 0;
    $lng = !empty($session['longitudes']) ? max($session['longitudes']) : 0;
    $city = !empty($session['cities']) ? $session['cities'][0] : 'Unknown';
    $country = !empty($session['countries']) ? $session['countries'][0] : 'Unknown';
    
    echo "Coordonnées finales : [$lat, $lng]\n";
    echo "Ville finale : $city\n";
    echo "Pays final : $country\n";
    
    if ($lat != 0 && $lng != 0) {
        echo "✅ Cette session DEVRAIT apparaître sur la carte\n";
    } else {
        echo "❌ Cette session n'apparaîtra PAS sur la carte (pas de coordonnées)\n";
    }
    
    echo "\n";
}

echo "=== FIN DU DEBUG ===\n";
?>
