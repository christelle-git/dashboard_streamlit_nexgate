# Dashboard Streamlit – Déploiement Cloud (Branche streamlit-deploy)

Ce dossier contient la version minimale du dashboard pour un déploiement sur Streamlit Cloud. Les données sont lues depuis https://christellelusso.nexgate.ch/analytics_data.json.

## Sommaire

- Fichiers inclus
- Déploiement Streamlit Cloud
- Pousser uniquement les fichiers nécessaires
- Authentification GitHub
- Politique d’indexation
- Maintenance

## Fichiers inclus
- dashboard.py
- requirements.txt
- .streamlit/config.toml

## Déploiement Streamlit Cloud (pas à pas)
1. Pousser la branche streamlit-deploy sur GitHub (voir Auth ci-dessous)
2. Streamlit Cloud → New app → Repo: christelle-git/dashboard_streamlit_nexgate → Branch: streamlit-deploy → Main file: dashboard.py → Deploy

## Pousser UNIQUEMENT les fichiers nécessaires
Branche orpheline (pas d’historique):




## Authentification GitHub
### Option 1 – Personal Access Token (Fine-grained)
- https://github.com/settings/tokens?type=beta
- Permissions: Contents Read/Write sur le repo
- Lors du push: login = ton compte, password = le token

### Option 2 – SSH
- ssh-keygen -t ed25519 -C "ton_email"
- pbcopy < ~/.ssh/id_ed25519.pub → ajouter dans GitHub / SSH keys
- git remote set-url origin git@github.com:christelle-git/dashboard_streamlit_nexgate.git
- git push -u origin streamlit-deploy

## Politique d’indexation
- Web app non indexée côté Nexgate (robots.txt/protection). Streamlit Cloud fournit une URL publique.

## Maintenance
- Modifier dashboard.py → commit → push sur streamlit-deploy → rebuild auto sur Streamlit Cloud.
