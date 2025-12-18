# SearchEngine_TD8
import numpy as np
import pandas as pd
from scipy import sparse
import math
from collections import defaultdict
import re
from typing import List, Dict, Tuple
from tqdm import tqdm

class SearchEngine:
    """
    Moteur de recherche corrigé pour le TD8
    """
    
    def __init__(self, corpus):
        """
        Initialise le moteur de recherche avec un corpus
        """
        self.corpus = corpus
        
        # Vérification du corpus
        print(f"Corpus reçu: {corpus.nom}")
        print(f"Nombre de documents dans id2doc: {len(corpus.id2doc)}")
        print(f"corpus.ndoc: {corpus.ndoc}")
        
        # Extraction CORRECTE des textes
        self.texts, self.doc_ids = self._extract_texts_and_ids()
        self.n_docs = len(self.texts)
        
        print(f"\nTextes extraits pour l'indexation: {self.n_docs}")
        
        # Vérification
        if self.n_docs == 0:
            print("⚠️ ATTENTION: Aucun texte extrait!")
            print("Vérifiez que vos objets Document ont un attribut 'texte'")
            return
        
        # Structures de données
        self.vocab = {}
        self.word_to_id = {}
        self.mat_TF = None
        self.mat_TFxIDF = None
        
        # Construction de l'index
        print("\nConstruction du vocabulaire...")
        self._build_vocabulary()
        
        print("\nConstruction de la matrice TF...")
        self._build_TF_matrix()
        
        print("\nConstruction de la matrice TF-IDF...")
        self._build_TFxIDF_matrix()
        
        print(f"\nMoteur initialisé avec {self.n_docs} documents et {len(self.vocab)} mots")
    
    def _extract_texts_and_ids(self):
        """
        Extrait les textes ET les IDs des documents
        Version corrigée et robuste
        """
        texts = []
        doc_ids = []
        
        print(f"Extraction des textes depuis {len(self.corpus.id2doc)} documents...")
        
        for doc_id, document in self.corpus.id2doc.items():
            # Vérifier que le document existe
            if document is None:
                continue
            
            # Essayer différentes méthodes pour obtenir le texte
            texte = None
            
            # Méthode 1: Attribut 'texte'
            if hasattr(document, 'texte'):
                texte = document.texte
            
            # Méthode 2: Attribut 'text'
            elif hasattr(document, 'text'):
                texte = document.text
            
            # Méthode 3: Méthode get_text()
            elif hasattr(document, 'get_text'):
                texte = document.get_text()
            
            # Méthode 4: Conversion en string
            else:
                try:
                    texte = str(document)
                except:
                    texte = ""
            
            # Nettoyage et validation
            if texte is not None and isinstance(texte, str) and texte.strip():
                texts.append(texte.strip())
                doc_ids.append(doc_id)
        
        print(f"  {len(texts)} textes valides extraits sur {len(self.corpus.id2doc)} documents")
        return texts, doc_ids
    
    def _clean_text(self, text: str) -> List[str]:
        """
        Nettoie un texte - VERSION SIMPLIFIÉE
        """
        if not text or not isinstance(text, str):
            return []
        
        # Conversion en minuscules
        text = text.lower()
        
        # Suppression de la ponctuation (conservation des apostrophes pour l'anglais)
        text = re.sub(r'[^\w\s\']', ' ', text)
        
        # Tokenisation
        tokens = text.split()
        
        # Suppression des stop words simples (optionnel)
        stop_words = {'the', 'and', 'to', 'of', 'a', 'in', 'that', 'is', 'i', 'it', 'for', 'on', 'with', 'as', 'was', 'he', 'be', 'this', 'are', 'or', 'his', 'by', 'at', 'from', 'but', 'not', 'have', 'an', 'they', 'which', 'one', 'you', 'were', 'her', 'all', 'she', 'there', 'would', 'their', 'we', 'him', 'been', 'has', 'when', 'who', 'will', 'more', 'no', 'if', 'out', 'so', 'up', 'said', 'what', 'its', 'than', 'about', 'into', 'them', 'can', 'only', 'other', 'new', 'some', 'could', 'time', 'these', 'two', 'may', 'then', 'do', 'first', 'any', 'my', 'now', 'such', 'like', 'our', 'over', 'man', 'me', 'even', 'most', 'made', 'after', 'also', 'did', 'many', 'before', 'must', 'through', 'back', 'years', 'where', 'much', 'your', 'way', 'well', 'should', 'down', 'see'}
        tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
        
        return tokens
    
    def _build_vocabulary(self):
        """
        Construit le vocabulaire - VERSION CORRIGÉE
        """
        all_tokens = []
        
        print(f"  Analyse de {self.n_docs} documents...")
        
        # Utilisation de tqdm pour la barre de progression
        for doc in tqdm(self.texts, desc="Tokenisation", unit="doc"):
            tokens = self._clean_text(doc)
            all_tokens.extend(tokens)
        
        # Obtenir les mots uniques
        unique_tokens = sorted(set(all_tokens))
        
        print(f"  Vocabulaire: {len(unique_tokens)} mots uniques")
        
        # Construire le dictionnaire vocabulaire
        for idx, token in enumerate(unique_tokens):
            self.vocab[token] = {
                'id': idx,
                'total_occurrences': 0,
                'doc_frequency': 0
            }
            self.word_to_id[token] = idx
    
    def _build_TF_matrix(self):
        """
        Construit la matrice TF - VERSION CORRIGÉE
        """
        n_words = len(self.vocab)
        
        print(f"  Dimensions: {self.n_docs} documents x {n_words} mots")
        
        # Initialisation des listes pour matrice creuse
        data = []
        rows = []
        cols = []
        
        # Parcours des documents avec progression
        for doc_id, doc in tqdm(enumerate(self.texts), 
                               desc="Construction TF", 
                               total=self.n_docs,
                               unit="doc"):
            
            tokens = self._clean_text(doc)
            doc_word_counts = defaultdict(int)
            
            # Compter les occurrences dans ce document
            for token in tokens:
                if token in self.word_to_id:
                    word_id = self.word_to_id[token]
                    doc_word_counts[word_id] += 1
            
            # Ajouter aux listes de la matrice creuse
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
        
        if self.mat_TF is None:
            print("  Matrice TF non disponible")
            return
        
        tf_coo = self.mat_TF.tocoo()
        data = []
        rows = []
        cols = []
        
        print(f"  Calcul des poids TF-IDF pour {tf_coo.nnz} éléments...")
        
        for i, j, tf in tqdm(zip(tf_coo.row, tf_coo.col, tf_coo.data),
                            desc="TF-IDF",
                            total=tf_coo.nnz,
                            unit="élément"):
            
            # Récupérer les infos du mot
            word_info = None
            for word, info in self.vocab.items():
                if info['id'] == j:
                    word_info = info
                    break
            
            if word_info:
                df = word_info['doc_frequency']
                if df > 0:
                    idf = math.log(n_docs / df)
                    tfidf = tf * idf
                    data.append(tfidf)
                    rows.append(i)
                    cols.append(j)
        
        # Création de la matrice TF-IDF
        if data:
            self.mat_TFxIDF = sparse.csr_matrix((data, (rows, cols)), 
                                               shape=(n_docs, n_words))
            print(f"  Matrice TF-IDF créée: {self.mat_TFxIDF.shape}")
        else:
            print("  Aucune donnée TF-IDF calculée")
    
    def _get_word_by_id(self, word_id: int):
        """Retourne les informations d'un mot par son ID"""
        for word, info in self.vocab.items():
            if info['id'] == word_id:
                return info
        return None
    
    def search(self, query: str, n_results: int = 10):
        """
        Recherche compatible TD8
        
        Args:
            query: Requête textuelle
            n_results: Nombre de résultats à retourner
            
        Returns:
            Liste de tuples (score, doc_id, document)
        """
        if self.n_docs == 0 or self.mat_TFxIDF is None:
            print("Index non disponible. Recherche basique...")
            return self._recherche_basique(query, n_results)
        
        # Convertir la requête en vecteur
        query_vec = self._query_to_vector(query)
        
        if query_vec is None:
            return []
        
        # Calculer les similarités cosinus
        similarities = self._compute_similarities(query_vec)
        
        # Extraire les meilleurs résultats
        results = self._get_top_results(similarities, n_results)
        
        return results
    
    def _query_to_vector(self, query: str):
        """Convertit une requête en vecteur"""
        if len(self.vocab) == 0:
            return None
        
        n_words = len(self.vocab)
        query_vec = np.zeros(n_words)
        
        tokens = self._clean_text(query)
        if not tokens:
            return query_vec
        
        # TF de la requête
        for token in tokens:
            if token in self.word_to_id:
                word_id = self.word_to_id[token]
                query_vec[word_id] += 1
        
        # Application IDF
        for token in tokens:
            if token in self.word_to_id:
                word_id = self.word_to_id[token]
                word_info = self.vocab.get(token)
                if word_info and word_info['doc_frequency'] > 0:
                    idf = math.log(self.n_docs / word_info['doc_frequency'])
                    query_vec[word_id] *= idf
        
        # Normalisation
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec = query_vec / norm
        
        return query_vec
    
    def _compute_similarities(self, query_vec):
        """Calcule les similarités cosinus"""
        if self.mat_TFxIDF is None:
            return np.array([])
        
        doc_matrix = self.mat_TFxIDF
        
        # Normalisation de la matrice des documents
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
        if len(similarities) == 0:
            return []
        
        # Tri décroissant
        sorted_indices = np.argsort(-similarities)
        
        results = []
        for i, doc_idx in enumerate(sorted_indices[:n_results]):
            if similarities[doc_idx] > 0:
                # Récupérer le document original
                doc_id = self.doc_ids[doc_idx]
                original_doc = self.corpus.id2doc[doc_id]
                
                results.append((float(similarities[doc_idx]), doc_id, original_doc))
        
        return results
    
    def _recherche_basique(self, query, n_results):
        """Recherche basique de secours"""
        results = []
        query_terms = self._clean_text(query)
        
        if not query_terms:
            return results
        
        print(f"  Recherche basique pour: {query_terms}")
        
        for doc_id, doc in self.corpus.id2doc.items():
            # Récupérer le texte
            texte = ""
            if hasattr(doc, 'texte'):
                texte = doc.texte
            elif hasattr(doc, 'text'):
                texte = doc.text
            else:
                continue
            
            texte_lower = texte.lower()
            score = 0
            
            for term in query_terms:
                if term in texte_lower:
                    # Score simple
                    score += texte_lower.count(term) * 0.1 + 1
            
            if score > 0:
                results.append((score, doc_id, doc))
        
        # Trier par score décroissant
        results.sort(reverse=True, key=lambda x: x[0])
        
        return results[:n_results]
    
    def get_vocab_stats(self, n: int = 20):
        """Retourne les statistiques du vocabulaire"""
        if not self.vocab:
            return pd.DataFrame()
        
        stats_data = []
        for word, info in self.vocab.items():
            stats_data.append({
                'mot': word,
                'id': info['id'],
                'occurrences_totales': info['total_occurrences'],
                'freq_document': info['doc_frequency']
            })
        
        df_stats = pd.DataFrame(stats_data)
        df_stats = df_stats.sort_values('occurrences_totales', ascending=False)
        
        if n is not None:
            df_stats = df_stats.head(n)
        
        return df_stats
    
    def display_corpus_info(self):
        """Affiche des informations sur le corpus"""
        print(f"\n=== INFORMATION SUR LE CORPUS ===")
        print(f"Nom du corpus: {self.corpus.nom}")
        print(f"Nombre de documents indexés: {self.n_docs}")
        print(f"Taille du vocabulaire: {len(self.vocab)} mots")
        
        if self.mat_TF is not None:
            print(f"Dimensions de la matrice TF: {self.mat_TF.shape}")
        
        if self.mat_TFxIDF is not None:
            print(f"Dimensions de la matrice TF-IDF: {self.mat_TFxIDF.shape}")