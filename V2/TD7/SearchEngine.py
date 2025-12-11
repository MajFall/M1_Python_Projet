# SearchEngine.py - Version corrigée

import numpy as np
import pandas as pd
from scipy import sparse
import math
from collections import defaultdict
import re
from typing import List, Dict, Tuple

class SearchEngine:
    """
    Moteur de recherche basé sur TF-IDF et similarité cosinus - TD7
    """
    
    def __init__(self, corpus):
        """
        Initialise le moteur de recherche avec un corpus de documents
        
        Args:
            corpus: Objet Corpus du TD6 (ou CorpusSingleton)
        """
        self.corpus = corpus
        # Extraire les textes de tous les documents
        self.texts = self._extract_texts()
        # Utiliser ndoc au lieu de len() pour CorpusSingleton
        self.n_docs = corpus.ndoc  # CHANGEMENT ICI
        
        # Structures de données pour le moteur
        self.vocab = {}  # Dictionnaire du vocabulaire
        self.mat_TF = None  # Matrice Term Frequency
        self.mat_TFxIDF = None  # Matrice TF-IDF
        self.word_to_id = {}  # Mapping mot -> index
        
        # Construire le vocabulaire et les matrices
        print("Construction du vocabulaire...")
        self._build_vocabulary()
        print("Construction de la matrice TF...")
        self._build_TF_matrix()
        print("Construction de la matrice TF-IDF...")
        self._build_TFxIDF_matrix()
    
    def _extract_texts(self):
        """Extrait les textes de tous les documents du corpus"""
        texts = []
        # Parcourir tous les documents du corpus
        for doc_id, document in self.corpus.id2doc.items():
            # Extraire le texte selon la structure des documents
            texte = getattr(document, 'texte', '') or getattr(document, 'contenu', '')
            if texte:
                texts.append(texte)
        return texts
    
    def _clean_text(self, text: str) -> List[str]:
        """
        Nettoie un texte en utilisant la méthode du Corpus
        
        Args:
            text: Texte à nettoyer
            
        Returns:
            Liste de tokens normalisés
        """
        # Utiliser la méthode nettoyer_texte du Corpus
        texte_propre = self.corpus.nettoyer_texte(text)
        # Tokenisation
        tokens = texte_propre.split()
        return tokens
    
    def _build_vocabulary(self):
        """1.1 - Construit le vocabulaire à partir du corpus"""
        all_tokens = []
        
        # Collecter tous les tokens de tous les documents
        print(f"  Analyse de {self.n_docs} documents...")
        for i, doc in enumerate(self.texts):
            tokens = self._clean_text(doc)
            all_tokens.extend(tokens)
        
        # Supprimer les doublons et trier par ordre alphabétique
        unique_tokens = sorted(set(all_tokens))
        
        print(f"  Vocabulaire: {len(unique_tokens)} mots uniques")
        
        # Construire le vocabulaire avec des informations supplémentaires
        for idx, token in enumerate(unique_tokens):
            self.vocab[token] = {
                'id': idx,
                'total_occurrences': 0,
                'doc_frequency': 0  # Nombre de documents contenant le mot
            }
            self.word_to_id[token] = idx
    
    def _build_TF_matrix(self):
        """1.2 - Construit la matrice Term Frequency (Documents x Termes)"""
        n_words = len(self.vocab)
        
        # Initialiser les listes pour la matrice creuse COO (Coordinate Format)
        data = []
        rows = []
        cols = []
        
        print(f"  Dimensions: {self.n_docs} documents x {n_words} mots")
        
        # Pour chaque document, compter les occurrences de chaque mot
        for doc_id, doc in enumerate(self.texts):
            tokens = self._clean_text(doc)
            
            # Compter les occurrences dans ce document
            doc_word_counts = defaultdict(int)
            for token in tokens:
                if token in self.word_to_id:
                    word_id = self.word_to_id[token]
                    doc_word_counts[word_id] += 1
            
            # Ajouter aux listes pour la matrice creuse
            for word_id, count in doc_word_counts.items():
                data.append(count)
                rows.append(doc_id)
                cols.append(word_id)
        
        # Créer la matrice creuse au format CSR comme demandé
        self.mat_TF = sparse.csr_matrix((data, (rows, cols)), 
                                        shape=(self.n_docs, n_words))
        
        # Mettre à jour les informations du vocabulaire
        self._update_vocab_stats()
    
    def _update_vocab_stats(self):
        """1.3 - Met à jour les statistiques du vocabulaire"""
        n_words = len(self.vocab)
        
        # Calculer le nombre total d'occurrences pour chaque mot
        total_occurrences = self.mat_TF.sum(axis=0).A1  # .A1 pour convertir en array 1D
        
        # Calculer le nombre de documents contenant chaque mot
        doc_frequency = (self.mat_TF > 0).sum(axis=0).A1
        
        # Mettre à jour le vocabulaire
        for word, info in self.vocab.items():
            word_id = info['id']
            info['total_occurrences'] = total_occurrences[word_id]
            info['doc_frequency'] = doc_frequency[word_id]
    
    def _build_TFxIDF_matrix(self):
        """1.4 - Construit la matrice TF-IDF"""
        n_docs = self.n_docs
        n_words = len(self.vocab)
        
        # Obtenir la matrice TF au format COO pour manipulation
        tf_coo = self.mat_TF.tocoo()
        data = []
        rows = []
        cols = []
        
        print(f"  Calcul des poids TF-IDF...")
        
        # Calculer TF-IDF pour chaque élément non nul
        for i, j, tf in zip(tf_coo.row, tf_coo.col, tf_coo.data):
            # IDF = log(N / df) où N = nombre de documents, df = document frequency
            word_info = self._get_word_by_id(j)
            if word_info:
                df = word_info['doc_frequency']
                
                if df > 0:
                    idf = math.log(n_docs / df)
                    tfidf = tf * idf
                    
                    data.append(tfidf)
                    rows.append(i)
                    cols.append(j)
        
        # Créer la matrice TF-IDF creuse
        self.mat_TFxIDF = sparse.csr_matrix((data, (rows, cols)), 
                                           shape=(n_docs, n_words))
    
    def _get_word_by_id(self, word_id: int):
        """Retourne les informations d'un mot par son ID"""
        for word, info in self.vocab.items():
            if info['id'] == word_id:
                return info
        return None
    
    def _query_to_vector(self, query: str, use_tfidf: bool = True):
        """
        Transforme une requête en vecteur dans l'espace du vocabulaire
        
        Args:
            query: Requête textuelle
            use_tfidf: Si True, utilise les poids TF-IDF, sinon TF
            
        Returns:
            Vecteur de la requête
        """
        n_words = len(self.vocab)
        query_vec = np.zeros(n_words)
        
        # Prétraiter la requête
        tokens = self._clean_text(query)
        
        if not tokens:
            return query_vec
        
        # Compter les occurrences dans la requête
        for token in tokens:
            if token in self.word_to_id:
                word_id = self.word_to_id[token]
                query_vec[word_id] += 1
        
        # Si on utilise TF-IDF, appliquer la pondération IDF
        if use_tfidf:
            for token in tokens:
                if token in self.word_to_id:
                    word_id = self.word_to_id[token]
                    word_info = self.vocab[token]
                    df = word_info['doc_frequency']
                    
                    if df > 0:
                        idf = math.log(self.n_docs / df)
                        query_vec[word_id] *= idf
        
        # Normalisation pour la similarité cosinus
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec = query_vec / norm
            
        return query_vec
    
    def search(self, query: str, k: int = 5, use_tfidf: bool = True) -> pd.DataFrame:
        """
        Effectue une recherche dans le corpus
        
        Args:
            query: Requête textuelle
            k: Nombre de résultats à retourner
            use_tfidf: Si True, utilise la matrice TF-IDF, sinon TF
            
        Returns:
            DataFrame pandas avec les résultats
        """
        print(f"\nRecherche: '{query}'")
        print(f"Paramètres: k={k}, TF-IDF={use_tfidf}")
        
        # Convertir la requête en vecteur
        query_vec = self._query_to_vector(query, use_tfidf)
        
        # Sélectionner la matrice à utiliser
        if use_tfidf:
            doc_matrix = self.mat_TFxIDF
            print("  Utilisation de la matrice TF-IDF")
        else:
            doc_matrix = self.mat_TF
            print("  Utilisation de la matrice TF")
        
        # Normaliser les documents pour la similarité cosinus
        # On normalise chaque vecteur document
        norms = np.sqrt(doc_matrix.power(2).sum(axis=1)).A1
        norm_matrix = doc_matrix.copy()
        
        # Éviter la division par zéro
        mask = norms > 0
        if mask.any():
            norm_matrix[mask] = doc_matrix[mask].multiply(1 / norms[mask].reshape(-1, 1))
        
        # Calculer les similarités cosinus
        similarities = norm_matrix.dot(query_vec)
        
        # Trier les documents par similarité décroissante
        sorted_indices = np.argsort(-similarities)
        
        # Préparer les résultats
        results = []
        for i, doc_idx in enumerate(sorted_indices[:k]):
            if similarities[doc_idx] > 0:  # Ne retourner que les documents pertinents
                # Récupérer l'objet document original
                doc_ids = list(self.corpus.id2doc.keys())
                if doc_idx < len(doc_ids):
                    doc_id = doc_ids[doc_idx]
                    original_doc = self.corpus.id2doc[doc_id]
                    
                    # Extraire les informations du document
                    titre = getattr(original_doc, 'titre', f'Document {doc_id}')
                    auteur = getattr(original_doc, 'auteur', 'Inconnu')
                    date = getattr(original_doc, 'date', 'Date inconnue')
                    doc_type = getattr(original_doc, 'getType', lambda: 'Document')()
                    
                    # Créer un aperçu du document
                    preview_length = 150
                    texte = self.texts[doc_idx]
                    if len(texte) > preview_length:
                        preview = texte[:preview_length] + '...'
                    else:
                        preview = texte
                    
                    result = {
                        'rang': i + 1,
                        'document_id': doc_id,
                        'titre': titre,
                        'auteur': auteur,
                        'date': str(date)[:10] if hasattr(date, '__str__') else str(date),
                        'type': doc_type,
                        'score_similarite': round(similarities[doc_idx], 4),
                        'aperçu': preview
                    }
                    results.append(result)
        
        # Créer le DataFrame
        df_results = pd.DataFrame(results)
        
        # Si aucun résultat n'a été trouvé
        if df_results.empty:
            print("Aucun document trouvé pour cette requête.")
            return pd.DataFrame()
            
        return df_results
    
    def get_vocab_stats(self, n: int = 20) -> pd.DataFrame:
        """
        Retourne les statistiques du vocabulaire sous forme de DataFrame
        
        Args:
            n: Nombre de mots à afficher (None pour tous)
            
        Returns:
            DataFrame avec les statistiques du vocabulaire
        """
        stats_data = []
        for word, info in sorted(self.vocab.items()):
            stats_data.append({
                'mot': word,
                'id': info['id'],
                'occurrences_totales': info['total_occurrences'],
                'freq_document': info['doc_frequency']
            })
        
        df_stats = pd.DataFrame(stats_data)
        
        # Trier par occurrences totales décroissantes
        df_stats = df_stats.sort_values('occurrences_totales', ascending=False)
        
        # Limiter au n premiers si spécifié
        if n is not None:
            df_stats = df_stats.head(n)
        
        return df_stats
    
    def display_corpus_info(self):
        """Affiche des informations sur le corpus"""
        print(f"\n=== INFORMATION SUR LE CORPUS ===")
        print(f"Nom du corpus: {self.corpus.nom}")
        print(f"Nombre de documents: {self.corpus.ndoc}")
        print(f"Nombre d'auteurs: {self.corpus.naut}")
        print(f"Taille du vocabulaire: {len(self.vocab)} mots")
        print(f"Dimensions de la matrice TF: {self.mat_TF.shape}")
        print(f"Dimensions de la matrice TF-IDF: {self.mat_TFxIDF.shape}")
        
        # Afficher quelques statistiques
        print(f"\nStatistiques textuelles:")
        df_freq = self.corpus.stats(5)  # Utilise la méthode stats du corpus
        
        return df_freq