# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 20:53:23 2025

@author: surface laptop 2
"""

# TD 5 PARTIE 1 : CLASSE RedditDocument


from Document import Document

class RedditDocument(Document):
    """
    Parie 1
    1.1 : Classe fille RedditDocument
    Hérite de Document et intègre une nouvelle variable typique aux documents Reddit
    """
    
    def __init__(self, titre, auteur, date, url, texte, nb_commentaires):
        # QUESTION 1.1 : Constructeur avec appel du constructeur de la classe mère
        super().__init__(titre, auteur, date, url, texte)  # Appel constructeur parent
        # Variable spécifique aux documents Reddit : nombre de commentaires
        self.nb_commentaires = nb_commentaires
    
    # QUESTION 1.1 : Accesseurs et mutateurs pour le champ spécifique
    def get_nb_commentaires(self):
        """Accesseur pour le nombre de commentaires"""
        return self.nb_commentaires
    
    def set_nb_commentaires(self, nouveau_nb):
        """Mutateur pour le nombre de commentaires"""
        self.nb_commentaires = nouveau_nb
    
    # TD5 QUESTION 3.2 : Méthode getType() pour identifier la source
    def getType(self):
        return "Reddit"
    
    # QUESTION 1.1 : Méthode spécifique pour l'affichage via __str__
    def __str__(self):
        return f"Reddit: '{self.titre}' - {self.nb_commentaires} commentaires"
    
    # Surcharge de la méthode d'affichage pour inclure les spécificités Reddit
    def afficher_infos(self):
        """Affiche toutes les informations du document Reddit"""
        print("=== Informations du document Reddit ===")
        super().afficher_infos()  # Appel de la méthode parente
        print(f"Nombre de commentaires: {self.nb_commentaires}")  # Info spécifique