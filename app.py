import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

# User-Agent pour éviter les blocages
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

# Vérifie si une URL est bloquée par robots.txt
def check_robots_txt(base_url):
    robots_url = urljoin(base_url, "/robots.txt")
    try:
        response = requests.get(robots_url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except Exception:
        return None

# Récupère les données de la page
def fetch_page_content(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text, response.status_code, response.headers
    except Exception as e:
        st.error(f"Erreur : {e}")
        return None, None, None

# Analyse META : Title, Description, Canonical, Robots, Hreflangs
def analyze_meta(soup):
    meta_data = {
        "Title": soup.title.string if soup.title else "Manquant",
        "Meta Description": soup.find("meta", attrs={"name": "description"})["content"] if soup.find("meta", attrs={"name": "description"}) else "Manquant",
        "Canonical": soup.find("link", rel="canonical")["href"] if soup.find("link", rel="canonical") else "Manquant",
        "Robots": soup.find("meta", attrs={"name": "robots"})["content"] if soup.find("meta", attrs={"name": "robots"}) else "Default: index, follow"
    }
    # Hreflangs
    hreflangs = [link['hreflang'] + " -> " + link['href'] for link in soup.find_all("link", rel="alternate", hreflang=True)]
    meta_data["Hreflangs"] = hreflangs if hreflangs else "Aucun hreflang trouvé"
    return meta_data

# Analyse des images
def analyze_images(soup):
    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "Manquant")
        alt = img.get("alt", "Alt manquant")
        images.append({"src": src, "alt": alt})
    return images

# Analyse des liens (internes et externes)
def analyze_links(soup, base_url):
    internal_links, external_links = set(), set()
    for link in soup.find_all("a", href=True):
        href = urljoin(base_url, link["href"])
        if urlparse(base_url).netloc in href:
            internal_links.add(href)
        else:
            external_links.add(href)
    return internal_links, external_links

# Vérification des données structurées
def check_structured_data(soup):
    scripts = [script.string for script in soup.find_all("script", type="application/ld+json")]
    return scripts if scripts else "Aucune donnée structurée trouvée"

# Génération des liens vers outils externes
def generate_external_tools_links(url):
    tools = {
        "Schema Markup Validator": f"https://validator.schema.org/?url={url}",
        "Rich Results Test": f"https://search.google.com/test/rich-results?url={url}",
        "Google PageSpeed Insights": f"https://pagespeed.web.dev/?url={url}",
        "Google Search Console (Performance)": f"https://search.google.com/search-console?resource_id={url}",
    }
    return tools

# Streamlit App
st.title("🚀 SEO Audit Tool - Analyse complète d'une URL")
st.write("Entrez une URL pour effectuer un audit SEO complet.")

# Input utilisateur
url = st.text_input("URL de la page :", "")

if st.button("Analyser"):
    with st.spinner("Analyse en cours..."):
        # Vérification du contenu de la page
        content, status_code, headers = fetch_page_content(url)
        if content:
            st.success(f"Page récupérée avec succès ! Statut HTTP : {status_code}")
            soup = BeautifulSoup(content, "html.parser")

            # Meta Information
            st.header("🔍 Informations META")
            meta = analyze_meta(soup)
            st.json(meta)

            # Images
            st.header("🖼️ Analyse des Images")
            images = analyze_images(soup)
            st.write(f"Nombre total d'images : {len(images)}")
            for img in images[:5]:
                st.write(f"Image : {img['src']}, Alt : {img['alt']}")

            # Liens internes et externes
            st.header("🔗 Liens Internes et Externes")
            internal, external = analyze_links(soup, url)
            st.write(f"Liens internes : {len(internal)} | Liens externes : {len(external)}")

            # Statuts des liens
            st.subheader("✅ Statuts des Liens Externes")
            external_status = {link: requests.head(link, headers=HEADERS).status_code for link in list(external)[:10]}
            st.json(external_status)

            # Données structurées
            st.header("🛠️ Données Structurées")
            structured_data = check_structured_data(soup)
            st.json(structured_data)

            # Robots.txt
            st.header("🤖 Vérification robots.txt")
            robots_txt = check_robots_txt(url)
            if robots_txt:
                st.text(robots_txt)
            else:
                st.warning("Aucun fichier robots.txt trouvé.")

            # Outils Externes
            st.header("🔗 Outils SEO Externes")
            tools = generate_external_tools_links(url)
            for tool, link in tools.items():
                st.markdown(f"[{tool}]({link})")

