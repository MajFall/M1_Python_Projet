# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 22:59:13 2025

@author: surface laptop 2
"""
#TD4
# Document.py

import pandas as pd
from datetime import datetime

#1.1
class Document:
    def __init__(self, titre, auteur, date, url, texte):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte
  
# 1.2         
    def afficher_infos(self):
        """Affiche toutes les informations du document"""
        print("=== Informations complètes du document ===")
        print(f"Titre: {self.titre}")
        print(f"Auteur: {self.auteur}")
        print(f"Date: {self.date}")
        print(f"URL: {self.url}")
        print(f"Texte (extrait): {self.texte[:100]}...")
        print("=" * 50)
    
    def __str__(self):
        """Version digeste - affiche seulement le titre"""
        return f"Document: '{self.titre}'"
    
