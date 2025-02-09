import streamlit as st
import pandas as pd
import os
from scrapping import scraper  # Import du script de scraping
import plotly.express as px  # Ajout pour des graphiques interactifs
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

    # **Graphiques interactifs**
    st.write("### 📊 Analyse des Prix")

    # Graphique avec Plotly
    fig = px.histogram(filtered_df, x="prix", nbins=30, title="Répartition des Prix")
    st.plotly_chart(fig)

    # **Nombre d'annonces par catégorie**
    st.write("### 📈 Nombre d'annonces par catégorie")
    category_counts = df["categorie"].value_counts()
    fig = px.bar(category_counts, x=category_counts.index, y=category_counts.values, title="Nombre d'annonces par catégorie")
    st.plotly_chart(fig)

    # **Prix moyen par catégorie**
    st.write("### 💰 Prix moyen par catégorie")
    avg_prices = df.groupby("categorie")["prix"].mean().sort_values(ascending=False)
    fig = px.bar(avg_prices, x=avg_prices.index, y=avg_prices.values, title="Prix moyen des véhicules par catégorie")
    st.plotly_chart(fig)

    # **Boîte à moustaches pour analyser la répartition des prix**
    st.write("### 📊 Distribution des Prix par Catégorie")
    fig = px.box(filtered_df, x="categorie", y="prix", title="Distribution des Prix par Catégorie")
    st.plotly_chart(fig)
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