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
    page = st.sidebar.radio("Aller à", ["📊 Dashboard", "📡 Scraper des données", "📥 Télécharger les données", "📝 Évaluer l'application"])
    
    if page == "📊 Dashboard":
        dashboard()
    elif page == "📡 Scraper des données":
        scrape_page()
    elif page == "📥 Télécharger les données":
        download_page()
    elif page == "📝 Évaluer l'application":
        evaluation_page()

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

# --- PAGE 3 : TÉLÉCHARGER LES DONNÉES ---
def download_page():
    st.title("📥 Télécharger les données complètes")

    # Vérifier si le fichier de données existe
    data_file = "dakar_auto_complet.csv"

    if os.path.exists(data_file):
        df_complet = pd.read_csv(data_file)

        st.write("### 📊 Aperçu des données complètes")
        st.dataframe(df_complet.head())  # Affiche les 5 premières lignes

        # Bouton pour télécharger les données complètes
        st.download_button(
            label="📂 Télécharger les données complètes",
            data=df_complet.to_csv(index=False).encode("utf-8"),
            file_name="dakar_auto_complet.csv",
            mime="text/csv"
        )
    else:
        st.warning("🚨 Aucune donnée complète trouvée. Veuillez d'abord effectuer un scraping.")
def evaluation_page():
    st.markdown("[Formulaire sous Kobo](https://ee.kobotoolbox.org/x/XVoXZ2fJ)")
    st.title("📝 Évaluation de l'Application ")

    # Champs du formulaire
    nom = st.text_input("👤 Votre Nom")
    email = st.text_input("📧 Votre Email")
    satisfaction = st.slider("🌟 Niveau de Satisfaction (0 = Mauvais, 10 = Excellent)", 0, 10, 5)
    commentaire = st.text_area("✍️ Partagez votre avis")

    # Fichier où stocker les évaluations
    eval_file = "evaluations.csv"

    # Bouton d'envoi
    if st.button("📩 Envoyer l'évaluation"):
        eval_data = pd.DataFrame([[nom, email, satisfaction, commentaire]],
                                 columns=["Nom", "Email", "Satisfaction", "Commentaire"])
        
        if os.path.exists(eval_file):
            eval_data.to_csv(eval_file, mode='a', header=False, index=False, encoding="utf-8")
        else:
            eval_data.to_csv(eval_file, index=False, encoding="utf-8")

        st.success("✅ Merci pour votre retour ! Votre évaluation a été enregistrée.")

    # Vérifier si des évaluations existent
    if os.path.exists(eval_file):
        df_eval = pd.read_csv(eval_file)

        # Calcul du score moyen
        if not df_eval.empty:
            moyenne_satisfaction = df_eval["Satisfaction"].mean()
            st.subheader(f"🌟 Score moyen : {moyenne_satisfaction:.1f}/10")
            
            # Affichage des étoiles ⭐⭐⭐⭐⭐
            nb_etoiles = int(round(moyenne_satisfaction / 2))  # Convertir en étoiles sur 5
            st.write("⭐" * nb_etoiles + "☆" * (5 - nb_etoiles))  # Afficher les étoiles

            # Afficher toutes les évaluations
            st.write("### 📜 Évaluations des utilisateurs")
            st.dataframe(df_eval)

            # Bouton pour télécharger les évaluations
            st.download_button(
                label="📂 Télécharger les évaluations",
                data=df_eval.to_csv(index=False).encode("utf-8"),
                file_name="evaluations.csv",
                mime="text/csv"
            )
        else:
            st.warning("😞 Aucune évaluation enregistrée pour l'instant.")
    else:
        st.warning("📭 Aucune évaluation disponible. Soyez le premier à donner votre avis !")


if __name__ == "__main__":
    main()