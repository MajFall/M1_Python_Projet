# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 18:12:47 2025

@author: surface laptop 2
"""

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

# === AJOUT TD6 ===
import re
import string
from collections import Counter
# === FIN AJOUT ===

# QUESTION 4.1 : Utilisation du Singleton pour le corpus
corpus = CorpusSingleton()  # Utilisez le Singleton au lieu de Corpus()

#%%
# Création d'un document Reddit
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
#%%

# AVEC LES NOUVELLES CLASSES
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

# Requête à l'API ArXiv (version HTTPS)
url = f"https://export.arxiv.org/api/query?search_query=all:{theme}&start=0&max_results=5"

# Contexte SSL sécurisé (utilise les certificats certifi)
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
    
    # QUESTION 3.1 : Ajout polymorphique
    corpus.add_document(doc)
    arxiv_count += 1

print(f"{arxiv_count} documents ArXiv créés.")
print(f"Total documents créés: {corpus.ndoc}")
print(f"Total auteurs identifiés: {corpus.naut}")

#%%
# QUESTION 3.2 : Test avec affichage des types
print("\n=== TEST DES MÉTHODES AVEC TYPES ===")
print("Représentation du corpus:", corpus)

if corpus.ndoc > 0:
    premier_doc = list(corpus.id2doc.values())[0]
    print("\nPremier document:", premier_doc)
    if hasattr(premier_doc, 'afficher_infos'):
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
        "type": doc.getType(),  # Champ type via getType()
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

# ANALYSE DU CORPUS AVEC TYPES
print("\n" + "="*50)
print("PARTIE 3 : ANALYSE DU CORPUS AVEC TYPES")
print("="*50)

#Taille du corpus par type
print("Taille du corpus :", len(df_loaded))
print("Répartition par type:")
print(df_loaded['type'].value_counts())

# Nombre de mots et de phrases PAR TYPE
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

# Création d'une chaîne unique
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

# Utilisation de getType() au lieu de la détection par URL
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

# ===================================================================
# AJOUT TD6 - PARTIE 1 : EXPRESSIONS RÉGULIÈRES
# ===================================================================
print("\n" + "="*80)
print("TD6 - PARTIE 1 : EXPRESSIONS RÉGULIÈRES")
print("="*80)

# Test de la recherche
print("\n=== TEST RECHERCHE (1.1) ===")
motif_recherche = input("Entrez un motif à rechercher dans le corpus: ").strip()
if motif_recherche:
    resultats_recherche = corpus.search(motif_recherche)
    print(f"\nNombre d'occurrences trouvées pour '{motif_recherche}': {len(resultats_recherche)}")
    
    if resultats_recherche:
        print("\nLes 3 premières occurrences:")
        for i, res in enumerate(resultats_recherche[:3], 1):
            print(f"\n{i}. Position {res['position']}:")
            print(f"   Contexte: {res['contexte']}")
        
        if len(resultats_recherche) > 3:
            print(f"\n... et {len(resultats_recherche) - 3} autre(s) résultat(s)")
    else:
        print("Aucune occurrence trouvée.")

# Test du concordancier
print("\n\n=== TEST CONCORDANCIER (1.2) ===")
expression = input("Entrez une expression pour le concordancier: ").strip()
if expression:
    contexte = input("Taille du contexte (défaut: 30): ").strip()
    contexte = int(contexte) if contexte.isdigit() else 30
    
    df_concorde = corpus.concorde(expression, contexte)
    
    if not df_concorde.empty:
        print(f"\n{len(df_concorde)} concordance(s) trouvée(s) pour '{expression}':")
        
        # Afficher le DataFrame
        print("\nTableau des concordances:")
        print(df_concorde[['contexte gauche', 'motif trouve', 'contexte droit']].to_string(index=False))
        
        # Option de sauvegarde
        sauver = input("\nSauvegarder en CSV? (o/n): ").strip().lower()
        if sauver == 'o':
            nom_fichier = input("Nom du fichier [concordances.csv]: ").strip()
            nom_fichier = nom_fichier if nom_fichier else "concordances.csv"
            df_concorde.to_csv(nom_fichier, index=False, encoding='utf-8')
            print(f"Fichier '{nom_fichier}' sauvegardé.")
    else:
        print(f"Aucune concordance trouvée pour '{expression}'.")

# ===================================================================
# AJOUT TD6 - PARTIE 2 : STATISTIQUES TEXTUELLES
# ===================================================================
print("\n\n" + "="*80)
print("TD6 - PARTIE 2 : STATISTIQUES TEXTUELLES")
print("="*80)

# Test de nettoyage
print("\n=== TEST NETTOYAGE DE TEXTE (2.1) ===")
texte_test = "Python 3.10 est SUPER! Avec 100% d'efficacité.\nNouvelle ligne ici."
print(f"Texte original:\n{texte_test}")
texte_propre = corpus.nettoyer_texte(texte_test)
print(f"\nTexte nettoyé:\n{texte_propre}")

# Statistiques du corpus
print("\n\n=== STATISTIQUES DU CORPUS (2.2-2.4) ===")
n_mots = input("Nombre de mots fréquents à afficher (défaut: 10): ").strip()
n_mots = int(n_mots) if n_mots.isdigit() else 10

df_stats = corpus.stats(n_mots)

# Options supplémentaires
print("\nOptions supplémentaires:")
print("a. Afficher les mots rares (fréquence ≤ 2)")
print("b. Rechercher un mot spécifique")
print("c. Exporter les statistiques en CSV")
print("d. Afficher la distribution des fréquences")
print("e. Continuer")

opt = input("Votre choix (a/b/c/d/e): ").strip().lower()

if opt == 'a':
    seuil = input("Seuil de fréquence maximale [2]: ").strip()
    seuil = int(seuil) if seuil.isdigit() else 2
    mots_rares = df_stats[df_stats['term_frequency'] <= seuil]
    print(f"\nMots avec ≤ {seuil} occurrence(s) ({len(mots_rares)} mots):")
    print(mots_rares[['mot', 'term_frequency', 'document_frequency']].to_string(index=False))
    
elif opt == 'b':
    mot_recherche = input("Mot à rechercher dans les statistiques: ").strip().lower()
    if mot_recherche in df_stats['mot'].values:
        ligne = df_stats[df_stats['mot'] == mot_recherche].iloc[0]
        print(f"\nStatistiques pour '{mot_recherche}':")
        print(f"  Fréquence totale: {ligne['term_frequency']}")
        print(f"  Nombre de documents: {ligne['document_frequency']} sur {corpus.ndoc}")
        
        # Chercher les contextes
        print(f"\nExemples d'occurrences:")
        df_contextes = corpus.concorde(mot_recherche, contexte=20)
        if not df_contextes.empty:
            for idx, row in df_contextes.head(3).iterrows():
                print(f"  - ...{row['contexte gauche'][-15:]}>>>{row['motif trouve']}<<<{row['contexte droit'][:15]}...")
        else:
            print("  Aucun contexte trouvé.")
    else:
        print(f"'{mot_recherche}' non trouvé dans le vocabulaire.")
        
elif opt == 'c':
    nom_fichier = input("Nom du fichier CSV [statistiques_corpus.csv]: ").strip()
    nom_fichier = nom_fichier if nom_fichier else "statistiques_corpus.csv"
    df_stats.to_csv(nom_fichier, index=False, encoding='utf-8')
    print(f"Statistiques sauvegardées dans '{nom_fichier}'")
    
elif opt == 'd':
    print("\nDistribution des fréquences:")
    print("=" * 50)
    
    # Calculer différentes catégories
    total_mots = df_stats['term_frequency'].sum()
    mots_uniques = len(df_stats[df_stats['term_frequency'] == 1])
    mots_2_5 = len(df_stats[(df_stats['term_frequency'] >= 2) & (df_stats['term_frequency'] <= 5)])
    mots_5_plus = len(df_stats[df_stats['term_frequency'] > 5])
    
    print(f"Total de mots (tokens): {total_mots}")
    print(f"Total de mots uniques (types): {len(df_stats)}")
    print(f"\nRépartition:")
    print(f"  - Mots avec 1 occurrence: {mots_uniques} ({mots_uniques/len(df_stats)*100:.1f}% du vocabulaire)")
    print(f"  - Mots avec 2-5 occurrences: {mots_2_5} ({mots_2_5/len(df_stats)*100:.1f}%)")
    print(f"  - Mots avec >5 occurrences: {mots_5_plus} ({mots_5_plus/len(df_stats)*100:.1f}%)")
    
    # Mots apparaissant dans plusieurs documents
    mots_multi_docs = df_stats[df_stats['document_frequency'] > 1]
    print(f"\nMots apparaissant dans plusieurs documents: {len(mots_multi_docs)}")
    
    # Richesse lexicale
    richesse = len(df_stats) / total_mots * 100 if total_mots > 0 else 0
    print(f"Richesse lexicale (types/tokens): {richesse:.2f}%")

# ===================================================================
# AJOUT TD6 - RECHERCHE AVANCÉE
# ===================================================================
print("\n\n" + "="*80)
print("RECHERCHE AVANCÉE")
print("="*80)

# Recherche multiple
print("\n=== RECHERCHE MULTIPLE ===")
mots_input = input("Entrez plusieurs mots à rechercher (séparés par des virgules): ").strip()
if mots_input:
    mots_recherche = [mot.strip() for mot in mots_input.split(',')]
    
    print(f"\nRecherche de {len(mots_recherche)} mot(s): {', '.join(mots_recherche)}")
    
    for mot in mots_recherche:
        resultats = corpus.search(mot)
        print(f"\n'{mot}': {len(resultats)} occurrence(s)")
        
        if resultats:
            # Afficher un exemple
            exemple = resultats[0]
            print(f"  Exemple: ...{exemple['contexte'][:50]}...")
    
    # Option pour un concordancier combiné
    combiner = input("\nCréer un concordancier combiné? (o/n): ").strip().lower()
    if combiner == 'o':
        df_multi = corpus.search_mots(mots_recherche, n_context=25)
        if not df_multi.empty:
            print(f"\nConcordancier combiné ({len(df_multi)} résultats):")
            print(df_multi[['mot_recherche', 'motif trouve', 'contexte gauche', 'contexte droit']].to_string(index=False))
            
            # Sauvegarde
            sauver = input("\nSauvegarder les résultats? (o/n): ").strip().lower()
            if sauver == 'o':
                nom_fichier = input("Nom du fichier [recherche_combinee.csv]: ").strip()
                nom_fichier = nom_fichier if nom_fichier else "recherche_combinee.csv"
                df_multi.to_csv(nom_fichier, index=False, encoding='utf-8')
                print(f"Résultats sauvegardés dans '{nom_fichier}'")

# ===================================================================
# RÉSUMÉ FINAL
# ===================================================================
print("\n\n" + "="*80)
print("RÉSUMÉ FINAL DU TD6")
print("="*80)

# Affichage des capacités du corpus
print(f"\nCapacités d'analyse textuelle du corpus '{corpus.nom}':")
print(f"1. Recherche par motif: {corpus.ndoc} documents indexés")
print(f"2. Vocabulaire: {len(corpus.vocabulaire) if hasattr(corpus, 'vocabulaire') and corpus.vocabulaire else 'Non calculé'} mots uniques")
print(f"3. Concordancier: prêt à utiliser")

# Export final
print("\nOptions d'export disponibles:")
print("1. Données brutes des documents (déjà exporté)")
print("2. Statistiques du vocabulaire")
print("3. Concordances")
print("4. Tout exporter")

export_choice = input("\nChoix d'export (1-4, Enter pour passer): ").strip()

if export_choice == "1":
    # Exporter à nouveau les documents
    df_docs = pd.DataFrame([
        {
            "id": doc_id,
            "titre": doc.titre,
            "auteur": doc.auteur,
            "type": doc.getType(),
            "mots": len(doc.texte.split())
        }
        for doc_id, doc in corpus.id2doc.items()
    ])
    df_docs.to_csv("export_documents.csv", index=False, encoding='utf-8')
    print("Documents exportés dans 'export_documents.csv'")
    
elif export_choice == "2":
    # Exporter les statistiques
    if df_stats is not None:
        df_stats.to_csv("export_statistiques.csv", index=False, encoding='utf-8')
        print("Statistiques exportées dans 'export_statistiques.csv'")
        
elif export_choice == "3":
    # Exporter les concordances pour un mot
    mot_export = input("Mot pour l'export des concordances: ").strip()
    if mot_export:
        df_concorde_export = corpus.concorde(mot_export, 30)
        if not df_concorde_export.empty:
            df_concorde_export.to_csv(f"concordances_{mot_export}.csv", index=False, encoding='utf-8')
            print(f"Concordances pour '{mot_export}' exportées dans 'concordances_{mot_export}.csv'")
            
elif export_choice == "4":
    # Tout exporter
    import os
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dossier = f"export_td6_{timestamp}"
    os.makedirs(dossier, exist_ok=True)
    
    # Documents
    df_docs_complet = pd.DataFrame([
        {
            "id": doc_id,
            "titre": doc.titre,
            "auteur": doc.auteur,
            "date": str(doc.date),
            "type": doc.getType(),
            "texte": doc.texte[:500] + "..." if len(doc.texte) > 500 else doc.texte,
            "mots": len(doc.texte.split())
        }
        for doc_id, doc in corpus.id2doc.items()
    ])
    df_docs_complet.to_csv(f"{dossier}/documents.csv", index=False, encoding='utf-8')
    
    # Statistiques
    df_stats.to_csv(f"{dossier}/statistiques.csv", index=False, encoding='utf-8')
    
    # Concordances pour les mots fréquents
    mots_frequents = df_stats.head(5)['mot'].tolist()
    for mot in mots_frequents:
        df_mot = corpus.concorde(mot, 30)
        if not df_mot.empty:
            df_mot.to_csv(f"{dossier}/concordances_{mot}.csv", index=False, encoding='utf-8')
    
    print(f"\nToutes les données exportées dans le dossier '{dossier}'")
    print(f"Contenu: documents.csv, statistiques.csv, concordances_*.csv")

print("\n" + "="*80)
print("TD6 TERMINÉ AVEC SUCCÈS!")
print("="*80)