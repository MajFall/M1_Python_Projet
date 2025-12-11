# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 20:56:45 2025

@author: surface laptop 2
"""

# TD5 PARTIE 2 : CLASSE ArxivDocument
# QUESTION 2.1 : Classe fille ArxivDocument qui hérite de Document

from Document import Document

class ArxivDocument(Document):
    """
    QUESTION 2.1 : Classe fille ArxivDocument
    Hérite de Document et intègre la gestion des co-auteurs
    """
    
    def __init__(self, titre, auteur_principal, date, url, texte, co_auteurs):
        # QUESTION 2.1 : Constructeur avec appel du constructeur de la classe mère
        super().__init__(titre, auteur_principal, date, url, texte)  # Appel constructeur parent
        # Variable spécifique aux documents Arxiv : liste des co-auteurs
        self.co_auteurs = co_auteurs if co_auteurs else []  # Liste vide par défaut
    
    # QUESTION 2.1 : Accesseurs et mutateurs pour le champ spécifique
    def get_co_auteurs(self):
        """Accesseur pour la liste des co-auteurs"""
        return self.co_auteurs
    
    def set_co_auteurs(self, nouveaux_co_auteurs):
        """Mutateur pour la liste des co-auteurs"""
        self.co_auteurs = nouveaux_co_auteurs
    
    def ajouter_co_auteur(self, co_auteur):
        """Méthode pour ajouter un co-auteur à la liste"""
        self.co_auteurs.append(co_auteur)
    
    # QUESTION 3.2 : Méthode getType() pour identifier la source
    def getType(self):
        return "Arxiv"
    
    # QUESTION 2.1 : Méthode spécifique pour l'affichage via __str__
    def __str__(self):
        co_auteurs_str = ", ".join(self.co_auteurs) if self.co_auteurs else "Aucun"
        return f"Arxiv: '{self.titre}' - Co-auteurs: {co_auteurs_str}"
    
    # Surcharge de la méthode d'affichage pour inclure les spécificités Arxiv
    def afficher_infos(self):
        """Affiche toutes les informations du document Arxiv"""
        print("=== Informations du document Arxiv ===")
        super().afficher_infos()  # Appel de la méthode parente
        print(f"Co-auteurs: {', '.join(self.co_auteurs) if self.co_auteurs else 'Aucun'}")  # Info spécifique