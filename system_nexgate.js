<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Tracker Analytics V6 - IP et GPS Séparés</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .section {
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background-color: #fafafa;
        }
        .section h2 {
            color: #34495e;
            margin-top: 0;
        }
        .file-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .file-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #3498db;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            color: #2c3e50;
        }
        .file-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
            border-color: #2980b9;
        }
        .file-item img {
            max-width: 100px;
            max-height: 100px;
            margin-bottom: 10px;
        }
        .status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 1000;
        }
        .status.success {
            background-color: #27ae60;
        }
        .status.error {
            background-color: #e74c3c;
        }
        .status.info {
            background-color: #3498db;
        }
        .debug-info {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            font-family: monospace;
            font-size: 12px;
        }
        .debug-info h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        .debug-info pre {
            margin: 10px 0;
            white-space: pre-wrap;
        }
        .test-buttons {
            text-align: center;
            margin: 20px 0;
        }
        .test-button {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        .test-button:hover {
            background: #2980b9;
        }
        .test-button.danger {
            background: #e74c3c;
        }
        .test-button.danger:hover {
            background: #c0392b;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📍 Test Tracker Analytics V6</h1>
        <p style="text-align: center; color: #7f8c8d; margin-bottom: 30px;">
            Version avec séparation IP et GPS - Test de localisation
        </p>

        <div class="section">
            <h2>🎯 Instructions de test</h2>
            <p>Cette page teste le nouveau tracker V6 qui sépare les données d'IP et de GPS :</p>
            <ul>
                <li><strong>IP publique</strong> : Récupérée via ipify.org</li>
                <li><strong>GPS</strong> : Demande d'autorisation au navigateur</li>
                <li><strong>Géolocalisation IP</strong> : Via ipapi.co</li>
                <li><strong>Comparaison</strong> : Calcul automatique de la cohérence</li>
            </ul>
            
            <div class="test-buttons">
                <button class="test-button" onclick="testGPS()">📍 Tester GPS</button>
                <button class="test-button" onclick="testIP()">🌐 Tester IP</button>
                <button class="test-button" onclick="testClick()">🖱️ Simuler un clic</button>
                <button class="test-button danger" onclick="clearDebug()">🗑️ Effacer debug</button>
            </div>
        </div>

        <div class="section">
            <h2>📁 Fichiers à tester</h2>
            <div class="file-grid">
                <a href="drawing/mystic.jpg" class="file-item">
                    <img src="drawing/mystic.jpg" alt="Mystic" onerror="this.style.display='none'">
                    <div>Mystic.jpg</div>
                </a>
                <a href="drawing/crazy_love_cp_clean.jpg" class="file-item">
                    <img src="drawing/crazy_love_cp_clean.jpg" alt="Crazy Love" onerror="this.style.display='none'">
                    <div>Crazy Love</div>
                </a>
                <a href="pdf/thesis.pdf" class="file-item">
                    <div style="font-size: 48px;">📄</div>
                    <div>Thesis.pdf</div>
                </a>
                <a href="pdf/abstract_lusso.pdf" class="file-item">
                    <div style="font-size: 48px;">📄</div>
                    <div>Abstract Lusso</div>
                </a>
                <a href="drawing/BD_criterium.jpg" class="file-item">
                    <img src="drawing/BD_criterium.jpg" alt="BD Criterium" onerror="this.style.display='none'">
                    <div>BD Criterium</div>
                </a>
                <a href="drawing/books_stack_cp.jpg" class="file-item">
                    <img src="drawing/books_stack_cp.jpg" alt="Books Stack" onerror="this.style.display='none'">
                    <div>Books Stack</div>
                </a>
            </div>
        </div>

        <div class="section">
            <h2>🔍 Informations de debug</h2>
            <div class="debug-info">
                <h3>Console du tracker :</h3>
                <pre id="debug-output">En attente des données...</pre>
            </div>
        </div>

        <div class="section">
            <h2>📊 Données collectées</h2>
            <div class="debug-info">
                <h3>Dernières données envoyées :</h3>
                <pre id="last-data">Aucune donnée encore...</pre>
            </div>
        </div>
    </div>

    <!-- Tracker V6 -->
    <script src="system.js"></script>
    
    <script>
        // Fonctions de test
        let debugOutput = [];
        let lastData = null;

        // Intercepter les logs du tracker
        const originalLog = console.log;
        console.log = function(...args) {
            originalLog.apply(console, args);
            const message = args.join(' ');
            debugOutput.push(new Date().toLocaleTimeString() + ': ' + message);
            if (debugOutput.length > 50) debugOutput.shift();
            updateDebugOutput();
        };

        function updateDebugOutput() {
            document.getElementById('debug-output').textContent = debugOutput.join('\n');
        }

        function updateLastData(data) {
            lastData = data;
            document.getElementById('last-data').textContent = JSON.stringify(data, null, 2);
        }

        // Intercepter les envois de données
        const originalFetch = window.fetch;
        window.fetch = function(url, options) {
            if (url.includes('api.php') && options && options.body) {
                try {
                    const data = JSON.parse(options.body);
                    updateLastData(data);
                } catch (e) {
                    console.log('Erreur parsing données:', e);
                }
            }
            return originalFetch.apply(this, arguments);
        };

        function showStatus(message, type = 'info') {
            const status = document.createElement('div');
            status.className = `status ${type}`;
            status.textContent = message;
            document.body.appendChild(status);
            setTimeout(() => status.remove(), 3000);
        }

        function testGPS() {
            if (navigator.geolocation) {
                showStatus('📍 Demande GPS en cours...', 'info');
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const coords = position.coords;
                        showStatus(`📍 GPS: ${coords.latitude.toFixed(4)}, ${coords.longitude.toFixed(4)} (précision: ${coords.accuracy}m)`, 'success');
                    },
                    (error) => {
                        showStatus(`📍 GPS refusé: ${error.message}`, 'error');
                    }
                );
            } else {
                showStatus('📍 GPS non supporté', 'error');
            }
        }

        function testIP() {
            showStatus('🌐 Test IP en cours...', 'info');
            fetch('https://api.ipify.org?format=json')
                .then(response => response.json())
                .then(data => {
                    showStatus(`🌐 IP: ${data.ip}`, 'success');
                })
                .catch(error => {
                    showStatus(`🌐 Erreur IP: ${error.message}`, 'error');
                });
        }

        function testClick() {
            const testElement = document.createElement('div');
            testElement.textContent = 'Test click';
            testElement.style.position = 'absolute';
            testElement.style.left = '-1000px';
            document.body.appendChild(testElement);
            
            const clickEvent = new MouseEvent('click', {
                clientX: 100,
                clientY: 100
            });
            
            testElement.dispatchEvent(clickEvent);
            document.body.removeChild(testElement);
            
            showStatus('🖱️ Clic simulé envoyé', 'success');
        }

        function clearDebug() {
            debugOutput = [];
            updateDebugOutput();
            document.getElementById('last-data').textContent = 'Aucune donnée...';
            showStatus('🗑️ Debug effacé', 'info');
        }

        // Initialisation
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 Page de test V6 chargée');
            showStatus('✅ Tracker V6 initialisé', 'success');
        });
    </script>
</body>
</html> 