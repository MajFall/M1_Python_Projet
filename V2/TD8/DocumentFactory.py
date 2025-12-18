# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 21:04:50 2025

@author: surface laptop 2
"""


#TD 5 PARTIE 4 : PATRONS DE CONCEPTION
# QUESTION 4.2 : Patron de conception d'usine (Factory Pattern)

from RedditDocument import RedditDocument
from ArxivDocument import ArxivDocument
from Document import Document

class DocumentFactory:
    """
    QUESTION 4.2 : Générateur de documents avec Factory Pattern
    Centralise la création des objets Document
    """
    
    @staticmethod
    def creer_reddit(titre, auteur, date, url, texte, nb_commentaires):
        """Factory method pour créer un document Reddit"""
        return RedditDocument(titre, auteur, date, url, texte, nb_commentaires)
    
    @staticmethod
    def creer_arxiv(titre, auteur_principal, date, url, texte, co_auteurs):
        """Factory method pour créer un document Arxiv"""
        return ArxivDocument(titre, auteur_principal, date, url, texte, co_auteurs)
    
    @staticmethod
    def creer_document_generique(titre, auteur, date, url, texte):
        """Factory method pour créer un document générique"""
        return Document(titre, auteur, date, url, texte)
    
    @staticmethod
    def creer_document(type_doc, *args, **kwargs):
        """
        QUESTION 4.2 : Méthode générique de factory
        Crée n'importe quel type de document en fonction du paramètre type_doc
        """
        if type_doc.lower() == "reddit":
            return DocumentFactory.creer_reddit(*args, **kwargs)
        elif type_doc.lower() == "arxiv":
            return DocumentFactory.creer_arxiv(*args, **kwargs)
        elif type_doc.lower() == "generique":
            return DocumentFactory.creer_document_generique(*args, **kwargs)
        else:
            raise ValueError(f"Type de document inconnu: {type_doc}")