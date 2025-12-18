# Corpus.py - Classe complète avec TD5 et TD6

from Document import Document
from Author import Author

import re
import pandas as pd
import numpy as np
from collections import Counter
import string

class Corpus:
    def __init__(self, nom):
        self.nom = nom
        self.authors = {}
        self.id2doc = {}
        self.ndoc = 0
        self.naut = 0
        
        # Attributs pour le TD6
        self.texte_integral = None
        self.vocabulaire = None
        self._df_freq = None
    
    # === Méthodes TD5 ===
    
   # def add_document(self, document):
    #    """TD5 - Ajout polymorphique de document"""
     #   doc_id = self.ndoc + 1
      #  self.id2doc[doc_id] = document
       # self.ndoc += 1

#        if document.auteur not in self.authors:
 #           self.authors[document.auteur] = Author(document.auteur)
  #          self.naut += 1
   #     self.authors[document.auteur].add(document)
        
    def add_document(self, titre, auteur, date, url, texte):
        """Ajoute un document au corpus et gère l'auteur associé"""
        doc_id = self.ndoc + 1
        document = Document(titre, auteur, date, url, texte)
        self.id2doc[doc_id] = document
        self.ndoc += 1
    


        
        if auteur not in self.authors:
            self.authors[auteur] = Author(auteur)  
            self.naut += 1
        
        # Ajout du document à l'auteur
        self.authors[auteur].add(document)
    
    
    
    def afficher_documents(self, tri="id", n=9):
        """TD5 - Affichage des documents avec leur type"""
        docs = list(self.id2doc.values())
        if tri == "titre":
            docs.sort(key=lambda x: x.titre.lower())
        elif tri == "date":
            docs.sort(key=lambda x: x.date)
        
        print(f"\n=== {n} premiers documents (tri: {tri}) ===")
        for i, doc in enumerate(docs[:n], 1):
            # Affiche le type de document
            print(f"{i}. {doc} ({doc.getType()})")
    
    def statistiques_auteur(self, nom_auteur):
        """TD5 - Statistiques pour un auteur donné"""
        if nom_auteur in self.authors:
            auteur = self.authors[nom_auteur]
            
            print(f"\n=== STATISTIQUES POUR {auteur.name} ===")
            print(f"Nombre de documents produits: {auteur.ndoc}")
            
            # Statistiques par type de document
            types_docs = {}
            for doc_id, document in auteur.production.items():
                doc_type = document.getType()
                if doc_type not in types_docs:
                    types_docs[doc_type] = 0
                types_docs[doc_type] += 1
            
            print("Répartition par type:")
            for doc_type, count in types_docs.items():
                print(f"  - {doc_type}: {count} document(s)")
            
            # Taille moyenne des documents
            total_mots = 0
            for doc_id, document in auteur.production.items():
                mots = len(document.texte.split())
                total_mots += mots
            
            if auteur.ndoc > 0:
                moyenne_mots = total_mots / auteur.ndoc
                print(f"Taille moyenne des documents: {moyenne_mots:.1f} mots")
                
                # Affichage des documents avec leur type
                print(f"\nDocuments de {auteur.name}:")
                for doc_id, doc in auteur.production.items():
                    print(f"- {doc.titre} ({doc.getType()})")
            else:
                print("Aucun document pour calculer la taille moyenne")
        else:
            print(f"Auteur '{nom_auteur}' non trouvé.")
    
    def __repr__(self):
        return f"Corpus {self.nom} : {self.ndoc} docs, {self.naut} auteurs"
    
    # === Méthodes TD6 ===
    
    def _get_texte_integral(self):
        """1.1 - Construit le texte intégral une seule fois"""
        if self.texte_integral is None:
            textes = []
            for doc_id, document in self.id2doc.items():
                texte = getattr(document, 'texte', '') or getattr(document, 'contenu', '')
                textes.append(texte)
            self.texte_integral = " ".join(textes)
        return self.texte_integral
    
    def search(self, motif):
        """1.1 - Recherche un motif dans tous les documents"""
        texte = self._get_texte_integral()
        pattern = re.compile(re.escape(motif), re.IGNORECASE)
        matches = []
        
        for match in pattern.finditer(texte):
            start = max(0, match.start() - 100)
            end = min(len(texte), match.end() + 100)
            contexte = texte[start:end]
            
            if start > 0:
                contexte = "..." + contexte
            if end < len(texte):
                contexte = contexte + "..."
                
            matches.append({
                'position': match.start(),
                'contexte': contexte,
                'motif_trouve': match.group()
            })
        
        return matches
    
    def concorde(self, expression, contexte=30):
        """1.2 - Crée un concordancier"""
        texte = self._get_texte_integral()
        
        try:
            pattern = re.compile(expression, re.IGNORECASE)
        except re.error:
            pattern = re.compile(re.escape(expression), re.IGNORECASE)
        
        results = []
        
        for match in pattern.finditer(texte):
            start_gauche = max(0, match.start() - contexte)
            contexte_gauche = texte[start_gauche:match.start()]
            if start_gauche > 0:
                contexte_gauche = "..." + contexte_gauche
            
            motif_trouve = match.group()
            
            end_droit = min(len(texte), match.end() + contexte)
            contexte_droit = texte[match.end():end_droit]
            if end_droit < len(texte):
                contexte_droit = contexte_droit + "..."
            
            results.append({
                'contexte gauche': contexte_gauche,
                'motif trouve': motif_trouve,
                'contexte droit': contexte_droit
            })
        
        df = pd.DataFrame(results)
        if not df.empty:
            df = df[['contexte gauche', 'motif trouve', 'contexte droit']]
        
        return df
    
    @staticmethod
    def nettoyer_texte(texte):
        """2.1 - Nettoie un texte"""
        if not isinstance(texte, str):
            return ""
        
        texte = texte.lower()
        texte = texte.replace('\n', ' ').replace('\r', ' ')
        
        # Supprimer la ponctuation
        ponctuation = string.punctuation + '«»"\''
        traducteur = str.maketrans('', '', ponctuation)
        texte = texte.translate(traducteur)
        
        # Supprimer les chiffres
        texte = re.sub(r'\d+', '', texte)
        
        # Supprimer les espaces multiples
        texte = re.sub(r'\s+', ' ', texte).strip()
        
        return texte
    
    def construire_vocabulaire(self):
        """2.2 et 2.3 - Construit le vocabulaire et compte les fréquences"""
        if self.vocabulaire is not None and self._df_freq is not None:
            return self.vocabulaire, self._df_freq
        
        freq_globale = Counter()
        doc_freq = Counter()
        
        for doc_id, document in self.id2doc.items():
            texte_brut = getattr(document, 'texte', '') or getattr(document, 'contenu', '')
            texte_propre = self.nettoyer_texte(texte_brut)
            mots = texte_propre.split()
            
            freq_doc = Counter(mots)
            freq_globale.update(freq_doc)
            
            for mot in set(mots):
                doc_freq[mot] += 1
        
        self.vocabulaire = set(freq_globale.keys())
        
        self._df_freq = pd.DataFrame({
            'mot': list(freq_globale.keys()),
            'term_frequency': list(freq_globale.values()),
            'document_frequency': [doc_freq[mot] for mot in freq_globale.keys()]
        })
        
        self._df_freq = self._df_freq.sort_values('term_frequency', ascending=False).reset_index(drop=True)
        
        return self.vocabulaire, self._df_freq
    
    def stats(self, n=10):
        """2.4 - Affiche les statistiques textuelles"""
        vocab, df_freq = self.construire_vocabulaire()
        
        print(f"\n=== STATISTIQUES TEXTUELLES DU CORPUS: {self.nom} ===")
        print(f"Nombre total de documents: {self.ndoc}")
        print(f"Nombre de mots différents: {len(vocab)}")
        
        total_mots = df_freq['term_frequency'].sum()
        print(f"Nombre total de mots: {total_mots}")
        
        if len(vocab) > 0:
            freq_moyenne = total_mots / len(vocab)
            print(f"Fréquence moyenne par mot: {freq_moyenne:.2f}")
        
        print(f"\nTop {n} mots les plus fréquents:")
        print("-" * 50)
        print(f"{'Mot':<20} {'Fréquence':<15} {'%':<10} {'Docs':<10}")
        print("-" * 50)
        
        top_n = df_freq.head(n)
        for _, row in top_n.iterrows():
            pourcentage = (row['term_frequency'] / total_mots) * 100 if total_mots > 0 else 0
            docs_avec_mot = row['document_frequency']
            print(f"{row['mot'][:18]:<20} {row['term_frequency']:<15} {pourcentage:.2f}%{'':<5} {docs_avec_mot:<10}")
        
        return df_freq
    
    
    def search_mots(self, mots, n_context=50):
    
      if isinstance(mots, str):
        mots = [mots]
    
      all_results = []
      for mot in mots:
           df_concorde = self.concorde(mot, contexte=n_context)
           if not df_concorde.empty:
               df_concorde['mot_recherche'] = mot
               all_results.append(df_concorde)
    
      if all_results:
        return pd.concat(all_results, ignore_index=True)
        return pd.DataFrame()