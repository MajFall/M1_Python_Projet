# SearchEngine_TD8.py - Version compatible TD8
import numpy as np
import pandas as pd
from scipy import sparse
import math
from collections import defaultdict
import re
from typing import List, Dict, Tuple
from tqdm import tqdm

class SearchEngineTD8:
    """
    Moteur de recherche compatible avec le TD8
    """
    
    def __init__(self, corpus):
        """
        Initialise le moteur de recherche avec un corpus de documents
        """
        self.corpus = corpus
        
        # Extraction des textes avec débogage
        print("Extraction des textes du corpus...")
        self.texts, self.doc_ids = self._extract_texts_and_ids()
        self.n_docs = len(self.texts)
        print(f"  Documents extraits: {self.n_docs}")
        
        # Structures de données
        self.vocab = {}
        self.word_to_id = {}
        self.mat_TF = None
        self.mat_TFxIDF = None
        
        if self.n_docs > 0:
            print("Construction du vocabulaire...")
            self._build_vocabulary()
            
            print("Construction de la matrice TF...")
            self._build_TF_matrix()
            
            print("Construction de la matrice TF-IDF...")
            self._build_TFxIDF_matrix()
        else:
            print("ATTENTION: Aucun document trouvé dans le corpus!")
    
    def _extract_texts_and_ids(self):
        """Extrait les textes et IDs de tous les documents"""
        texts = []
        doc_ids = []
        
        for doc_id, document in tqdm(self.corpus.id2doc.items(), 
                                    desc="Extraction", 
                                    total=len(self.corpus.id2doc)):
            
            # Méthode robuste pour obtenir le texte
            texte = ""
            if hasattr(document, 'texte'):
                texte = document.texte
            elif hasattr(document, 'text'):
                texte = document.text
            elif hasattr(document, 'contenu'):
                texte = document.contenu
            elif hasattr(document, 'content'):
                texte = document.content
            else:
                # Dernier recours: essayer d'accéder directement
                try:
                    texte = str(document)
                except:
                    texte = ""
            
            # Nettoyage basique
            if isinstance(texte, str) and texte.strip():
                texts.append(texte.strip())
                doc_ids.append(doc_id)
        
        return texts, doc_ids
    
    def _clean_text(self, text: str) -> List[str]:
        """Nettoie et tokenise un texte"""
        if not text:
            return []
        
        # Conversion en minuscules
        text = text.lower()
        
        # Remplacement des caractères spéciaux
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Tokenisation
        tokens = text.split()
        
        # Filtrage des tokens courts
        tokens = [token for token in tokens if len(token) > 2]
        
        return tokens
    
    def _build_vocabulary(self):
        """Construit le vocabulaire"""
        all_tokens = []
        
        # Collecte tous les tokens
        for doc in tqdm(self.texts, desc="Tokenisation"):
            tokens = self._clean_text(doc)
            all_tokens.extend(tokens)
        
        # Création du vocabulaire
        unique_tokens = sorted(set(all_tokens))
        
        for idx, token in enumerate(unique_tokens):
            self.vocab[token] = {
                'id': idx,
                'total_occurrences': 0,
                'doc_frequency': 0
            }
            self.word_to_id[token] = idx
        
        print(f"  Vocabulaire: {len(unique_tokens)} mots uniques")
    
    def _build_TF_matrix(self):
        """Construit la matrice TF"""
        n_words = len(self.vocab)
        
        data = []
        rows = []
        cols = []
        
        for doc_id, doc in tqdm(enumerate(self.texts), 
                               desc="Construction TF", 
                               total=self.n_docs):
            tokens = self._clean_text(doc)
            doc_word_counts = defaultdict(int)
            
            for token in tokens:
                if token in self.word_to_id:
                    word_id = self.word_to_id[token]
                    doc_word_counts[word_id] += 1
            
            for word_id, count in doc_word_counts.items():
                data.append(count)
                rows.append(doc_id)
                cols.append(word_id)
        
        # Création de la matrice creuse
        self.mat_TF = sparse.csr_matrix((data, (rows, cols)), 
                                        shape=(self.n_docs, n_words))
        
        # Mise à jour des statistiques
        self._update_vocab_stats()
    
    def _update_vocab_stats(self):
        """Met à jour les statistiques du vocabulaire"""
        if self.mat_TF is None:
            return
        
        # Calcul des fréquences
        total_occurrences = self.mat_TF.sum(axis=0).A1
        doc_frequency = (self.mat_TF > 0).sum(axis=0).A1
        
        for word, info in self.vocab.items():
            word_id = info['id']
            info['total_occurrences'] = total_occurrences[word_id]
            info['doc_frequency'] = doc_frequency[word_id]
    
    def _build_TFxIDF_matrix(self):
        """Construit la matrice TF-IDF"""
        n_docs = self.n_docs
        n_words = len(self.vocab)
        
        tf_coo = self.mat_TF.tocoo()
        data = []
        rows = []
        cols = []
        
        for i, j, tf in tqdm(zip(tf_coo.row, tf_coo.col, tf_coo.data),
                            desc="Calcul TF-IDF",
                            total=tf_coo.nnz):
            word_info = self._get_word_by_id(j)
            if word_info:
                df = word_info['doc_frequency']
                if df > 0:
                    idf = math.log(n_docs / df)
                    tfidf = tf * idf
                    data.append(tfidf)
                    rows.append(i)
                    cols.append(j)
        
        self.mat_TFxIDF = sparse.csr_matrix((data, (rows, cols)), 
                                           shape=(n_docs, n_words))
    
    def _get_word_by_id(self, word_id: int):
        """Retourne les informations d'un mot par son ID"""
        for word, info in self.vocab.items():
            if info['id'] == word_id:
                return info
        return None
    
    def search(self, query: str, n_results: int = 10) -> list:
        """
        Recherche compatible TD8
        
        Args:
            query: Requête textuelle
            n_results: Nombre de résultats à retourner
            
        Returns:
            Liste de tuples (score, doc_id, document)
        """
        if self.n_docs == 0:
            print("ATTENTION: Aucun document dans l'index")
            return []
        
        # Vecteur de la requête
        query_vec = self._query_to_vector(query)
        
        if query_vec is None:
            return []
        
        # Similarités cosinus
        similarities = self._compute_similarities(query_vec)
        
        # Tri et sélection
        results = self._get_top_results(similarities, n_results)
        
        return results
    
    def _query_to_vector(self, query: str):
        """Convertit une requête en vecteur"""
        n_words = len(self.vocab)
        if n_words == 0:
            return None
        
        query_vec = np.zeros(n_words)
        tokens = self._clean_text(query)
        
        if not tokens:
            return query_vec
        
        # TF de la requête
        for token in tokens:
            if token in self.word_to_id:
                word_id = self.word_to_id[token]
                query_vec[word_id] += 1
        
        # Application IDF si disponible
        if hasattr(self, 'mat_TFxIDF'):
            for token in tokens:
                if token in self.word_to_id:
                    word_id = self.word_to_id[token]
                    word_info = self.vocab[token]
                    df = word_info['doc_frequency']
                    if df > 0:
                        idf = math.log(self.n_docs / df)
                        query_vec[word_id] *= idf
        
        # Normalisation
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec = query_vec / norm
        
        return query_vec
    
    def _compute_similarities(self, query_vec):
        """Calcule les similarités cosinus"""
        # Normalisation de la matrice des documents
        if hasattr(self, 'mat_TFxIDF') and self.mat_TFxIDF is not None:
            doc_matrix = self.mat_TFxIDF
        else:
            doc_matrix = self.mat_TF
        
        norms = np.sqrt(doc_matrix.power(2).sum(axis=1)).A1
        mask = norms > 0
        norm_matrix = doc_matrix.copy()
        
        if mask.any():
            norm_matrix[mask] = doc_matrix[mask].multiply(1 / norms[mask].reshape(-1, 1))
        
        # Calcul des similarités
        similarities = norm_matrix.dot(query_vec)
        
        return similarities
    
    def _get_top_results(self, similarities, n_results):
        """Extrait les meilleurs résultats"""
        # Tri décroissant
        sorted_indices = np.argsort(-similarities)
        
        results = []
        for i, doc_idx in enumerate(sorted_indices[:n_results]):
            if similarities[doc_idx] > 0:
                # Récupération du document original
                doc_id = self.doc_ids[doc_idx]
                original_doc = self.corpus.id2doc[doc_id]
                
                results.append((float(similarities[doc_idx]), doc_id, original_doc))
        
        return results