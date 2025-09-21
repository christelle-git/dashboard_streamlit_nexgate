<?php
/**
 * Dashboard de Tracking Analytics - Version PHP Améliorée
 * Compatible avec l'hébergeur Nexgate (Web-FTP uniquement)
 * 
 * @author Christelle Lusso
 * @version 2.0
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
            'user_agent' => 'Dashboard PHP/2.0'
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

// Fonction pour personnaliser l'IP fixe
function customizeIP($ip, $country, $city) {
    if ($ip === '82.66.151.2') {
        return ['country' => 'France', 'city' => 'MOI'];
    }
    return ['country' => $country, 'city' => $city];
}

// Fonction pour traiter les données
function processData($data) {
    if (isset($data['error'])) {
        return $data;
    }
    
    $sessions = [];
    $clicks = [];
    $sessionEnds = [];
    $otherEvents = [];
    
    // Séparer tous les types d'événements
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
            default:
                $otherEvents[] = $entry;
                break;
        }
    }
    
    // Créer un mapping des sessions
    $sessionMap = [];
    
    // Traiter d'abord les sessions de début
    foreach ($sessions as $session) {
        $sessionId = $session['session_id'];
        $ipCustom = customizeIP($session['client_ip'] ?? '', $session['country'] ?? '', $session['city'] ?? '');
        
        $sessionMap[$sessionId] = [
            'session_id' => $sessionId,
            'timestamp' => $session['timestamp'],
            'client_ip' => $session['client_ip'] ?? 'Non spécifié',
            'country' => $ipCustom['country'],
            'city' => $ipCustom['city'],
            'latitude' => $session['latitude'] ?? 0,
            'longitude' => $session['longitude'] ?? 0,
            'session_duration' => 0,
            'click_count' => 0,
            'is_from_session_start' => true
        ];
    }
    
    // Ajouter les sessions de fin
    foreach ($sessionEnds as $sessionEnd) {
        $sessionId = $sessionEnd['session_id'];
        $ipCustom = customizeIP($sessionEnd['client_ip'] ?? '', $sessionEnd['country'] ?? '', $sessionEnd['city'] ?? '');
        
        if (!isset($sessionMap[$sessionId])) {
            // Créer une session à partir de session_end
            $sessionMap[$sessionId] = [
                'session_id' => $sessionId,
                'timestamp' => $sessionEnd['timestamp'],
                'client_ip' => $sessionEnd['client_ip'] ?? 'Non spécifié',
                'country' => $ipCustom['country'],
                'city' => $ipCustom['city'],
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
    
    // Créer des sessions à partir des clics (pour capturer toutes les sessions)
    foreach ($clicks as $click) {
        $sessionId = $click['session_id'];
        if (!isset($sessionMap[$sessionId])) {
            $ipCustom = customizeIP($click['client_ip'] ?? '', $click['country'] ?? '', $click['city'] ?? '');
            
            $sessionMap[$sessionId] = [
                'session_id' => $sessionId,
                'timestamp' => $click['timestamp'],
                'client_ip' => $click['client_ip'] ?? 'Non spécifié',
                'country' => $ipCustom['country'],
                'city' => $ipCustom['city'],
                'latitude' => $click['latitude'] ?? 0,
                'longitude' => $click['longitude'] ?? 0,
                'session_duration' => 0,
                'click_count' => 0,
                'is_from_click' => true
            ];
        }
    }
    
    // Calculer les statistiques
    $stats = [
        'total_sessions' => count($sessionMap),
        'total_clicks' => count($clicks),
        'sessions_with_clicks' => count(array_filter($sessionMap, function($s) { return ($s['click_count'] ?? 0) > 0; })),
        'sessions_without_clicks' => count(array_filter($sessionMap, function($s) { return ($s['click_count'] ?? 0) == 0; })),
        'countries' => [],
        'cities' => []
    ];
    
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
    
    // Analyser les parcours utilisateur
    $userJourneys = [];
    foreach ($sessionMap as $sessionId => $session) {
        $sessionClicks = array_filter($clicks, function($click) use ($sessionId) {
            return $click['session_id'] === $sessionId;
        });
        
        $clickedFiles = [];
        foreach ($sessionClicks as $click) {
            if (isset($click['page'])) {
                $clickedFiles[] = basename($click['page']);
            }
        }
        
        $userJourneys[] = [
            'session_id' => $sessionId,
            'city' => $session['city'],
            'journey' => empty($clickedFiles) ? 'Aucun parcours (session sans clics)' : implode(' → ', array_unique($clickedFiles)),
            'files' => empty($clickedFiles) ? 'Aucun fichier' : implode(', ', array_unique($clickedFiles)),
            'click_count' => count($sessionClicks),
            'duration' => $session['session_duration'] > 0 ? round($session['session_duration'] / 1000, 1) . 's' : '0s'
        ];
    }
    
    // Analyser les fichiers les plus cliqués
    $fileStats = [];
    foreach ($clicks as $click) {
        if (isset($click['page'])) {
            $file = basename($click['page']);
            $fileStats[$file] = ($fileStats[$file] ?? 0) + 1;
        }
    }
    arsort($fileStats);
    
    return [
        'sessions' => $sessionMap,
        'clicks' => $clicks,
        'user_journeys' => $userJourneys,
        'file_stats' => $fileStats,
        'stats' => $stats,
        'last_update' => date('Y-m-d H:i:s')
    ];
}

// Récupérer et traiter les données
$rawData = getAnalyticsData();
$processedData = processData($rawData);
?>
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Analytics - Tracking</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css">
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
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
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .card-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px 15px 0 0 !important;
            border: none;
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
        .nav-tabs .nav-link {
            border-radius: 10px 10px 0 0;
            margin-right: 5px;
        }
        .nav-tabs .nav-link.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
        }
        .table {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .table thead th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-weight: 600;
            padding: 15px 12px;
        }
        .table tbody tr {
            transition: all 0.3s ease;
        }
        .table tbody tr:hover {
            background-color: #f8f9fa;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .table tbody td {
            padding: 12px;
            vertical-align: middle;
            border-top: 1px solid #e9ecef;
        }
        .badge {
            font-size: 0.85rem;
            padding: 6px 12px;
            border-radius: 20px;
        }
        .country-badge {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
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
                        <div class="stat-number"><?php echo $processedData['stats']['sessions_without_clicks']; ?></div>
                        <div class="stat-label">Sessions sans Clics</div>
                    </div>
                </div>
            </div>

            <!-- Onglets -->
            <ul class="nav nav-tabs mb-4" id="dashboardTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="geolocation-tab" data-bs-toggle="tab" data-bs-target="#geolocation" type="button" role="tab">
                        🗺️ Géolocalisation
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="files-tab" data-bs-toggle="tab" data-bs-target="#files" type="button" role="tab">
                        📁 Tracking par Fichier
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="journeys-tab" data-bs-toggle="tab" data-bs-target="#journeys" type="button" role="tab">
                        🚶 Parcours Utilisateurs
                    </button>
                </li>
            </ul>

            <div class="tab-content" id="dashboardTabsContent">
                <!-- Onglet Géolocalisation -->
                <div class="tab-pane fade show active" id="geolocation" role="tabpanel">
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
                                                    <th>Session ID</th>
                                                    <th>Date</th>
                                                    <th>Heure</th>
                                                    <th>IP</th>
                                                    <th>Pays</th>
                                                    <th>Ville</th>
                                                    <th>Durée</th>
                                                    <th>Clics</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <?php foreach ($processedData['sessions'] as $session): ?>
                                                <tr>
                                                    <td><code><?php echo substr($session['session_id'], 0, 20); ?>...</code></td>
                                                    <td><?php echo date('d/m/Y', strtotime($session['timestamp'])); ?></td>
                                                    <td><?php echo date('H:i:s', strtotime($session['timestamp'])); ?></td>
                                                    <td><?php echo htmlspecialchars($session['client_ip']); ?></td>
                                                    <td><span class="country-badge"><?php echo htmlspecialchars($session['country']); ?></span></td>
                                                    <td><?php echo htmlspecialchars($session['city']); ?></td>
                                                    <td><?php echo $session['session_duration'] > 0 ? round($session['session_duration'] / 1000, 1) . 's' : '0s'; ?></td>
                                                    <td><?php echo $session['click_count']; ?></td>
                                                </tr>
                                                <?php endforeach; ?>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Onglet Tracking par Fichier -->
                <div class="tab-pane fade" id="files" role="tabpanel">
                    <div class="row">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-header">
                                    <h5>📁 Fichiers les Plus Cliqués</h5>
                                </div>
                                <div class="card-body">
                                    <div class="table-responsive">
                                        <table class="table table-striped">
                                            <thead>
                                                <tr>
                                                    <th>Fichier</th>
                                                    <th>Nombre de Clics</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <?php foreach ($processedData['file_stats'] as $file => $count): ?>
                                                <tr>
                                                    <td><strong><?php echo htmlspecialchars($file); ?></strong></td>
                                                    <td><span class="badge bg-primary"><?php echo $count; ?></span></td>
                                                </tr>
                                                <?php endforeach; ?>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Onglet Parcours Utilisateurs -->
                <div class="tab-pane fade" id="journeys" role="tabpanel">
                    <div class="row">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-header">
                                    <h5>🚶 Détails des Parcours</h5>
                                </div>
                                <div class="card-body">
                                    <div class="table-responsive">
                                        <table class="table table-striped">
                                            <thead>
                                                <tr>
                                                    <th>Session ID</th>
                                                    <th>Ville</th>
                                                    <th>Parcours</th>
                                                    <th>Fichiers Cliqués</th>
                                                    <th>Nombre de Clics</th>
                                                    <th>Durée Estimée</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <?php foreach ($processedData['user_journeys'] as $journey): ?>
                                                <tr>
                                                    <td><code><?php echo substr($journey['session_id'], 0, 20); ?>...</code></td>
                                                    <td><?php echo htmlspecialchars($journey['city']); ?></td>
                                                    <td><?php echo htmlspecialchars($journey['journey']); ?></td>
                                                    <td><?php echo htmlspecialchars($journey['files']); ?></td>
                                                    <td><span class="badge bg-info"><?php echo $journey['click_count']; ?></span></td>
                                                    <td><?php echo $journey['duration']; ?></td>
                                                </tr>
                                                <?php endforeach; ?>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
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

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Initialiser la carte
        const map = L.map('map').setView([46.0, 2.0], 6);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Ajouter les marqueurs des sessions
        <?php if (!isset($processedData['error'])): ?>
        const sessions = <?php echo json_encode(array_values($processedData['sessions'])); ?>;
        sessions.forEach(session => {
            if (session.latitude && session.longitude) {
                const marker = L.marker([session.latitude, session.longitude]).addTo(map);
                marker.bindPopup(`
                    <strong>Session:</strong> ${session.session_id.substring(0, 20)}...<br>
                    <strong>Ville:</strong> ${session.city}<br>
                    <strong>Pays:</strong> ${session.country}<br>
                    <strong>Date:</strong> ${new Date(session.timestamp).toLocaleString()}<br>
                    <strong>Clics:</strong> ${session.click_count}
                `);
            }
        });
        <?php endif; ?>

        // Graphique des pays
        <?php if (!isset($processedData['error'])): ?>
        const countryData = <?php echo json_encode($processedData['stats']['countries']); ?>;
        const ctx = document.getElementById('countryChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(countryData),
                datasets: [{
                    data: Object.values(countryData),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'
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
        <?php endif; ?>
    </script>
</body>
</html>
