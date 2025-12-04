# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 21:04:50 2025

@author: surface laptop 2
"""

# TD 5 PARTIE 4 : PATRONS DE CONCEPTION
# QUESTION 4.1 : Patron de type Singleton pour le Corpus

from Corpus import Corpus

class CorpusSingleton:
    """
    QUESTION 4.1 : Implémentation du patron Singleton
    Garantit qu'une seule instance de Corpus existe dans l'application
    """
    _instance = None  # Variable de classe pour stocker l'instance unique
    
    def __new__(cls):
        """
        QUESTION 4.1 : Surcharge de __new__ pour contrôler la création d'instances
        """
        if cls._instance is None:
            # Première création de l'instance
            cls._instance = super().__new__(cls)
            # Initialisation de l'instance Corpus
            cls._instance.corpus = Corpus("Corpus Singleton Global")
        return cls._instance  # Retourne toujours la même instance
    
    def __getattr__(self, name):
        """
        Délégation des appels aux méthodes non définies vers l'instance corpus
        Permet d'utiliser CorpusSingleton comme un Corpus normal
        """
        return getattr(self.corpus, name)
    
    def __setattr__(self, name, value):
        """
        Contrôle de l'affectation des attributs
        """
        if name in ["_instance", "corpus"]:
            # Attributs spéciaux du Singleton
            super().__setattr__(name, value)
        else:
            # Délégation vers l'instance corpus
            setattr(self.corpus, name, value)
       
    # Ajout de la méthode __repr__ pour délégation     
    def __repr__(self):
         return repr(self.corpus)    
            
