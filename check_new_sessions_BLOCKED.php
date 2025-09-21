<?php
// 🚨 URGENT : FICHIER DE BLOCAGE COMPLET
header('Content-Type: application/json');

// BLOQUER COMPLÈTEMENT L'ENVOI D'EMAILS
echo json_encode([
    'success' => false,
    'message' => 'SYSTÈME D\'ALERTE BLOQUÉ - AUCUN EMAIL ENVOYÉ',
    'status' => 'BLOCKED',
    'emails_sent' => 0,
    'new_sessions' => 0
]);

// ARRÊTER IMMÉDIATEMENT L'EXÉCUTION
exit;
?>
