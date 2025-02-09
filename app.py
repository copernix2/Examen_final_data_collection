import streamlit as st
import pandas as pd
import os
import seaborn as sns
from scrapping import scraper  # Import du script de scraping
#import plotly.express as px  # Ajout pour des graphiques interactifs
import matplotlib.pyplot as plt
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

    # Vérifier si le fichier existe
    if not os.path.exists("dakar_auto_complet.csv"):
        st.warning("Aucune donnée disponible. Veuillez lancer le scraping.")
        return

    # Charger les données
    df = pd.read_csv("dakar_auto_complet.csv")

    # Convertir les prix en numérique
    df["prix"] = pd.to_numeric(df["prix"], errors="coerce")

    # Afficher un aperçu des données
    st.write("### 🔍 Aperçu des données")
    st.dataframe(df.head())

    # **Ajout des filtres**
    st.sidebar.header("🔎 Filtres")
    
    # Sélection de la catégorie
    categories = df["categorie"].unique().tolist()
    selected_category = st.sidebar.selectbox("📂 Catégorie", ["Toutes"] + categories)

    # Sélection de la marque
    marques = df["marque"].unique().tolist()
    selected_marque = st.sidebar.selectbox("🚗 Marque", ["Toutes"] + marques)

    # Sélection de la fourchette de prix
    min_price, max_price = int(df["prix"].min()), int(df["prix"].max())
    price_range = st.sidebar.slider("💰 Plage de prix (CFA)", min_price, max_price, (min_price, max_price))

    # **Filtrer les données**
    filtered_df = df.copy()
    if selected_category != "Toutes":
        filtered_df = filtered_df[filtered_df["categorie"] == selected_category]
    if selected_marque != "Toutes":
        filtered_df = filtered_df[filtered_df["marque"] == selected_marque]
    filtered_df = filtered_df[(filtered_df["prix"] >= price_range[0]) & (filtered_df["prix"] <= price_range[1])]

    # **Affichage des données filtrées**
    st.write("### 📌 Résultats après filtrage")
    st.dataframe(filtered_df)

    # **Visualisation des données**
    st.write("### 📊 Visualisation des données")
    # **Histogramme pour analyser la distribution des prix**
    st.write("### 📊 Distribution des Prix")    
    fig, ax = plt.subplots()
    sns.histplot(filtered_df["prix"], kde=True, ax=ax)
    ax.set_title("Distribution des Prix")
    st.pyplot(fig)

    # Graphique avec Seaborn
    st.write("### Statistiques des Prix")
    fig, ax = plt.subplots()
    sns.barplot(x=df["categorie"], y=df["prix"], ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.write("### Nombre d'annonces par catégorie")
    fig, ax = plt.subplots()
    sns.countplot(x=df["categorie"], ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    
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