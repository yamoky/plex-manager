import os
import sys
import hashlib
from plex_manager.c411 import search_c411_torrent
from plex_manager.alldebrid import send_to_alldebrid

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

    # Récupération des clés API et des métadonnées du film
    c411_token = os.environ.get("C411_TOKEN")
    alldebrid_key = os.environ.get("ALLDEBRID_KEY")
    title = os.environ.get("MOVIE_TITLE", "")
    year = os.environ.get("MOVIE_YEAR", "")

    if not c411_token or not alldebrid_key:
        print("❌ Erreur : Les clés API C411 ou AllDebrid sont manquantes.")
        sys.exit(1)

    print(f"🎬 Film demandé : {title} ({year})")

    # Recherche sur C411
    torrent = search_c411_torrent(c411_token, title, year)

    # Envoi vers AllDebrid
    send_to_alldebrid(alldebrid_key, torrent)

if __name__ == "__main__":
    main()
