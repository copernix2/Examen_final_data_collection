import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Définition des URL pour chaque catégorie
CATEGORIES = {
   "voitures": {
        "url": "https://dakar-auto.com/senegal/voitures-4?&page=",
        "columns": ["marque", "annee", "prix", "adresse", "kilometrage", "boite_vitesse", "carburant", "proprietaire"],
    },
     "motos": {
        "url": "https://dakar-auto.com/senegal/motos-and-scooters-3?&page=",
        "columns": ["marque", "annee", "prix", "adresse", "kilometrage", "proprietaire"],
    },
    
   "locations": {
        "url": "https://dakar-auto.com/senegal/location-de-voitures-19?&page=",
        "columns": ["marque", "annee", "prix", "adresse", "proprietaire"],
    }
    }
# Fonction de nettoyage des valeurs
def clean_value(value):
    if value:
        return value.strip().replace("\u202f", "").replace(",,", ",")
    return None

# Fonction de scraping pour une catégorie donnée
def scrape_category(category_name, url_base, columns):
    data = []
    page = 1  # Commencer à la première page

    print(f"Démarrage du scraping pour la catégorie {category_name}...")
    
    while True:
        url = f"{url_base}{page}"
        print(f"📄 Scraping {category_name} - Page {page}...")

        # Requête HTTP avec User-Agent pour éviter d'être détecté comme bot
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"🔴 Fin du scraping pour {category_name} (plus de pages disponibles).")
            break

        # Parser le HTML avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        annonces = soup.find_all("div", class_="listings-cards__list-item")

        if not annonces:
            print(f"⚠️ Aucune annonce trouvée pour {category_name}, fin du scraping.")
            break

        # Extraction des informations
        for annonce in annonces:
            try:
                # Marque et Année
                titre_elem = annonce.find("h2", class_="listing-card__header__title").find("a")
                titre = titre_elem.text.strip() if titre_elem else None
                marque = titre.split()[0] if titre else None  # Première partie du titre = marque
                annee = titre.split()[-1] if titre and titre.split()[-1].isdigit() else None

                # Prix
                prix_elem = annonce.find("h3", class_="listing-card__header__price")
                prix = prix_elem.text.strip().replace("F CFA", "").replace("\u202f", "").strip() if prix_elem else None

                # Adresse
                quartier_elem = annonce.find("span", class_="town-suburb")
                ville_elem = annonce.find("span", class_="province")
                adresse = f"{quartier_elem.text.strip()} {ville_elem.text.strip()}" if quartier_elem and ville_elem else None

                # Kilométrage (si disponible)
                  # Kilométrage, boîte de vitesse et carburant
                kilometrage, boite_vitesse, carburant = None, None, None
                
                for attrib in annonce.find_all("li", class_="listing-card__attribute"):
                    text = clean_value(attrib.get_text(strip=True))  # Récupérer uniquement le texte sans icônes
                    
                    if "km" in text:
                        kilometrage = text.replace("km", "").strip()
                    elif "Automatique" in text or "Manuelle" in text:
                        boite_vitesse = text.strip()
                    elif "Essence" in text or "Diesel" in text:
                        carburant = text.strip()                
                
                # Propriétaire
                proprietaire_elem = annonce.find("a", style="color:#0f3081; text-decoration: none;")
                proprietaire = proprietaire_elem.text.replace("Par ", "").strip() if proprietaire_elem else None

                # Construire la ligne de données en respectant le nombre exact de colonnes
                row = [marque, annee, prix, adresse]
                if "kilometrage" in columns:
                    row.append(kilometrage)
                if "boite_vitesse" in columns:
                    row.append(boite_vitesse)
                if "carburant" in columns:
                    row.append(carburant)
                row.append(proprietaire)
                
                # Vérifier que la ligne correspond au nombre de colonnes
                if len(row) == len(columns):
                    data.append(row)
                else:
                    print(f"⚠️ Problème de correspondance des colonnes pour {category_name}: {row}")

                
            except Exception as e:
                print(f"⚠️ Erreur sur une annonce : {e}")
                continue

        page += 1
        print(f"✅ Page {page - 1} terminée. Passage à la suivante...")
        time.sleep(2)  # Pause pour éviter d'être bloqué

    print(f"✅ Fin du scraping pour {category_name}. {len(data)} annonces récupérées.")
    # Convertir en DataFrame Pandas
    df = pd.DataFrame(data, columns=columns)
    return df

# Fonction principale pour scraper toutes les catégories
def scraper_all():
    print("🚀 Début du scraping pour toutes les catégories...")
    all_data = {}

    for category, info in CATEGORIES.items():
        df = scrape_category(category, info["url"], info["columns"])
        all_data[category] = df

        # Sauvegarder chaque catégorie séparément
        filename = f"{category}_scrapees_all.csv"
        df.to_csv(filename, index=False)
        print(f"💾 Données enregistrées dans {filename}")

    # Fusionner toutes les données
    df_combined = pd.concat(all_data.values(), keys=all_data.keys(), names=["categorie"])
    df_combined.to_csv("dakar_auto_complet_all.csv", index=True)
    print("🎯 Scraping terminé et fichier consolidé sauvegardé sous 'dakar_auto_complet.csv'.")

# Fonction de scraping
def scraper(selected_categories, num_pages):
    print("🚀 Début du scraping...")
    all_data = {}

    for category in selected_categories:
        info = CATEGORIES.get(category)
        if not info:
            print(f"⚠️ Catégorie inconnue : {category}")
            continue

        data = []
        page = 1

        print(f"📄 Scraping {category}...")
        while page <= num_pages:
            url = f"{info['url']}{page}"
            print(f"🔍 Scraping page {page} de {category}...")
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

            if response.status_code != 200:
                print(f"❌ Fin du scraping pour {category} (erreur HTTP {response.status_code}).")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            annonces = soup.find_all("div", class_="listings-cards__list-item")

            if not annonces:
                print(f"⚠️ Aucune annonce trouvée pour {category}, fin du scraping.")
                break

            for annonce in annonces:
                try:
                    titre_elem = annonce.find("h2", class_="listing-card__header__title").find("a")
                    titre = clean_value(titre_elem.text) if titre_elem else None
                    marque = titre.split()[0] if titre else None
                    annee = titre.split()[-1] if titre and titre.split()[-1].isdigit() else None

                    prix_elem = annonce.find("h3", class_="listing-card__header__price")
                    prix = clean_value(prix_elem.text.replace("F CFA", "")) if prix_elem else None

                    quartier_elem = annonce.find("span", class_="town-suburb")
                    ville_elem = annonce.find("span", class_="province")
                    adresse = clean_value(f"{quartier_elem.text}, {ville_elem.text}") if quartier_elem and ville_elem else None

                    kilometrage, boite_vitesse, carburant = None, None, None
                    for attrib in annonce.find_all("li", class_="listing-card__attribute"):
                        text = clean_value(attrib.get_text(strip=True))
                        if "km" in text:
                            kilometrage = text.replace("km", "").strip()
                        elif "Automatique" in text or "Manuelle" in text:
                            boite_vitesse = text.strip()
                        elif "Essence" in text or "Diesel" in text:
                            carburant = text.strip()

                    proprietaire_elem = annonce.find("a", style="color:#0f3081; text-decoration: none;")
                    proprietaire = clean_value(proprietaire_elem.text.replace("Par ", "")) if proprietaire_elem else None

                    row = [marque, annee, prix, adresse]
                    if "kilometrage" in info["columns"]:
                        row.append(kilometrage)
                    if "boite_vitesse" in info["columns"]:
                        row.append(boite_vitesse)
                    if "carburant" in info["columns"]:
                        row.append(carburant)
                    row.append(proprietaire)
                    
                    if len(row) == len(info["columns"]):
                        data.append(row)
                    else:
                        print(f"⚠️ Problème de colonnes pour {category}: {row}")

                except Exception as e:
                    print(f"⚠️ Erreur sur une annonce : {e}")
                    continue

            page += 1
            time.sleep(2)

        print(f"✅ Fin du scraping pour {category}. {len(data)} annonces récupérées.")
        df = pd.DataFrame(data, columns=info["columns"])
        df.to_csv(f"{category}_scrapees.csv", index=False)
        all_data[category] = df

    df_combined = pd.concat(all_data.values(), keys=all_data.keys(), names=["categorie"])
    df_combined.to_csv("dakar_auto_complet.csv", index=True)
    print("🎯 Scraping terminé et fichier consolidé sauvegardé sous 'dakar_auto_complet.csv'.")
