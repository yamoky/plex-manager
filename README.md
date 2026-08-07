# Plex Manager

Plex Manager est un outil automatisé léger permettant de lier une interface Web hébergée sur GitHub Pages à un flux de téléchargement direct via **C411** et **AllDebrid**.

## Architecture du projet
```text
plex-manager/
├── .github/
│   └── workflows/
│       └── download.yml
├── plex_manager/
│   ├── __init__.py
│   ├── c411.py
│   ├── alldebrid.py
│   ├── config.py
│   └── utils.py
├── process_download.py
├── requirements.txt
└── README.md
