<?php
/**
 * Dashboard de Tracking Analytics - Version PHP
 * Compatible avec l'hébergeur Nexgate (Web-FTP uniquement)
 * 
 * @author Christelle Lusso
 * @version 1.0
 * @date 2025-09-01
 */

// Configuration
$ANALYTICS_DATA_URL = 'https://christellelusso.nexgate.ch/analytics_data.json';
$CACHE_DURATION = 300; // 5 minutes
$CACHE_FILE = 'analytics_cache.json';

// Fonction pour récupérer les données
function getAnalyticsData() {
    global $ANALYTICS_DATA_URL, $CACHE_DURATION, $CACHE_FILE;
    
    // Vérifier le cache
    if (file_exists($CACHE_FILE) && (time() - filemtime($CACHE_FILE)) < $CACHE_DURATION) {
        $data = json_decode(file_get_contents($CACHE_FILE), true);
        if ($data) return $data;
    }
    
    // Récupérer les données depuis l'API
    $context = stream_context_create([
        'http' => [
            'timeout' => 10,
            'user_agent' => 'Dashboard PHP/1.0'
        ]
    ]);
    
    $json = @file_get_contents($ANALYTICS_DATA_URL, false, $context);
    if ($json === false) {
        return ['error' => 'Impossible de récupérer les données'];
    }
    
    $data = json_decode($json, true);
    if (!$data) {
        return ['error' => 'Données JSON invalides'];
    }
    
    // Sauvegarder en cache
    file_put_contents($CACHE_FILE, $json);
    
    return $data;
}

// Fonction pour traiter les données
function processData($data) {
    if (isset($data['error'])) {
        return $data;
    }
    
    $sessions = [];
    $clicks = [];
    $sessionEnds = [];
    
    // Séparer les types d'événements
    foreach ($data as $entry) {
        switch ($entry['type']) {
            case 'session_start':
                $sessions[] = $entry;
                break;
            case 'click':
                $clicks[] = $entry;
                break;
            case 'session_end':
                $sessionEnds[] = $entry;
                break;
        }
    }
    
    // Créer un mapping des sessions
    $sessionMap = [];
    foreach ($sessions as $session) {
        $sessionMap[$session['session_id']] = $session;
    }
    
    // Ajouter les sessions de fin
    foreach ($sessionEnds as $sessionEnd) {
        $sessionId = $sessionEnd['session_id'];
        if (!isset($sessionMap[$sessionId])) {
            // Créer une session à partir de session_end
            $sessionMap[$sessionId] = [
                'session_id' => $sessionId,
                'timestamp' => $sessionEnd['timestamp'],
                'client_ip' => $sessionEnd['client_ip'] ?? 'Non spécifié',
                'country' => $sessionEnd['country'] ?? 'Non spécifié',
                'city' => $sessionEnd['city'] ?? 'Non spécifié',
                'latitude' => $sessionEnd['latitude'] ?? 0,
                'longitude' => $sessionEnd['longitude'] ?? 0,
                'session_duration' => $sessionEnd['session_duration'] ?? 0,
                'click_count' => $sessionEnd['click_count'] ?? 0,
                'is_from_session_end' => true
            ];
        } else {
            // Mettre à jour la session existante
            $sessionMap[$sessionId]['session_duration'] = $sessionEnd['session_duration'] ?? 0;
            $sessionMap[$sessionId]['click_count'] = $sessionEnd['click_count'] ?? 0;
        }
    }
    
    // Calculer les statistiques
    $stats = [
        'total_sessions' => count($sessionMap),
        'total_clicks' => count($clicks),
        'sessions_with_clicks' => count(array_filter($sessionMap, function($s) { return ($s['click_count'] ?? 0) > 0; })),
        'sessions_without_clicks' => count(array_filter($sessionMap, function($s) { return ($s['click_count'] ?? 0) == 0; })),
        'average_duration' => 0,
        'countries' => [],
        'cities' => []
    ];
    
    // Calculer la durée moyenne
    $totalDuration = 0;
    $sessionsWithDuration = 0;
    foreach ($sessionMap as $session) {
        if (isset($session['session_duration']) && $session['session_duration'] > 0) {
            $totalDuration += $session['session_duration'];
            $sessionsWithDuration++;
        }
    }
    if ($sessionsWithDuration > 0) {
        $stats['average_duration'] = round($totalDuration / $sessionsWithDuration / 1000, 2); // en secondes
    }
    
    // Compter les pays et villes
    foreach ($sessionMap as $session) {
        $country = $session['country'] ?? 'Non spécifié';
        $city = $session['city'] ?? 'Non spécifié';
        
        $stats['countries'][$country] = ($stats['countries'][$country] ?? 0) + 1;
        $stats['cities'][$city] = ($stats['cities'][$city] ?? 0) + 1;
    }
    
    // Trier les sessions par date (plus récentes en premier)
    uasort($sessionMap, function($a, $b) {
        return strtotime($b['timestamp']) - strtotime($a['timestamp']);
    });
    
    return [
        'sessions' => $sessionMap,
        'clicks' => $clicks,
        'stats' => $stats,
        'last_update' => date('Y-m-d H:i:s')
    ];
}

// Récupérer et traiter les données
$analyticsData = getAnalyticsData();
$processedData = processData($analyticsData);
?>

<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Analytics - Tracking</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Leaflet pour les cartes -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <style>
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stat-label {
            font-size: 1rem;
            opacity: 0.9;
        }
        .session-card {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            transition: transform 0.2s;
        }
        .session-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .country-badge {
            background: #007bff;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            margin: 2px;
            display: inline-block;
        }
        .map-container {
            height: 400px;
            border-radius: 10px;
            overflow: hidden;
        }
        .refresh-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <!-- Header -->
        <div class="row bg-primary text-white py-3 mb-4">
            <div class="col">
                <h1 class="h2 mb-0">📊 Dashboard Analytics - Tracking</h1>
                <p class="mb-0">Dernière mise à jour : <?php echo $processedData['last_update']; ?></p>
            </div>
        </div>

        <?php if (isset($processedData['error'])): ?>
            <div class="alert alert-danger">
                <h4>❌ Erreur</h4>
                <p><?php echo htmlspecialchars($processedData['error']); ?></p>
            </div>
        <?php else: ?>
            <!-- Statistiques globales -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number"><?php echo $processedData['stats']['total_sessions']; ?></div>
                        <div class="stat-label">Sessions Total</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number"><?php echo $processedData['stats']['total_clicks']; ?></div>
                        <div class="stat-label">Clics Total</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number"><?php echo $processedData['stats']['sessions_with_clicks']; ?></div>
                        <div class="stat-label">Sessions avec Clics</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number"><?php echo $processedData['stats']['average_duration']; ?>s</div>
                        <div class="stat-label">Durée Moyenne</div>
                    </div>
                </div>
            </div>

            <!-- Cartes et graphiques -->
            <div class="row mb-4">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h5>🗺️ Géolocalisation des Sessions</h5>
                        </div>
                        <div class="card-body">
                            <div id="map" class="map-container"></div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h5>🌍 Répartition par Pays</h5>
                        </div>
                        <div class="card-body">
                            <canvas id="countryChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Liste des sessions -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5>📋 Détails des Sessions</h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Date/Heure</th>
                                            <th>IP</th>
                                            <th>Pays</th>
                                            <th>Ville</th>
                                            <th>Durée</th>
                                            <th>Clics</th>
                                            <th>Type</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <?php foreach (array_slice($processedData['sessions'], 0, 50) as $session): ?>
                                            <tr>
                                                <td><?php echo date('d/m/Y H:i', strtotime($session['timestamp'])); ?></td>
                                                <td><?php echo htmlspecialchars($session['client_ip']); ?></td>
                                                <td><?php echo htmlspecialchars($session['country']); ?></td>
                                                <td><?php echo htmlspecialchars($session['city']); ?></td>
                                                <td><?php echo isset($session['session_duration']) ? round($session['session_duration']/1000, 1) . 's' : '-'; ?></td>
                                                <td><?php echo $session['click_count'] ?? 0; ?></td>
                                                <td>
                                                    <?php if (isset($session['is_from_session_end'])): ?>
                                                        <span class="badge bg-warning">Session End</span>
                                                    <?php else: ?>
                                                        <span class="badge bg-success">Session Start</span>
                                                    <?php endif; ?>
                                                </td>
                                            </tr>
                                        <?php endforeach; ?>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        <?php endif; ?>
    </div>

    <!-- Bouton de rafraîchissement -->
    <button class="btn btn-primary refresh-btn" onclick="location.reload()">
        🔄 Actualiser
    </button>

    <!-- Scripts -->
    <script>
        // Données pour les graphiques
        const sessions = <?php echo json_encode(array_values($processedData['sessions'])); ?>;
        const stats = <?php echo json_encode($processedData['stats']); ?>;

        // Initialiser la carte
        const map = L.map('map').setView([46.0, 2.0], 6);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

        // Ajouter les marqueurs des sessions
        sessions.forEach(session => {
            if (session.latitude && session.longitude && session.latitude != 0 && session.longitude != 0) {
                const marker = L.marker([session.latitude, session.longitude])
                    .addTo(map)
                    .bindPopup(`
                        <strong>Session ${session.session_id}</strong><br>
                        Date: ${new Date(session.timestamp).toLocaleString()}<br>
                        Pays: ${session.country}<br>
                        Ville: ${session.city}<br>
                        Clics: ${session.click_count || 0}
                    `);
            }
        });

        // Graphique des pays
        const countryCtx = document.getElementById('countryChart').getContext('2d');
        const countryData = Object.entries(stats.countries).slice(0, 10);
        
        new Chart(countryCtx, {
            type: 'doughnut',
            data: {
                labels: countryData.map(([country]) => country),
                datasets: [{
                    data: countryData.map(([, count]) => count),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF',
                        '#4BC0C0', '#FF6384'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Auto-refresh toutes les 5 minutes
        setTimeout(() => {
            location.reload();
        }, 300000);
    </script>
</body>
</html>
