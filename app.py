import streamlit as st
import requests
from bs4 import BeautifulSoup

# Fonction pour récupérer le contenu de la page
def fetch_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None, response.status_code
    except requests.exceptions.RequestException as e:
        return None, str(e)

# Interface utilisateur Streamlit
st.title('Analyseur de page web')

url = st.text_input("Entrez l'URL de la page à analyser")

if url:
    content = fetch_page(url)
    if content:
        st.write("Contenu de la page récupéré avec succès !")
    else:
        st.write("Erreur de récupération de la page.")
else:
    st.write("Veuillez entrer une URL.")
