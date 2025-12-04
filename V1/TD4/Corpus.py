# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 00:28:06 2025

@author: surface laptop 2
"""
#Partie 3
#3.1 Creation de la classe campus
# Corpus.py
import pandas as pd
from Document import Document
from Author import Author
from datetime import datetime


class Corpus:
    def __init__(self, nom):
        self.nom = nom
        self.authors = {}
        self.id2doc = {}
        self.ndoc = 0
        self.naut = 0
#Partie 1
#1.3
    def add_document(self, titre, auteur, date, url, texte):
        """Ajoute un document au corpus et gère l'auteur associé"""
        doc_id = self.ndoc + 1
        document = Document(titre, auteur, date, url, texte)
        self.id2doc[doc_id] = document
        self.ndoc += 1

#Partioe 2
#2.3
        # Ajout ou mise à jour de l'auteur
        if auteur not in self.authors:
            self.authors[auteur] = Author(auteur)
            self.naut += 1
        self.authors[auteur].add(document)
#Partie 3
#3.2 Methode d affichage digeste du corpus
    def __repr__(self):
        return f"Corpus {self.nom} : {self.ndoc} docs, {self.naut} auteurs"
#   Methode tri par titre ou date
    def afficher_documents(self, tri="id", n=5):
        """Affiche les n premiers documents du corpus"""
        docs = list(self.id2doc.values())
        if tri == "titre":
            docs.sort(key=lambda x: x.titre.lower())
        elif tri == "date":
            # Fonction pour convertir les dates en datetime
            def to_datetime(date_value):
                if isinstance(date_value, datetime):
                    return date_value
                try:
                    # Conversion d'une chaîne ISO ou ArXiv (finissant par Z)
                    return datetime.fromisoformat(str(date_value).replace("Z", ""))
                except Exception:
                    # Si échec, renvoyer une date très ancienne
                    return datetime.min
    
            docs.sort(key=lambda x: to_datetime(x.date))
    
        print(f"\n=== {n} premiers documents (tri: {tri}) ===")
        for doc in docs[:n]:
            print(f"- {doc.titre} ({doc.date})")
#2.4    
    def statistiques_auteur(self, nom_auteur):
        """Affiche les statistiques pour un auteur donné"""
        if nom_auteur in self.authors:
            auteur = self.authors[nom_auteur]
            
            print(f"\n=== STATISTIQUES POUR {auteur.name} ===")
            print(f"Nombre de documents produits: {auteur.ndoc}")
            
            # Taille moyenne des documents (en mots)
            total_mots = 0
            for doc_id, document in auteur.production.items():
                mots = len(document.texte.split())
                total_mots += mots
            
            if auteur.ndoc > 0:
                moyenne_mots = total_mots / auteur.ndoc
                print(f"Taille moyenne des documents: {moyenne_mots:.1f} mots")
                
                # Affichage des titres des documents
                print(f"\nDocuments de {auteur.name}:")
                for doc_id, doc in auteur.production.items():
                    print(f"- {doc.titre}")
            else:
                print("Aucun document pour calculer la taille moyenne")
        else:
            print(f"Auteur '{nom_auteur}' non trouvé.")