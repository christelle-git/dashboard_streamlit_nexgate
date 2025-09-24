# Dashboard Streamlit – Analytics (Nexgate)

Objectif: déployer rapidement le dashboard en tant que web app sur Streamlit Cloud, en lisant les données depuis `https://christellelusso.nexgate.ch/analytics_data.json`.

Fichiers importants
- `dashboard.py` (main app)
- `config_setup.py` (config centralisée – aucune variable obligatoire)
- `requirements.txt` (dépendances pour Streamlit Cloud)
- `.streamlit/config.toml` (options d’UI – optionnel)

Déploiement sur Streamlit Cloud (résumé)
1. Créer un repo GitHub (ou une branche dédiée)
2. Pousser ces fichiers au root du repo
3. Sur Streamlit Cloud: New app → choisir le repo/branche → Main file: `dashboard.py` → Deploy

Notes
- Les données sont lues côté app via `requests` depuis Nexgate; aucun fichier JSON local n’est requis.
- Le stockage local (SQLite) est optionnel et éphémère sur Streamlit Cloud.