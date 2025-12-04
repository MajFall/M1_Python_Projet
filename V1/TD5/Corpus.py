# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 00:28:06 2025

@author: surface laptop 2
"""



# TD 5 PARTIE 3 : MISE À JOUR DE LA CLASSE CORPUS

import pandas as pd
from Document import Document
from Author import Author
#TD5
from RedditDocument import RedditDocument
from ArxivDocument import ArxivDocument

class Corpus:
    def __init__(self, nom):
        self.nom = nom
        self.authors = {}
        self.id2doc = {}
        self.ndoc = 0
        self.naut = 0

    #TD5  QUESTION 3.1 : Méthode polymorphique pour ajouter des documents
    def add_document(self, document):
        """
        QUESTION 3.1 : Méthode polymorphique
        Accepte tout type de Document (RedditDocument, ArxivDocument, Document)
        Le polymorphisme permet cette opération sans modifier la méthode
        """
        doc_id = self.ndoc + 1
        self.id2doc[doc_id] = document  # Stockage du document
        self.ndoc += 1

        # Gestion des auteurs (existant)
        if document.auteur not in self.authors:
            self.authors[document.auteur] = Author(document.auteur)
            self.naut += 1
        self.authors[document.auteur].add(document)
   
    def afficher_documents(self, tri="id", n=9):
        """
        QUESTION 3.2 : Affichage avec la source
        Affiche la liste des articles avec leur source (Reddit ou Arxiv)
        """
        docs = list(self.id2doc.values())
        if tri == "titre":
            docs.sort(key=lambda x: x.titre.lower())
        elif tri == "date":
            docs.sort(key=lambda x: x.date)
        
        print(f"\n=== {n} premiers documents (tri: {tri}) ===")
        for i, doc in enumerate(docs[:n], 1):
            # QUESTION 3.2 : Affichage du type via getType()
            print(f"{i}. {doc} ({doc.getType()})")  # Affiche le type de document
     
    def __repr__(self):
        return f"Corpus {self.nom} : {self.ndoc} docs, {self.naut} auteurs"
    
    def statistiques_auteur(self, nom_auteur):
        """Affiche les statistiques pour un auteur donné"""
        if nom_auteur in self.authors:
            auteur = self.authors[nom_auteur]
            
            print(f"\n=== STATISTIQUES POUR {auteur.name} ===")
            print(f"Nombre de documents produits: {auteur.ndoc}")
            
            # QUESTION 3.2 : Statistiques par type de document
            types_docs = {}
            for doc_id, document in auteur.production.items():
                doc_type = document.getType()  # Utilisation de getType()
                if doc_type not in types_docs:
                    types_docs[doc_type] = 0
                types_docs[doc_type] += 1
            
            print("Répartition par type:")
            for doc_type, count in types_docs.items():
                print(f"  - {doc_type}: {count} document(s)")
            
            # Taille moyenne des documents (existant)
            total_mots = 0
            for doc_id, document in auteur.production.items():
                mots = len(document.texte.split())
                total_mots += mots
            
            if auteur.ndoc > 0:
                moyenne_mots = total_mots / auteur.ndoc
                print(f"Taille moyenne des documents: {moyenne_mots:.1f} mots")
                
                # QUESTION 3.2 : Affichage des documents avec leur type
                print(f"\nDocuments de {auteur.name}:")
                for doc_id, doc in auteur.production.items():
                    print(f"- {doc.titre} ({doc.getType()})")  # Affiche le type
            else:
                print("Aucun document pour calculer la taille moyenne")
        else:
            print(f"Auteur '{nom_auteur}' non trouvé.")
    
    # QUESTION 3.2 : Méthode pour filtrer par type de document
    def get_documents_par_type(self, type_doc):
        """Retourne les documents d'un type spécifique"""
        return [doc for doc in self.id2doc.values() if doc.getType() == type_doc]
    
    def afficher_stats(self):
        """Affiche des statistiques sur le corpus"""
        print(f"=== Statistiques du corpus: {self.nom} ===")
        print(f"Total documents: {self.ndoc}")
        
        # QUESTION 3.2 : Utilisation de getType() pour les statistiques
        documents_reddit = self.get_documents_par_type("Reddit")
        documents_arxiv = self.get_documents_par_type("Arxiv")
        documents_generiques = self.get_documents_par_type("Document générique")
        
        print(f"Documents Reddit: {len(documents_reddit)}")
        print(f"Documents Arxiv: {len(documents_arxiv)}")
        print(f"Documents génériques: {len(documents_generiques)}")
        print(f"Nombre d'auteurs uniques: {len(self.authors)}")