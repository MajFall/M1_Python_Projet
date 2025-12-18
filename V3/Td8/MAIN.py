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
from SearchEngineTD8 import SearchEngineTD8

# === AJOUT TD6 ===
import re
import string
from collections import Counter
# === FIN AJOUT ===

# QUESTION 4.1 : Utilisation du Singleton pour le corpus
corpus = CorpusSingleton()  # Utilisez le Singleton au lieu de Corpus()


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
texte_test = "Python est SUPER! Avec 100% d'efficacité.\n"
print(f"Texte original:\n{texte_test}")
texte_propre = corpus.nettoyer_texte(texte_test)
print(f"\nTexte nettoyé:\n{texte_propre}")

# Statistiques du corpus
print("\n\n=== STATISTIQUES DU CORPUS (2.2-2.4) ===")
n_mots = input("Nombre de mots fréquents à afficher (défaut: 10): ").strip()
n_mots = int(n_mots) if n_mots.isdigit() else 10

df_stats = corpus.stats(n_mots)



# ===================================================================


print("\n" + "="*80)
print("TD6 TERMINÉ AVEC SUCCÈS!")
print("="*80)


# ===================================================================
# AJOUT TD7 - MOTEUR DE RECHERCHE 
# ===================================================================
print("\n\n" + "="*80)
print("TD7 - MOTEUR DE RECHERCHE")
print("="*80)

try:
    # Import de la classe SearchEngine
    from SearchEngine import SearchEngine
    
    print("Création du moteur de recherche...")
    
    # Création du moteur de recherche avec notre corpus existant
    moteur = SearchEngine(corpus)
    
    # Afficher les informations du corpus
    moteur.display_corpus_info()
    
    # Menu de recherche interactif
    while True:
        print("\n" + "="*50)
        print("MENU DE RECHERCHE TD7")
        print("="*50)
        print("1. Rechercher avec TF-IDF")
        print("2. Rechercher avec TF seulement")
        print("3. Afficher les statistiques du vocabulaire")
        print("4. Tester plusieurs requêtes pré-définies")
        print("5. Comparer TF vs TF-IDF")
        print("6. Quitter")
        
        choix = input("\nVotre choix (1-6): ").strip()
        
        if choix == "1" or choix == "2":
            # Recherche simple
            requete = input("Entrez votre requête de recherche: ").strip()
            if not requete:
                print("Requête vide, retour au menu.")
                continue
                
            k = input("Nombre de résultats (défaut: 5): ").strip()
            k = int(k) if k.isdigit() and int(k) > 0 else 5
            
            use_tfidf = (choix == "1")
            resultats = moteur.search(requete, k=k, use_tfidf=use_tfidf)
            
            if not resultats.empty:
                print(f"\n{len(resultats)} résultat(s) trouvé(s):")
                print("-" * 100)
                
                # Afficher les résultats de manière lisible
                for _, row in resultats.iterrows():
                    print(f"\nRang {row['rang']} (score: {row['score_similarite']:.4f})")
                    print(f"Titre: {row['titre']}")
                    print(f"Auteur: {row['auteur']} | Type: {row['type']} | Date: {row['date']}")
                    print(f"Aperçu: {row['aperçu']}")
                    print("-" * 100)
                
                # Option d'export
                exporter = input("\nExporter les résultats en CSV? (o/n): ").strip().lower()
                if exporter == 'o':
                    nom_fichier = input("Nom du fichier [resultats_recherche.csv]: ").strip()
                    nom_fichier = nom_fichier if nom_fichier else "resultats_recherche.csv"
                    resultats.to_csv(nom_fichier, index=False, encoding='utf-8')
                    print(f"Résultats exportés dans '{nom_fichier}'")
            else:
                print("Aucun résultat trouvé pour cette requête.")
                
        elif choix == "3":
            # Statistiques du vocabulaire
            n = input("Nombre de mots à afficher (défaut: 20): ").strip()
            n = int(n) if n.isdigit() and int(n) > 0 else 20
            
            vocab_stats = moteur.get_vocab_stats(n=n)
            
            print(f"\nTop {len(vocab_stats)} mots du vocabulaire:")
            print("-" * 60)
            print(f"{'Mot':<20} {'Occurrences':<15} {'Documents':<10}")
            print("-" * 60)
            
            for _, row in vocab_stats.iterrows():
                print(f"{row['mot'][:18]:<20} {row['occurrences_totales']:<15} {row['freq_document']:<10}")
            
            # Calculer quelques statistiques supplémentaires
            total_mots = vocab_stats['occurrences_totales'].sum()
            mots_uniques = len(vocab_stats)
            mots_plusieurs_docs = len(vocab_stats[vocab_stats['freq_document'] > 1])
            
            print(f"\nStatistiques:")
            print(f"  Total d'occurrences: {total_mots}")
            print(f"  Mots uniques: {mots_uniques}")
            print(f"  Mots dans plusieurs documents: {mots_plusieurs_docs}")
            print(f"  Taux de répétition: {total_mots/mots_uniques:.2f} occurrences/mot")
            
        elif choix == "4":
            # Tests pré-définis
            print("\n=== TESTS PRÉ-DÉFINIS ===")
            print("Sélectionnez une requête test:")
            print("1. 'python' (langage de programmation)")
            print("2. 'football' (thème principal)")
            print("3. 'machine learning' (thème scientifique)")
            print("4. 'chat chien' (animaux domestiques)")
            print("5. 'recherche' (général)")
            
            test_choix = input("Votre choix (1-5): ").strip()
            
            tests = {
                "1": "python",
                "2": "football",
                "3": "machine learning",
                "4": "chat chien",
                "5": "recherche"
            }
            
            if test_choix in tests:
                requete = tests[test_choix]
                print(f"\nRecherche: '{requete}'")
                
                # Test avec TF-IDF
                print("\n--- Résultats avec TF-IDF ---")
                resultats_tfidf = moteur.search(requete, k=3, use_tfidf=True)
                if not resultats_tfidf.empty:
                    for _, row in resultats_tfidf.iterrows():
                        print(f"  {row['rang']}. {row['titre']} (score: {row['score_similarite']:.4f})")
                else:
                    print("  Aucun résultat")
                
                # Test avec TF seulement
                print("\n--- Résultats avec TF seulement ---")
                resultats_tf = moteur.search(requete, k=3, use_tfidf=False)
                if not resultats_tf.empty:
                    for _, row in resultats_tf.iterrows():
                        print(f"  {row['rang']}. {row['titre']} (score: {row['score_similarite']:.4f})")
                else:
                    print("  Aucun résultat")
            
        elif choix == "5":
            # Comparaison TF vs TF-IDF
            print("\n=== COMPARAISON TF vs TF-IDF ===")
            requete = input("Entrez une requête pour comparer: ").strip()
            
            if requete:
                # TF
                print("\nMéthode TF (Term Frequency):")
                resultats_tf = moteur.search(requete, k=5, use_tfidf=False)
                if not resultats_tf.empty:
                    print("Résultats (premier document):")
                    premier_tf = resultats_tf.iloc[0]
                    print(f"  Titre: {premier_tf['titre']}")
                    print(f"  Score: {premier_tf['score_similarite']:.4f}")
                    print(f"  Auteur: {premier_tf['auteur']}")
                else:
                    print("  Aucun résultat")
                
                # TF-IDF
                print("\nMéthode TF-IDF (Term Frequency - Inverse Document Frequency):")
                resultats_tfidf = moteur.search(requete, k=5, use_tfidf=True)
                if not resultats_tfidf.empty:
                    print("Résultats (premier document):")
                    premier_tfidf = resultats_tfidf.iloc[0]
                    print(f"  Titre: {premier_tfidf['titre']}")
                    print(f"  Score: {premier_tfidf['score_similarite']:.4f}")
                    print(f"  Auteur: {premier_tfidf['auteur']}")
                    
                    # Comparaison des scores
                    if not resultats_tf.empty:
                        print("\nComparaison des scores du premier document:")
                        print(f"  TF: {premier_tf['score_similarite']:.4f}")
                        print(f"  TF-IDF: {premier_tfidf['score_similarite']:.4f}")
                        difference = abs(premier_tf['score_similarite'] - premier_tfidf['score_similarite'])
                        print(f"  Différence: {difference:.4f}")
                else:
                    print("  Aucun résultat")
                
                # Explication
                print("\nExplication:")
                print("  - TF: Compte seulement la fréquence des mots")
                print("  - TF-IDF: Poids les mots par leur rareté dans le corpus")
                print("  - TF-IDF est généralement meilleur pour ignorer les mots trop communs")
                
        elif choix == "6":
            print("Retour au menu principal...")
            break
            
        else:
            print("Choix invalide, veuillez réessayer.")
    
    print("\n" + "="*80)
    print("TD7 TERMINÉ AVEC SUCCÈS!")
    print("="*80)

except ImportError as e:
    print(f"\nErreur: Impossible d'importer SearchEngine")
  
except Exception as e:
    print(f"\nErreur lors de l'exécution d{e}")
    import traceback
    traceback.print_exc()

# ===================================================================
# RÉSUMÉ FINAL TD6 + TD7
# ===================================================================
print("\n\n" + "="*80)
print("RÉSUMÉ FINAL DES TD6 ET TD7")
print("="*80)

print(f"\nCorpus '{corpus.nom}' analysé avec succès!")
print(f"Nombre de documents: {corpus.ndoc}")
print(f"Nombre d'auteurs: {corpus.naut}")

if 'moteur' in locals():
    print(f"Moteur de recherche créé avec {len(moteur.vocab)} mots dans le vocabulaire")
    print(f"Matrices construites: TF ({moteur.mat_TF.shape}) et TF-IDF ({moteur.mat_TFxIDF.shape})")

print("\nFonctionnalités implémentées:")
print("✓ TD6: Recherche par motif et concordancier")
print("✓ TD6: Nettoyage de texte et statistiques")
print("✓ TD6: Vocabulaire et fréquences")
print("✓ TD7: Construction de matrices Documents x Termes")
print("✓ TD7: Calcul TF et TF-IDF")
print("✓ TD7: Similarité cosinus")
print("✓ TD7: Moteur de recherche complet avec classement")

print("\n" + "="*80)
print("PROJET COMPLET TERMINÉ!")
print("="*80)
