import sys
import requests
from plex_manager.utils import clean_movie_title
from plex_manager.config import TIMEOUT_SECONDS

def search_c411_torrent(token: str, title: str, year: str) -> dict:
    """
    Recherche un torrent sur l'API C411 avec l'année, puis sans l'année si besoin.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "PlexManager/1.0"
    }

    clean_title = clean_movie_title(title)
    search_query = f"{clean_title} {year}".strip()

    def execute_query(query):
        print(f"🔍 Recherche C411 : {query}")
        try:
            r = requests.get(
                "https://c411.org/api/torrents",
                headers=headers,
                params={"q": query},
                timeout=TIMEOUT_SECONDS
            )
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau lors de la connexion à C411 : {e}")
            sys.exit(1)

        print(f"Code HTTP C411 : {r.status_code}")
        
        if r.status_code != 200:
            print(f"Erreur API : {r.text}")
            sys.exit(1)

        try:
            data = r.json()
        except Exception:
            print("❌ Réponse non JSON reçue de C411 :")
            print(r.text)
            sys.exit(1)

        if isinstance(data, dict):
            return data.get("results", [])
        elif isinstance(data, list):
            return data
        return []

    # 1. Premier essai avec l'année
    results = execute_query(search_query)

    # 2. Second essai sans l'année si aucun résultat
    if not results and year:
        print("⚠️ Aucun résultat avec l'année. Nouvelle tentative sans l'année...")
        results = execute_query(clean_title)

    if not results:
        print(f"❌ Aucun torrent trouvé sur C411 pour : {clean_title}")
        sys.exit(0)

    # Sélection du premier résultat pertinent
    torrent = results[0]
    print(f"✅ Torrent trouvé : {torrent.get('name', 'Inconnu')}")
    return torrent
