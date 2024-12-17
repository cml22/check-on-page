import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import json

# Configuration des en-têtes pour éviter les erreurs 403
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# Fonction pour récupérer et parser une page
def fetch_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup, response.status_code
    except requests.RequestException as e:
        st.error(f"Erreur lors de la récupération de la page : {e}")
        return None, None

# Fonction pour extraire les balises meta importantes
def get_meta_info(soup):
    title = soup.title.string if soup.title else "Aucun titre trouvé"
    meta_desc = soup.find("meta", attrs={"name": "description"})
    description = meta_desc["content"] if meta_desc and "content" in meta_desc.attrs else "Aucune description trouvée"
    canonical = soup.find("link", rel="canonical")
    canonical_url = canonical["href"] if canonical else "Aucune URL canonique trouvée"
    return title, description, canonical_url

# Fonction pour récupérer les en-têtes HTTP
def get_http_headers(url):
    try:
        response = requests.head(url, headers=HEADERS, timeout=10)
        return dict(response.headers), response.status_code
    except requests.RequestException as e:
        return {"Erreur": str(e)}, None

# Fonction pour analyser les liens internes et externes
def get_links(soup, base_url):
    internal_links = set()
    external_links = set()
    for link in soup.find_all("a", href=True):
        href = link["href"]
        full_url = urljoin(base_url, href)
        if base_url in full_url:
            internal_links.add(full_url)
        else:
            external_links.add(full_url)
    return internal_links, external_links

# Fonction pour récupérer les images et vérifier les attributs alt
def get_images_info(soup):
    images = soup.find_all("img")
    image_data = []
    for img in images:
        src = img.get("src", "Pas de source")
        alt = img.get("alt", "Alt manquant")
        image_data.append({"src": src, "alt": alt})
    return image_data

# Fonction pour vérifier le fichier robots.txt
def check_robots_txt(url):
    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    robots_url = urljoin(base_url, "robots.txt")
    try:
        response = requests.get(robots_url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.text
        return "Fichier robots.txt introuvable ou inaccessible."
    except requests.RequestException as e:
        return f"Erreur lors de la récupération du robots.txt : {e}"

# Fonction principale Streamlit
def main():
    st.title("🔍 SEO Audit Tool")
    st.write("Entrez l'URL d'une page pour obtenir un audit SEO complet.")

    # Input pour l'URL
    url = st.text_input("🌐 URL de la page", placeholder="https://example.com")

    if st.button("Analyser") and url:
        with st.spinner("Analyse en cours..."):
            soup, status_code = fetch_page(url)

            if not soup:
                st.error("Impossible de récupérer la page. Vérifiez l'URL.")
                return

            st.subheader("🔎 Informations Générales")
            st.write(f"**Code HTTP :** {status_code}")

            # Meta information
            title, description, canonical_url = get_meta_info(soup)
            st.write(f"**Title :** {title}")
            st.write(f"**Meta Description :** {description}")
            st.write(f"**Canonical URL :** {canonical_url}")

            # HTTP Headers
            st.subheader("🛠️ En-têtes HTTP")
            headers, _ = get_http_headers(url)
            st.json(headers)

            # Images
            st.
