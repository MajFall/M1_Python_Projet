# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 18:22:09 2025

@author: madji
"""




# Importation des classes
from Document import Document
from Author import Author
from Corpus import Corpus
import pandas as pd
from datetime import datetime

# Création du corpus 
corpus = Corpus("CorpusFootball")

# %%
import praw
reddit = praw.Reddit(client_id='rszoFwH_2YUIELX9D3FGWw',
                     client_secret='1t2sraMxx3vtC6_S9_4jW0aRNgCE9w',
                     user_agent='docs')

theme = "football"

#Partie 1
#1.3
print("Récupération des documents Reddit...")
for post in reddit.subreddit(theme).hot(limit=10):
    if post.selftext.strip():
        # Utilisation de la méthode du corpus
        corpus.add_document(
            titre=post.title,
            auteur=str(post.author) if post.author else "Inconnu",
            date=datetime.fromtimestamp(post.created_utc),
            url=f"https://reddit.com{post.permalink}",
            texte=post.selftext.replace("\n", " ").strip()
        )

print(f"{corpus.ndoc} documents Reddit créés.")
print(f"{corpus.naut} auteurs identifiés.")


import urllib.request
import xmltodict
import ssl, certifi
#  Thème de recherche
theme = "football"

#  Requête à l'API ArXiv (version HTTPS)
url = f"https://export.arxiv.org/api/query?search_query=all:{theme}&start=0&max_results=5"

#  Contexte SSL sécurisé (utilise les certificats certifi)
context = ssl.create_default_context(cafile=certifi.where())

# Récupération des données XML depuis ArXiv
with urllib.request.urlopen(url, context=context) as response:
    data = response.read()
feed = xmltodict.parse(data)
entries = feed["feed"]["entry"]
if isinstance(entries, dict):
    entries = [entries]

for entry in entries:
    auteurs = entry.get("author", [])
    if isinstance(auteurs, dict):
        auteur_nom = auteurs.get("name", "Inconnu")
    elif isinstance(auteurs, list):
        auteur_nom = ", ".join([a.get("name", "Inconnu") for a in auteurs])
    else:
        auteur_nom = "Inconnu"
    
    # Utilisation de la méthode du corpus
    corpus.add_document(
        titre=entry["title"].replace("\n", " ").strip(),
        auteur=auteur_nom,
        date=entry["published"],
        url=entry["id"],
        texte=entry["summary"].replace("\n", " ").strip()
    )

print(f"Total documents créés: {corpus.ndoc}")
print(f"Total auteurs identifiés: {corpus.naut}")


# Test des méthodes
print("\n=== TEST DES MÉTHODES ===")
print("Représentation du corpus:", corpus)

if corpus.ndoc > 0:
    premier_doc = list(corpus.id2doc.values())[0]
    print("\nPremier document:", premier_doc)
    premier_doc.afficher_infos()
#%%
#3.2
# Test de l'affichage des documents
corpus.afficher_documents(tri="titre", n=3)
corpus.afficher_documents(tri="date", n=3)
#%%

# : sauvegarde en DataFrame
print("\n=== SAUVEGARDE EN DATAFRAME ===")
data = []
for doc_id, doc in corpus.id2doc.items():
    origine = "reddit" if "reddit" in doc.url else "arxiv"
    
    data.append({
        "id": doc_id,
        "titre": doc.titre,
        "auteur": doc.auteur,
        "date": str(doc.date),
        "url": doc.url,
        "texte": doc.texte,
        "origine": origine
    })

df = pd.DataFrame(data)
df.to_csv("documents_avec_metadonnees.tsv", sep="\t", index=False)

# Recharger pour vérifier
df_loaded = pd.read_csv("documents_avec_metadonnees.tsv", sep="\t")
print(f"DataFrame sauvegardé avec {len(df)} documents")
print("\nAperçu du DataFrame:")
print(df_loaded.head())


# PARTIE 3 : ANALYSE DU CORPUS
print("\n" + "="*50)
print("PARTIE 3 : ANALYSE DU CORPUS")
print("="*50)

# Taille du corpus
print("Taille du corpus :", len(df_loaded))

# Nombre de mots et de phrases
print("\n Statistiques par document:")
for i, row in df_loaded.iterrows():
    mots = row["texte"].split(" ")  
    phrases = row["texte"].split(".")  
    print(f"Doc {row['id']} ({row['origine']}) → {len(mots)} mots, {len(phrases)} phrases")

# Suppression des documents trop courts
print("\n Filtrage des documents - avant: {len(df_loaded)} documents")
df_loaded = df_loaded[df_loaded["texte"].str.len() >= 20]
print(f"Après filtrage: {len(df_loaded)} documents (longueur >= 20 caractères)")

#  Création d'une chaîne unique
texte_total = " ".join(df_loaded["texte"].tolist())
mots_total = texte_total.split()

print(f"\n3.4 Chaîne unique créée:")
print(f"Longueur totale du texte fusionné : {len(texte_total)} caractères")
print(f"Nombre total de mots : {len(mots_total)}")
print(f"Nombre moyen de mots par document : {len(mots_total) / len(df_loaded):.1f}")


print("\n" + "="*50)
print("STATISTIQUES PAR AUTEUR")
print("="*50)
#%%
# Afficher les auteurs disponibles
print("Auteurs disponibles:")
auteurs_liste = list(corpus.authors.keys())
for i, nom in enumerate(auteurs_liste[:8], 1):
    print(f"{i}. {nom}")
if len(auteurs_liste) > 8:
    print("...")
#%%
#Partie 2
#2.4
# Utilisation de la méthode du corpus pour les statistiques
nom_auteur = input("\nEntrez le nom d'un auteur: ")
corpus.statistiques_auteur(nom_auteur)
#%%

# Affichage de tous les documents
print("\n=== LISTE DE TOUS LES DOCUMENTS ===")
for doc_id, doc in corpus.id2doc.items():
    print(f"ID {doc_id}: {doc}")


# Statistiques finales
print("\n=== STATISTIQUES ===")
print(f"Nombre total de documents: {corpus.ndoc}")
print(f"Nombre total d'auteurs: {corpus.naut}")

doc_reddit = sum(1 for doc in corpus.id2doc.values() if "reddit" in doc.url)
doc_arxiv = sum(1 for doc in corpus.id2doc.values() if "arxiv" in doc.url)
print(f"- Documents Reddit: {doc_reddit}")
print(f"- Documents ArXiv: {doc_arxiv}")

total_mots = sum(len(doc.texte.split()) for doc in corpus.id2doc.values())
print(f"Nombre total de mots: {total_mots}")

