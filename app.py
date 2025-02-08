import streamlit as st
import pandas as pd
import os
from scrapping import scraper  # Import du script de scraping

# Configuration de l'application
st.set_page_config(page_title="Dakar Auto Scraper", layout="wide")

# Définition des pages disponibles
def main():
    st.sidebar.title("📌 Navigation")
    page = st.sidebar.radio("Aller à", ["📊 Dashboard", "📡 Scraper des données"])
    
    if page == "📊 Dashboard":
        dashboard()
    elif page == "📡 Scraper des données":
        scrape_page()

# --- PAGE 1 : DASHBOARD ---
def dashboard():
    st.title("📊 Dashboard des Données Scrappées")
    
    # Vérifier si les fichiers de données existent
    if os.path.exists("dakar_auto_complet.csv"):
        df = pd.read_csv("dakar_auto_complet.csv")
        df["prix"] = pd.to_numeric(df["prix"], errors="coerce")
        st.write("### Aperçu des données")
        st.dataframe(df.head())
        
        # Analyse des données
        st.write("### Statistiques des Prix")
        st.bar_chart(df.groupby("categorie")["prix"].mean())
        
        st.write("### Nombre d'annonces par catégorie")
        st.bar_chart(df["categorie"].value_counts())
    else:
        st.warning("Aucune donnée disponible. Veuillez lancer le scraping.")

# --- PAGE 2 : SCRAPER LES DONNÉES ---
def scrape_page():
    st.title("📡 Scraper les données")
    
    st.write("Sélectionnez les catégories et le nombre de pages à scraper")
    
    # Sélection des catégories
    categories = ["voitures", "motos", "locations"]
    selected_categories = st.multiselect("Choisissez les catégories à scraper", categories, default=["voitures"])
    
    # Sélection du nombre de pages
    num_pages = st.number_input("Nombre de pages à scraper par catégorie", min_value=1, max_value=100, value=5, step=1)
    
    if st.button("Lancer le Scraping"):
        with st.spinner("Scraping en cours... ⏳"):
            scraper(selected_categories, num_pages)
            st.success("Scraping terminé avec succès ! ✅")

        if os.path.exists("dakar_auto_complet.csv"):
            df = pd.read_csv("dakar_auto_complet.csv")
            st.write("### Aperçu des nouvelles données")
            st.dataframe(df.head())

if __name__ == "__main__":
    main()