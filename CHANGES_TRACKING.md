# Modifications du Script de Tracking

## Objectif
Éviter le blacklist de l'IP en réduisant le nombre d'événements envoyés au serveur.

## Modifications apportées à `advanced_tracking.js`

### 1. Suppression du monitoring d'activité
- **Ligne 25** : Suppression de `this.setupActivityMonitoring();`
- **Résultat** : Plus d'événements d'inactivité générés automatiquement

### 2. Protection contre le spam
- **Ajout** : `this.lastSendTime = 0;` et `this.minSendInterval = 1000;` dans le constructeur
- **Résultat** : Maximum 1 événement par seconde

### 3. Filtrage des événements
- **Modification** de la fonction `sendData()` :
  ```javascript
  // Ignore les événements d'inactivité et de scroll pour éviter le blacklist
  if (data.type === 'inactivity' || data.type === 'scroll') {
      console.log('Événement ignoré:', data.type);
      return;
  }
  ```

## Événements maintenant ignorés
- ❌ `inactivity` - Événements d'inactivité
- ❌ `scroll` - Événements de défilement
- ✅ `click` - Clics (conservés)
- ✅ `session_start` - Début de session (conservé)
- ✅ `session_end` - Fin de session (conservée)
- ✅ `file_download` - Téléchargements (conservés)

## Protection anti-spam
- **Limite** : 1 événement maximum par seconde
- **Log** : Messages dans la console pour les événements ignorés

## Application
1. Remplacer le contenu de `advanced_tracking.js` sur votre serveur web
2. Vider le cache du navigateur
3. Tester sur votre site

## Résultat attendu
- Réduction drastique du nombre d'événements envoyés
- Protection contre le blacklist IP
- Conservation des données importantes (clics, sessions) 