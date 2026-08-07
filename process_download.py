import sys
import os
import hashlib
import requests

MOVIE_TITLE = sys.argv[1] if len(sys.argv) > 1 else ""
MOVIE_YEAR = sys.argv[2] if len(sys.argv) > 2 else ""
INPUT_USER = sys.argv[3] if len(sys.argv) > 3 else ""
INPUT_HASH = sys.argv[4] if len(sys.argv) > 4 else ""

# Secrets récupérés depuis les paramètres GitHub
VALID_USER = os.environ.get("APP_USER")
VALID_PASS = os.environ.get("APP_PASSWORD")
C411_API_TOKEN = os.environ.get("C411_API_TOKEN")
ALLDEBRID_API_KEY = os.environ.get("ALLDEBRID_API_KEY")

def verify_credentials():
    if not VALID_PASS or not VALID_USER:
        print("Erreur : Paramètres de sécurité manquants sur GitHub.")
        return False
    
    # Génération du hash SHA-256 attendu
    expected_hash = hashlib.sha256(VALID_PASS.encode('utf-8')).hexdigest()
    
    if INPUT_USER == VALID_USER and INPUT_HASH.lower() == expected_hash.lower():
        return True
    return False

def main():
    if not verify_credentials():
        print(f"SÉCURITÉ : Échec d'authentification pour l'utilisateur '{INPUT_USER}'. Accès refusé.")
        sys.exit(1)

    print(f"Authentification réussie pour '{INPUT_USER}'. Recherche : {MOVIE_TITLE} ({MOVIE_YEAR})")
    
    # 1. Recherche C411
    search_url = f"https://api.c411.org/torrents/search?title={MOVIE_TITLE}"
    headers = {"Authorization": f"Bearer {C411_API_TOKEN}"}
    
    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            print(f"Erreur recherche C411 : Code {response.status_code}")
            return
        results = response.json().get('results', [])
    except Exception as e:
        print(f"Erreur de connexion à l'API C411 : {e}")
        return

    # 2. Filtrage strict pour le NAS MyCloud Home
    best_torrent = None
    for item in results:
        name = item.get('name', '').lower()
        size_gb = item.get('size', 0) / (1024**3)
        
        # Critères NAS : Max 10 Go, 1080p ou 720p, pas de REMUX ni AV1
        if size_gb <= 10.0 and ('1080p' in name or '720p' in name):
            if 'remux' not in name and 'av1' not in name:
                best_torrent = item
                break
                
    if not best_torrent:
        print("Aucun torrent correspondant aux critères d'optimisation du NAS trouvé.")
        return

    magnet_link = best_torrent.get('magnet_or_download_link')
    print(f"Torrent sélectionné : {best_torrent.get('name')} ({size_gb:.2f} Go)")

    # 3. Envoi vers AllDebrid
    alldebrid_url = f"https://api.alldebrid.com/v4/magnet/upload?agent=PlexApp&apikey={ALLDEBRID_API_KEY}&magnet={magnet_link}"
    res_ad = requests.get(alldebrid_url)
    
    if res_ad.status_code == 200:
        print("Succès ! Film transmis à AllDebrid.")
    else:
        print(f"Erreur d'envoi vers AllDebrid : {res_ad.text}")

if __name__ == "__main__":
    main()
