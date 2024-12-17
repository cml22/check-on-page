import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import datetime
from urllib.parse import urlparse

# Fonction pour récupérer le contenu de la page et son code de statut
def fetch_page(url):
    try:
        # Effectuer une requête GET pour récupérer le contenu de la page
        response = requests.get(url, timeout=10)  # Timeout de 10 secondes
        # Vérifier si la requête a été réussie
        if response.status_code == 200:
            return response.text, response.status_code, response.headers
        else:
            return None, response.status_code, response.headers
    except requests.exceptions.RequestException as e:
        # En cas d'erreur, retourner None et l'erreur
        return None, None, str(e)

# Exemple d'utilisation de la fonction fetch_page
if __name__ == "__main__":
    url = "http://exemple.com"
    content, status, headers = fetch_page(url)
    if content:
        st.write("Contenu récupéré avec succès")
        st.write(content)
        st.write("Code de statut:", status)
        st.write("En-têtes:", headers)
    else:
        st.write("Erreur de récupération de la page. Statut:", status)
        st.write("Erreur:", headers)
