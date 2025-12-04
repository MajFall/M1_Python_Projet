# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 00:13:32 2025

@author: surface laptop 2
"""

# Author.py
#Partie 2
#2.1
class Author:
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = {}  # dictionnaire des documents
#2.2
    def add(self, document):
        """Ajoute un document à la production de l'auteur"""
        self.ndoc += 1
        self.production[self.ndoc] = document  # On utilise ndoc comme clé

    def __str__(self):
        return f"{self.name} - {self.ndoc} document(s)"