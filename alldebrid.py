import sys
import requests
from plex_manager.config import TIMEOUT_SECONDS

def send_to_alldebrid(apikey: str, torrent_data: dict):
    """
    Extrait le lien magnet/URL et l'envoie au convertisseur AllDebrid.
    """
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
