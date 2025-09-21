<?php
/**
 * Dashboard de Tracking Analytics - Version PHP Finale
 * Compatible avec l'hébergeur Nexgate (Web-FTP uniquement)
 * 
 * @author Christelle Lusso
 * @version 2.1
 * @date 2025-09-01
 */

// Configuration
$ANALYTICS_DATA_URL = 'https://christellelusso.nexgate.ch/analytics_data.json';
$CACHE_DURATION = 300; // 5 minutes
$CACHE_FILE = 'analytics_cache.json';

// Fonction pour personnaliser l'IP fixe et corriger les pays
function customizeIP($ip, $country, $city) {
    if ($ip === '82.66.151.2') {
        return ['country' => 'France', 'city' => 'MOI'];
    }
    
    // Corriger les pays basés sur les villes
    $cityCountryMap = [
        'Mountain View' => 'États-Unis',
        'Seocho-gu' => 'Corée du Sud',
        'Seoul' => 'Corée du Sud',
        'San Francisco' => 'États-Unis',
        'New York' => 'États-Unis',
        'London' => 'Royaume-Uni',
        'Paris' => 'France',
        'Berlin' => 'Allemagne',
        'Tokyo' => 'Japon',
        'Sydney' => 'Australie',
        'Sartrouville' => 'France',
        'Houilles' => 'France'
    ];
    
    foreach ($cityCountryMap as $cityName => $correctCountry) {
        if (stripos($city, $cityName) !== false) {
            return ['country' => $correctCountry, 'city' => $city];
        }
    }
    
    return ['country' => $country, 'city' => $city];
}

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
            'user_agent' => 'Dashboard PHP/2.1'
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
        $timeA = strtotime($a['timestamp']);
        $timeB = strtotime($b['timestamp']);
        if ($timeA === false || $timeB === false) {
            return 0; // Garder l'ordre si timestamp invalide
        }
        return $timeB - $timeA; // Plus récentes en premier
    });
    
    // Analyser les parcours utilisateur
    $userJourneys = [];
    foreach ($sessionMap as $sessionId => $session) {
        $sessionClicks = array_filter($clicks, function($click) use ($sessionId) {
            return $click['session_id'] === $sessionId;
        });
        
        $clickedFiles = [];
        foreach ($sessionClicks as $click) {
            if (isset($click['page']) && !empty($click['page'])) {
                $page = $click['page'];
                // Si c'est la page d'accueil, on l'indique
                if ($page === '/' || $page === '') {
                    $clickedFiles[] = 'Page d\'accueil';
                } else {
                    $clickedFiles[] = basename($page);
                }
            }
        }
        
        // Trier les clics par timestamp pour avoir l'ordre chronologique
        usort($sessionClicks, function($a, $b) {
            return strtotime($a['timestamp']) - strtotime($b['timestamp']);
        });
        
        $userJourneys[] = [
            'session_id' => $sessionId,
            'timestamp' => $session['timestamp'],
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
        if (isset($click['page']) && !empty($click['page'])) {
            $page = $click['page'];
            if ($page === '/' || $page === '') {
                $file = 'Page d\'accueil';
            } else {
                $file = basename($page);
            }
            if (!empty($file)) { // Filtrer les fichiers vides
                $fileStats[$file] = ($fileStats[$file] ?? 0) + 1;
            }
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
        .nav-tabs .nav-link {
            border-radius: 10px 10px 0 0;
            margin-right: 5px;
        }
        .nav-tabs .nav-link.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
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
                                                <?php foreach (array_slice($processedData['sessions'], 0, 100) as $session): ?>
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
                                                            <?php elseif (isset($session['is_from_session_start'])): ?>
                                                                <span class="badge bg-success">Session Start</span>
                                                            <?php else: ?>
                                                                <span class="badge bg-info">From Click</span>
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
                </div>

                <!-- Onglet Tracking par Fichier -->
                <div class="tab-pane fade" id="files" role="tabpanel">
                    <div class="row mb-4">
                        <div class="col-12">
                            <div class="alert alert-info">
                                <h6>📊 Analyse des Fichiers</h6>
                                <p class="mb-0">Cette section montre quels fichiers sont les plus consultés sur votre site. Les fichiers sont classés par nombre de clics.</p>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-header">
                                    <h5>📁 Fichiers les Plus Cliqués</h5>
                                    <small class="text-muted">Classement par popularité</small>
                                </div>
                                <div class="card-body">
                                    <div class="table-responsive">
                                        <table class="table table-striped">
                                            <thead>
                                                <tr>
                                                    <th>#</th>
                                                    <th>Fichier</th>
                                                    <th>Nombre de Clics</th>
                                                    <th>Type</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <?php 
                                                $rank = 1;
                                                foreach ($processedData['file_stats'] as $file => $count): 
                                                    $fileType = pathinfo($file, PATHINFO_EXTENSION);
                                                    $typeIcon = '';
                                                    switch(strtolower($fileType)) {
                                                        case 'pdf': $typeIcon = '📄'; break;
                                                        case 'jpg':
                                                        case 'jpeg':
                                                        case 'png':
                                                        case 'gif': $typeIcon = '🖼️'; break;
                                                        case 'html': $typeIcon = '🌐'; break;
                                                        default: $typeIcon = '📁'; break;
                                                    }
                                                ?>
                                                <tr>
                                                    <td><span class="badge bg-secondary"><?php echo $rank; ?></span></td>
                                                    <td><strong><?php echo htmlspecialchars($file); ?></strong></td>
                                                    <td><span class="badge bg-primary"><?php echo $count; ?></span></td>
                                                    <td><?php echo $typeIcon; ?> <?php echo strtoupper($fileType); ?></td>
                                                </tr>
                                                <?php 
                                                $rank++;
                                                endforeach; ?>
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
                    <div class="row mb-4">
                        <div class="col-12">
                            <div class="alert alert-info">
                                <h6>🚶 Analyse des Parcours Utilisateurs</h6>
                                <p class="mb-0">Cette section montre comment les visiteurs naviguent sur votre site : quels fichiers ils consultent, dans quel ordre, et combien de temps ils restent.</p>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-header">
                                    <h5>🚶 Détails des Parcours</h5>
                                    <small class="text-muted">Analyse du comportement des visiteurs</small>
                                </div>
                                <div class="card-body">
                                    <div class="table-responsive">
                                        <table class="table table-striped">
                                            <thead>
                                                <tr>
                                                    <th>Session</th>
                                                    <th>Date/Heure</th>
                                                    <th>Localisation</th>
                                                    <th>Parcours de Navigation</th>
                                                    <th>Fichiers Consultés</th>
                                                    <th>Activité</th>
                                                    <th>Durée</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <?php foreach ($processedData['user_journeys'] as $journey): ?>
                                                <tr>
                                                    <td>
                                                        <code><?php echo substr($journey['session_id'], 0, 15); ?>...</code>
                                                        <br><small class="text-muted">ID de session</small>
                                                    </td>
                                                    <td>
                                                        <strong><?php echo date('d/m/Y H:i', strtotime($journey['timestamp'])); ?></strong>
                                                        <br><small class="text-muted">Date et heure</small>
                                                    </td>
                                                    <td>
                                                        <strong><?php echo htmlspecialchars($journey['city']); ?></strong>
                                                        <br><small class="text-muted">Ville du visiteur</small>
                                                    </td>
                                                    <td>
                                                        <span class="badge bg-light text-dark"><?php echo htmlspecialchars($journey['journey']); ?></span>
                                                    </td>
                                                    <td>
                                                        <small><?php echo htmlspecialchars($journey['files']); ?></small>
                                                    </td>
                                                    <td>
                                                        <span class="badge bg-primary"><?php echo $journey['click_count']; ?> clic<?php echo $journey['click_count'] > 1 ? 's' : ''; ?></span>
                                                    </td>
                                                    <td>
                                                        <span class="badge bg-success"><?php echo $journey['duration']; ?></span>
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
                </div>
            </div>
        <?php endif; ?>
    </div>

    <!-- Bouton de rafraîchissement -->
    <button class="btn btn-primary refresh-btn" onclick="location.reload()">
        🔄 Actualiser
    </button>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Données pour les graphiques
        const sessions = <?php echo json_encode(array_values($processedData['sessions'])); ?>;
        const stats = <?php echo json_encode($processedData['stats']); ?>;

        // Initialiser la carte
        const map = L.map('map').setView([46.0, 2.0], 6);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

        // Coordonnées par défaut pour les villes
        const cityCoords = {
            'Paris': [48.8566, 2.3522],
            'Sartrouville': [48.9442, 2.1917],
            'Mountain View': [37.3861, -122.0839],
            'Seocho-gu': [37.4945, 127.0276],
            'Seoul': [37.5665, 126.9780],
            'Houilles': [48.9226, 2.1850],
            'Paris (IP)': [48.8566, 2.3522],
            'Sartrouville (IP)': [48.9442, 2.1917]
        };
        
        // Ajouter les marqueurs des sessions
        let markersAdded = 0;
        let sessionsWithoutCoords = 0;
        
        sessions.forEach(session => {
            let lat = session.latitude;
            let lng = session.longitude;
            
            // Debug pour toutes les sessions
            console.log(`Session: ${session.session_id} - ${session.city}, ${session.country} - Clics: ${session.click_count} - GPS: [${lat}, ${lng}]`);
            
            // Si pas de coordonnées GPS, essayer de les déduire de la ville
            if (!lat || !lng || lat === 0 || lng === 0) {
                const cityName = session.city.replace(' (IP)', '').trim();
                if (cityCoords[cityName]) {
                    lat = cityCoords[cityName][0];
                    lng = cityCoords[cityName][1];
                } else if (cityCoords[session.city]) {
                    // Essayer avec le nom complet de la ville
                    lat = cityCoords[session.city][0];
                    lng = cityCoords[session.city][1];
                } else {
                    // Coordonnées par défaut pour la France si pas trouvé
                    lat = 48.8566;
                    lng = 2.3522;
                }
                console.log(`Coordonnées déduites pour ${session.session_id}: [${lat}, ${lng}]`);
            }
            
            // Toujours afficher la session sur la carte
            const marker = L.marker([lat, lng])
                .addTo(map)
                .bindPopup(`
                    <strong>Session ${session.session_id}</strong><br>
                    <strong>Date:</strong> ${new Date(session.timestamp).toLocaleString()}<br>
                    <strong>Pays:</strong> ${session.country}<br>
                    <strong>Ville:</strong> ${session.city}<br>
                    <strong>Clics:</strong> ${session.click_count || 0}<br>
                    <strong>Durée:</strong> ${session.session_duration ? (session.session_duration/1000).toFixed(1) + 's' : '0s'}<br>
                    <strong>IP:</strong> ${session.client_ip}
                `);
            markersAdded++;
        });
        
        // Afficher un message si des sessions n'ont pas de coordonnées
        if (sessionsWithoutCoords > 0) {
            console.log(`${sessionsWithoutCoords} sessions sans coordonnées GPS (non affichées sur la carte)`);
        }
        
        // Ajuster la vue de la carte pour inclure tous les marqueurs
        if (markersAdded > 0) {
            const group = new L.featureGroup();
            map.eachLayer(function(layer) {
                if (layer instanceof L.Marker) {
                    group.addLayer(layer);
                }
            });
            if (group.getLayers().length > 0) {
                map.fitBounds(group.getBounds().pad(0.1));
            }
        }

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

        // Auto-refresh désactivé pour éviter les bannissements
        // setTimeout(() => {
        //     location.reload();
        // }, 300000);
    </script>
</body>
</html>
