import os
import sys
import hashlib
import re
import requests

# ================= CONFIGURATION =================
TIMEOUT_SECONDS = 30

def clean_movie_title(title: str) -> str:
    """Nettoie un titre de film en remplaçant les caractères spéciaux par des espaces."""
    if not title:
        return ""
    cleaned = re.sub(r"[\'’\.\,\-\_\:\!\?]", " ", title)
    return " ".join(cleaned.split())

def search_c411_torrent(token: str, title: str, year: str) -> dict:
    """Recherche un torrent sur l'API C411 avec plusieurs niveaux de repli."""
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "PlexManager/1.0"
    }

    clean_title = clean_movie_title(title)
    search_query_with_year = f"{clean_title} {year}".strip()

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

    # 1. Essai avec le titre complet + l'année
    results = execute_query(search_query_with_year)

    # 2. Essai avec le titre complet sans l'année
    if not results:
        print("⚠️ Aucun résultat avec l'année. Essai avec le titre complet...")
        results = execute_query(clean_title)

    # 3. Essai de repli sur les mots-clés principaux (ex: "Star Wars")
    if not results:
        words = [w for w in clean_title.split() if w.lower() not in ['les', 'des', 'un', 'une', 'la', 'le', 'de', 'du']]
        short_query = ' '.join(words[:2]) if len(words) >= 2 else clean_title
        if short_query.lower() != clean_title.lower():
            print(f"⚠️ Essai de repli avec les mots-clés : {short_query}")
            results = execute_query(short_query)

    if not results:
        print(f"❌ Aucun torrent trouvé sur C411 pour : {clean_title}")
        sys.exit(0)

    torrent = results[0]
    print(f"✅ Torrent trouvé : {torrent.get('name', 'Inconnu')}")
    return torrent

def send_to_alldebrid(apikey: str, torrent_data: dict):
    """Extrait le magnet et l'envoie au convertisseur AllDebrid."""
    magnet = (
        torrent_data.get("magnet")
        or torrent_data.get("download_url")
        or torrent_data.get("link")
    )

    if not magnet:
        print("❌ Aucun lien magnet ou de téléchargement valide trouvé.")
        sys.exit(1)

    print("🚀 Envoi du lien vers le convertisseur AllDebrid...")

    params = {
        "agent": "PlexManager",
        "apikey": apikey,
        "magnets[]": magnet
    }

    try:
        response = requests.get(
            "https://api.alldebrid.com/v4/magnet/upload",
            params=params,
            timeout=TIMEOUT_SECONDS
        )
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau lors de la communication avec AllDebrid : {e}")
        sys.exit(1)

    print(f"Code HTTP AllDebrid : {response.status_code}")

    try:
        result = response.json()
    except Exception:
        print("❌ Réponse non JSON reçue d'AllDebrid :")
        print(response.text)
        sys.exit(1)

    print("Réponse AllDebrid :", result)

    if result.get("status") != "success":
        print("❌ Erreur signalée par AllDebrid.")
        sys.exit(1)

    print("🎉 Torrent soumis et converti avec succès sur AllDebrid !")

def main():
    print("🔐 Vérification de l'authentification...")

    valid_user = os.environ.get("VALID_USER")
    valid_pass = os.environ.get("VALID_PASS")
    input_user = os.environ.get("INPUT_USER", "")
    input_hash = os.environ.get("INPUT_PASS_HASH", "")

    if not valid_user or not valid_pass:
        print("❌ Erreur : Les secrets d'authentification ne sont pas configurés.")
        sys.exit(1)

    expected_hash = hashlib.sha256(valid_pass.encode("utf-8")).hexdigest()

    if input_user != valid_user or input_hash.lower() != expected_hash.lower():
        print("❌ Authentification refusée.")
        sys.exit(1)

    print("✅ Authentification validée avec succès.")

    c411_token = os.environ.get("C411_TOKEN")
    alldebrid_key = os.environ.get("ALLDEBRID_KEY")
    title = os.environ.get("MOVIE_TITLE", "")
    year = os.environ.get("MOVIE_YEAR", "")

    if not c411_token or not alldebrid_key:
        print("❌ Erreur : Les clés API C411 ou AllDebrid sont manquantes.")
        sys.exit(1)

    print(f"🎬 Film demandé : {title} ({year})")

    # Exécution de la chaîne
    torrent = search_c411_torrent(c411_token, title, year)
    send_to_alldebrid(alldebrid_key, torrent)

if __name__ == "__main__":
    main()
