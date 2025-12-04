# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 23:57:00 2025
@author: surface laptop 2
"""

from DocumentFactory import DocumentFactory
from CorpusSingleton import CorpusSingleton
from RedditDocument import RedditDocument
from ArxivDocument import ArxivDocument
import pandas as pd
from datetime import datetime

# QUESTION 4.1 : Utilisation du Singleton pour le corpus
corpus = CorpusSingleton()  #  Utilisez le Singleton au lieu de Corpus()

#%%
# Création d’un document Reddit
#Partie 1
#1.1
doc = RedditDocument(
    titre="Mon premier post",
    texte="Ceci est le contenu du post Reddit.",
    date=datetime.now(),
    nb_commentaires=42,
    auteur="Jacques",
    url=None
)

# Vérification des valeurs
print(doc.titre)
# %%
#Partie 2#2.1

    # Création d'un document Arxiv
doc = ArxivDocument(
        titre="Deep Learning for Vision",
        auteur_principal="Yann LeCun",
        date=datetime.now(),
        url="https://arxiv.org/abs/1234.5678",
        texte="Un article très intéressant sur le deep learning...",
        co_auteurs=["Geoffrey Hinton", "Yoshua Bengio"]
    )
    
    # Test affichage __str__
print("Test __str__ :")
print(doc)

    # Test getters
print("\nCo-auteurs actuels :", doc.get_co_auteurs())

    # Test ajouter co-auteur
doc.ajouter_co_auteur("Andrew Ng")
print("Après ajout :", doc.get_co_auteurs())

    # Test méthode héritée
print("\nTest getType() :", doc.getType())

    # Test méthode d'affichage complète
print("\nInfos détaillées :")
doc.afficher_infos()
#%%
import praw
reddit = praw.Reddit(client_id='rszoFwH_2YUIELX9D3FGWw',
                     client_secret='1t2sraMxx3vtC6_S9_4jW0aRNgCE9w',
                     user_agent='docs')

theme = "football"

print("Récupération des documents Reddit...")
print(f"{reddit} documents Reddit créés.")
#%%

#  AVEC LES NOUVELLES CLASSES
reddit_count = 0
for post in reddit.subreddit(theme).hot(limit=10):
    if post.selftext.strip():
        # QUESTION 4.2 : Création avec Factory Pattern
        doc = DocumentFactory.creer_reddit(
            titre=post.title,
            auteur=str(post.author) if post.author else "Inconnu",
            date=datetime.fromtimestamp(post.created_utc),
            url=f"https://reddit.com{post.permalink}",
            texte=post.selftext.replace("\n", " ").strip(),
            nb_commentaires=post.num_comments  # Spécificité Reddit
        )
        # QUESTION 3.1 : Ajout polymorphique
        corpus.add_document(doc)
        reddit_count += 1

print(f"{reddit_count} documents Reddit créés.")
print(f"{len(corpus.authors)} auteurs identifiés.")

# %%

import urllib.request
import xmltodict
import ssl, certifi

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

arxiv_count = 0
for entry in entries:
    auteurs = entry.get("author", [])
    if isinstance(auteurs, dict):
        auteur_nom = auteurs.get("name", "Inconnu")
        co_auteurs = []  # Spécificité Arxiv
    elif isinstance(auteurs, list):
        auteur_nom = auteurs[0].get("name", "Inconnu") if auteurs else "Inconnu"
        co_auteurs = [a.get("name", "Inconnu") for a in auteurs[1:]]  # ✅ Co-auteurs
    else:
        auteur_nom = "Inconnu"
        co_auteurs = []
    
    # QUESTION 4.2 : Création avec Factory Pattern
    doc = DocumentFactory.creer_arxiv(
        titre=entry["title"].replace("\n", " ").strip(),
        auteur_principal=auteur_nom,
        date=entry["published"],
        url=entry["id"],
        texte=entry["summary"].replace("\n", " ").strip(),
        co_auteurs=co_auteurs  # Spécificité Arxiv
    )
 #%%   
#Partie 3
    # QUESTION 3.1 : Ajout polymorphique
    corpus.add_document(doc)
    arxiv_count += 1

print(f"{arxiv_count} documents ArXiv créés.")  # Affichage spécifique ArXiv
print(f"Total documents créés: {corpus.ndoc}")
print(f"Total auteurs identifiés: {corpus.naut}")
#%%
# QUESTION 3.2 : Test avec affichage des types
print("\n=== TEST DES MÉTHODES AVEC TYPES ===")
print("Représentation du corpus:", corpus)

if corpus.ndoc > 0:
    premier_doc = list(corpus.id2doc.values())[0]
    print("\nPremier document:", premier_doc)
    premier_doc.afficher_infos()

# QUESTION 3.2 : Affichage avec sources
corpus.afficher_documents(tri="titre", n=10)
#%%

print("\n=== SAUVEGARDE EN DATAFRAME AVEC TYPES ===")
data = []
for doc_id, doc in corpus.id2doc.items():
   
    data.append({
        "id": doc_id,
        "titre": doc.titre,
        "auteur": doc.auteur,
        "date": str(doc.date),
        "url": doc.url,
        "texte": doc.texte,
        "type": doc.getType(),  #  Champ type via getType()
        "nb_commentaires": doc.get_nb_commentaires() if hasattr(doc, 'get_nb_commentaires') else 0,
        "co_auteurs": ", ".join(doc.get_co_auteurs()) if hasattr(doc, 'get_co_auteurs') else ""
    })

df = pd.DataFrame(data)
df.to_csv("documents_avec_types.tsv", sep="\t", index=False)

# Recharger pour vérifier
df_loaded = pd.read_csv("documents_avec_types.tsv", sep="\t")
print(f"DataFrame sauvegardé avec {len(df)} documents")
print("\nAperçu du DataFrame:")
print(df_loaded.head())

#  ANALYSE DU CORPUS AVEC TYPES
print("\n" + "="*50)
print("PARTIE 3 : ANALYSE DU CORPUS AVEC TYPES")
print("="*50)

#Taille du corpus par type
print("Taille du corpus :", len(df_loaded))
print("Répartition par type:")
print(df_loaded['type'].value_counts())

#  Nombre de mots et de phrases PAR TYPE
print("\nStatistiques par type de document:")
for doc_type in df_loaded['type'].unique():
    docs_type = df_loaded[df_loaded['type'] == doc_type]
    total_mots = sum(len(texte.split()) for texte in docs_type['texte'])
    total_phrases = sum(len(texte.split('.')) for texte in docs_type['texte'])
    print(f"{doc_type}: {len(docs_type)} docs, {total_mots} mots, {total_phrases} phrases")

# Suppression des documents trop courts
print(f"\nFiltrage des documents - avant: {len(df_loaded)} documents")
df_loaded = df_loaded[df_loaded["texte"].str.len() >= 20]
print(f"Après filtrage: {len(df_loaded)} documents (longueur >= 20 caractères)")

#  Création d'une chaîne unique
texte_total = " ".join(df_loaded["texte"].tolist())
mots_total = texte_total.split()

print(f"\n3.4 Chaîne unique créée:")
print(f"Longueur totale du texte fusionné : {len(texte_total)} caractères")
print(f"Nombre total de mots : {len(mots_total)}")
print(f"Nombre moyen de mots par document : {len(mots_total) / len(df_loaded):.1f}")

# STATISTIQUES AUTEUR AVEC TYPES
print("\n" + "="*50)
print("STATISTIQUES PAR AUTEUR AVEC TYPES")
print("="*50)

# Afficher les auteurs disponibles
print("Auteurs disponibles:")
auteurs_liste = list(corpus.authors.keys())
for i, nom in enumerate(auteurs_liste[:8], 1):
    print(f"{i}. {nom}")
if len(auteurs_liste) > 8:
    print("...")

# Utilisation de la méthode du corpus pour les statistiques
if auteurs_liste:
    nom_auteur = input("\nEntrez le nom d'un auteur: ")
    corpus.statistiques_auteur(nom_auteur)

# Affichage de tous les documents AVEC TYPES
print("\n=== LISTE DE TOUS LES DOCUMENTS AVEC TYPES ===")
for doc_id, doc in corpus.id2doc.items():
    print(f"ID {doc_id}: {doc} ({doc.getType()})")  # Affichage du type

# Statistiques finales avec types
print("\n=== STATISTIQUES AVEC TYPES ===")
print(f"Nombre total de documents: {corpus.ndoc}")
print(f"Nombre total d'auteurs: {corpus.naut}")

#  Utilisation de getType() au lieu de la détection par URL
doc_reddit = len([doc for doc in corpus.id2doc.values() if doc.getType() == "Reddit"])
doc_arxiv = len([doc for doc in corpus.id2doc.values() if doc.getType() == "Arxiv"])

print(f"- Documents Reddit: {doc_reddit}")
print(f"- Documents ArXiv: {doc_arxiv}")

total_mots = sum(len(doc.texte.split()) for doc in corpus.id2doc.values())
print(f"Nombre total de mots: {total_mots}")

#%%
# QUESTION 4.1 : Test du Singleton
print("\n=== TEST SINGLETON ===")
corpus2 = CorpusSingleton()
print(f"Les deux variables pointent vers la même instance : {corpus is corpus2}")
print(f"Nombre de documents dans corpus2 : {corpus2.ndoc}")
#%%
# QUESTION 4.2 : Test de la Factory
print("\n=== TEST FACTORY PATTERN ===")
doc_test = DocumentFactory.creer_reddit(
    "Test Factory",
    "TestUser", 
    "2024-01-18",
    "https://test.com",
    "Texte de test",
    25
)
print(f"Document créé via factory: {doc_test}")

doc3 = DocumentFactory.creer_document(
    "generique",
    "Titre",
    "Auteur",
    "2025-08-10",
    "url",
    "texte"
)
print(f"Document Générique créé via factory: {doc3}")