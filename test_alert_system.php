<?php
// Script de test pour le système d'alerte
header('Content-Type: application/json');

// Supprimer les fichiers de protection pour permettre le test
$notifiedFile = 'notified_sessions.json';
$lastCheckFile = 'last_check.json';

if (file_exists($lastCheckFile)) {
    unlink($lastCheckFile);
}

if (file_exists($notifiedFile)) {
    unlink($notifiedFile);
}

echo json_encode([
    'success' => true,
    'message' => 'Fichiers de protection supprimés - Test possible',
    'debug' => 'Protection désactivée pour les tests'
]);
?>
