import re

def clean_movie_title(title: str) -> str:
    """
    Nettoie un titre de film en remplaçant les points, tirets, 
    apostrophes et caractères spéciaux par des espaces.
    """
    if not title:
        return ""
    # Remplace les points, tirets bas, apostrophes et ponctuations par des espaces
    cleaned = re.sub(r"[\'’\.\,\-\_\:\!\?]", " ", title)
    # Supprime les espaces multiples
    return " ".join(cleaned.split())
