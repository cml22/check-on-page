import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json

# Fonction pour récupérer le contenu de la page
def fetch_page_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text, response.status_code, response.headers
    except requests.exceptions.RequestException as e:
        return None, None, str(e)

# Fonction pour analyser les méta-données
def analyze_meta(soup):
    meta_data = {
        "title": soup.title.string if soup.title else "Manquant",
        "description": soup.find("meta", attrs={"name": "description"})["content"] if soup.find("meta", attrs={"name": "description"}) else "Manquant",
        "canonical": soup.find("link", rel="canonical")["href"] if soup.find("link", rel="canonical") else "Manquant",
        "robots": soup.find("meta", attrs={"name": "robots"})["content"] if soup.find("meta", attrs={"name": "robots"}) else "Default: index, follow"
    }
    return meta_data

# Fonction pour analyser les images
def analyze_images(soup):
    images = []
    for img in soup.find_all("img"):
        img_src = img.get("src", "Manquant")
        alt_text = img.get("alt", "Alt manquant")
        images.append({"src": img_src, "alt": alt_text})
    return images

# Fonction pour analyser les liens (internes et externes)
def analyze_links(soup, base_url):
    internal_links = []
    external_links = []

    for link in soup.find_all("a", href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            internal_links.append(full_url)
        else:
            external_links.append(full_url)

    return internal_links, external_links

# Fonction pour vérifier les statuts des URLs
def check_url_status(urls):
    statuses = {}
    for url in urls:
        try:
            response = requests.head(url, timeout=5)
            statuses[url] = response.status_code
        except requests.RequestException:
            statuses[url] = "Erreur"
    return statuses

# Fonction pour recommandations SEO
def generate_recommendations(meta, images, links):
    recommendations = []
    
    # Recommandations META
    if len(meta.get("title", "")) > 60:
        recommendations.append("Le titre dépasse 60 caractères, pensez à le raccourcir.")
    if meta.get("description", "Manquant") == "Manquant":
        recommendations.append("La meta description est manquante.")
    
    # Recommandations Images
    for img in images:
        if img["alt"] == "Alt manquant":
            recommendations.append(f"Une image ({img['src']}) n'a pas d'attribut 'alt'.")
    
    # Recommandations Liens
    if len(links['internal']) == 0:
        recommendations.append("Aucun lien interne trouvé, pensez à améliorer le maillage interne.")
    if len(links['external']) > 50:
        recommendations.append("Trop de liens externes détectés, limitez-les pour éviter une fuite de SEO.")

    return recommendations

# Streamlit App
st.title("One-Pager SEO Tool")
st.write("Entrez une URL pour analyser ses performances SEO :")

# Entrée utilisateur
url = st.text_input("URL de la page :", "https://")

if st.button("Analyser"):
    with st.spinner("Analyse en cours..."):
        content, status_code, headers = fetch_page_content(url)

        if content:
            st.success("Contenu de la page récupéré avec succès !")
            
            # Parse le HTML
            soup = BeautifulSoup(content, "html.parser")
            
            # Analyse des META
            meta = analyze_meta(soup)
            st.subheader("🔍 Meta Informations")
            st.json(meta)
            
            # Analyse des Images
            images = analyze_images(soup)
            st.subheader("🖼️ Analyse des Images")
            st.write(f"Nombre d'images trouvées : {len(images)}")
            for img in images[:5]:
                st.write(f"Image: {img['src']}, Alt: {img['alt']}")
            
            # Analyse des Liens
            internal_links, external_links = analyze_links(soup, url)
            st.subheader("🔗 Liens")
            st.write(f"Liens internes : {len(internal_links)}")
            st.write(f"Liens externes : {len(external_links)}")
            
            # Vérification des statuts des liens
            link_statuses = check_url_status(internal_links + external_links)
            st.subheader("✅ Statuts des URLs")
            st.json(link_statuses)
            
            # Recommandations SEO
            recommendations = generate_recommendations(meta, images, {"internal": internal_links, "external": external_links})
            st.subheader("📝 Recommandations SEO")
            if recommendations:
                for rec in recommendations:
                    st.warning(rec)
            else:
                st.success("Tout semble bon, aucune recommandation !")
        else:
            st.error(f"Erreur lors de la récupération de la page : {status_code} {headers}")

