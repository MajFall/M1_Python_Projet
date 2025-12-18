# -*- coding: utf-8 -*-
"""
Created on Wed Dec 17 23:32:59 2025

@author: surface laptop 2
"""



import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import re
from math import log
import json
import os
import sys
from datetime import datetime
import pandas as pd

class CorpusExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("Explorateur de Corpus SHS")
        self.root.geometry("1300x850")
        
        # Configuration du style
        self.setup_styles()
        
        # Données 
        self.documents = []
        self.current_corpus = []
        self.corpus_a = []
        self.corpus_b = []
        self.all_sources = []
        
        # Variables d'interface
        self.search_var = tk.StringVar()
        self.word_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.source_var = tk.StringVar()
        self.date_start_var = tk.StringVar()
        self.date_end_var = tk.StringVar()
        
        self.setup_ui()
        
        # Charger les trois corpus
        self.load_all_corpora()
        
    def setup_styles(self):
        """Configure les styles de l'interface."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Couleurs personnalisées
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Section.TLabel', font=('Arial', 10, 'bold'), foreground='#2c3e50')
        
    def load_all_corpora(self):
        """Charge tous les corpus disponibles."""
        print("=" * 60)
        print("CHARGEMENT DES CORPUS")
        print("=" * 60)
        
        total_before = len(self.documents)
        
        # 1. Charger le corpus Discours US
        print("\n1. CHARGEMENT DU CORPUS DISCOURS US")
        print("-" * 40)
        if self.load_discours_us():
            print(f"Discours US chargé: {len(self.documents) - total_before} documents")
        else:
            print("Échec du chargement du corpus Discours US")
            # Ajouter des données d'exemple minimales
            self.add_sample_discours()
        
        total_after_discours = len(self.documents)
        
        # 2. Charger Reddit
        print("\n2. CHARGEMENT DU CORPUS REDDIT")
        print("-" * 40)
        reddit_count = self.load_reddit_data()
        print(f" Reddit chargé: {reddit_count} documents")
        
        # 3. Charger Arxiv
        print("\n3. CHARGEMENT DU CORPUS ARXIV")
        print("-" * 40)
        arxiv_count = self.load_arxiv_data()
        print(f"Arxiv chargé: {arxiv_count} documents")
        
        # Mettre à jour l'affichage
        self.current_corpus = self.documents
        self.display_documents()
        
        # Mettre à jour la liste des sources
        self.update_source_list()
        
        # Afficher le résumé
        total_loaded = len(self.documents)
        discours_count = total_after_discours - total_before
        
        summary = (
            f"CHARGEMENT TERMINÉ !\n\n"
            f" Statistiques :\n"
            f" Discours US : {discours_count} documents\n"
            f" Reddit : {reddit_count} documents\n"
            f" Arxiv : {arxiv_count} documents\n"
            f" TOTAL : {total_loaded} documents\n\n"
            f" Vous pouvez maintenant effectuer des recherches !"
        )
        
        messagebox.showinfo("Chargement terminé", summary)
        print("\n" + "=" * 60)
        print("CHARGEMENT TERMINÉ AVEC SUCCÈS")
        print("=" * 60)
    
    def load_discours_us(self):
        
        json_path = 'C:/Users/surface laptop 2/Desktop/Master1-Lyon2/PYTHON/Projet_Python/V1(TD3-5)/TD9-10/corpus_discours_us_simple.json'
        
        if not os.path.exists(json_path):
            print(f" Fichier non trouvé: {json_path}")
            return False
        
        try:
            print(f" Lecture du fichier: {json_path}")
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f" Structure détectée: {type(data)}")
            
            # Si c'est un dictionnaire avec des métadonnées
            if isinstance(data, dict):
                if 'documents' in data:
                    print(" Structure: Dictionnaire avec clé 'documents'")
                    documents_list = data['documents']
                elif 'data' in data:
                    print(" Structure: Dictionnaire avec clé 'data'")
                    documents_list = data['data']
                else:
                    print("Structure inattendue, tentative avec toutes les clés")
                    # Essayer de trouver une liste dans les valeurs
                    documents_list = []
                    for key, value in data.items():
                        if isinstance(value, list):
                            documents_list = value
                            print(f" Liste trouvée dans la clé: {key}")
                            break
            else:
                documents_list = data
            
            if not isinstance(documents_list, list):
                print(f" Format inattendu: {type(documents_list)}")
                return False
            
            print(f" Nombre de documents à traiter: {len(documents_list)}")
            
            # Analyser le premier document pour comprendre la structure
            if documents_list:
                first_doc = documents_list[0]
                print("\n ANALYSE DE LA STRUCTURE DU PREMIER DOCUMENT:")
                print("-" * 50)
                for key, value in first_doc.items():
                    if isinstance(value, str):
                        # Afficher un aperçu
                        preview = value.replace('\n', ' ').replace('\r', ' ')[:80]
                        print(f"  '{key}': '{preview}...'")
                    elif isinstance(value, (int, float)):
                        print(f"   '{key}': {value}")
                    elif isinstance(value, list):
                        print(f" '{key}': Liste de {len(value)} éléments")
                    else:
                        print(f" '{key}': {type(value)}")
                print("-" * 50)
            
            # Traitement des documents
            loaded_count = 0
            for i, item in enumerate(documents_list):
                if not isinstance(item, dict):
                    continue
                
                # Fonction de nettoyage
                def clean_text(text):
                    if not isinstance(text, str):
                        return ""
                    # Nettoyage de base
                    text = text.strip()
                    text = re.sub(r'\s+', ' ', text)  # Supprimer les espaces multiples
                   
                    text = re.sub(r'\bDiscount\b', 'Discours', text, flags=re.IGNORECASE)
                    return text
                
                # Chercher le titre
                title = ""
                for key in ['descr', 'title', 'titre', 'subject', 'name', 'topic']:
                    if key in item and item[key]:
                        title = clean_text(str(item[key]))
                        if title:
                            break
                
                # Chercher l'auteur (plusieurs champs possibles)
                author = "Inconnu"
                for key in ['speaker', 'author', 'auteur', 'by', 'speaker_raw', 'person', 'president']:
                    if key in item and item[key]:
                        author = clean_text(str(item[key]))
                        # Nettoyer l'auteur
                        author = re.sub(r'[^\w\s\-]', '', author)  # Enlever caractères spéciaux
                        author = author.strip()
                        if author:
                           
                            if len(author) > 2 and not re.match(r'^\d+$', author):
                                break
                
                # Chercher la date
                date_str = ""
                for key in ['date', 'datetime', 'time', 'year', 'timestamp']:
                    if key in item and item[key]:
                        date_str = str(item[key])
                        # Essayer de formater la date
                        try:
                            # Convertir "April 12, 2015" en "2015-04-12"
                            from dateutil import parser
                            parsed_date = parser.parse(date_str)
                            date_str = parsed_date.strftime("%Y-%m-%d")
                        except:
                            # Garder la date originale
                            date_str = clean_text(date_str)
                        break
                
                # Chercher le texte
                text = ""
                for key in ['text', 'texte', 'content', 'transcript', 'speech', 'body']:
                    if key in item and item[key]:
                        text = clean_text(str(item[key]))
                        if len(text) > 10:  # Ignorer les textes trop courts
                            break
                
                # Chercher l'URL
                url = ""
                for key in ['url', 'link', 'uri', 'source', 'permalink']:
                    if key in item and item[key]:
                        url = clean_text(str(item[key]))
                        break
                
                # Créer le document
                doc = {
                    'id': len(self.documents) + 1,
                    'title': title if title else f"Discours_{i+1}",
                    'author': author if author else "Inconnu",
                    'source': 'Discours US',
                    'date': date_str,
                    'text': text,
                    'url': url,
                    'original_data': item  # Garder les données originales pour le débogage
                }
                
                # Ajouter seulement si on a du texte
                if doc['text'] and len(doc['text']) > 20:
                    self.documents.append(doc)
                    loaded_count += 1
                
                # Afficher la progression
                if (i + 1) % 1000 == 0:
                    print(f"  Traités: {i + 1}/{len(documents_list)} documents")
            
            print(f"\n Discours US: {loaded_count} documents chargés")
            
            # Statistiques des auteurs
            if loaded_count > 0:
                authors = Counter([d['author'] for d in self.documents[-loaded_count:]])
                print(f" Auteurs détectés: {len(authors)}")
                print(f" Top 5 auteurs:")
                for author, count in authors.most_common(5):
                    if author != 'Inconnu':
                        print(f"  {author}: {count} documents")
                
                unknown_count = authors.get('Inconnu', 0)
                if unknown_count > 0:
                    print(f" {unknown_count} documents sans auteur identifié")
            
            return True
            
        except Exception as e:
            print(f" Erreur lors du chargement: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
   
       
    
    def load_reddit_data(self):
        """Charge des données Reddit."""
        reddit_count = 0
        
        # Essayer de charger depuis un fichier
        reddit_path = 'C:/Users/surface laptop 2/Desktop/Master1-Lyon2/PYTHON/Projet_Python/reddit_data.json'
        
        if os.path.exists(reddit_path):
            try:
                with open(reddit_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    for item in data:
                        doc = {
                            'id': len(self.documents) + 1,
                            'title': item.get('title', 'Post Reddit'),
                            'author': item.get('author', 'Anonyme'),
                            'source': 'Reddit',
                            'date': item.get('created_utc', ''),
                            'text': item.get('selftext', '') + ' ' + item.get('body', ''),
                            'url': item.get('url', ''),
                            'upvotes': item.get('score', 0),
                            'comments': item.get('num_comments', 0),
                            'subreddit': item.get('subreddit', '')
                        }
                        self.documents.append(doc)
                        reddit_count += 1
                
                print(f" Chargé depuis fichier: {reddit_path}")
                
            except Exception as e:
                print(f" Erreur avec le fichier Reddit: {e}")
        
        # Si pas de fichier ou erreur, créer des données d'exemple
        if reddit_count == 0:
            reddit_count = self._create_sample_reddit_data()
        
        return reddit_count
    
    def _create_sample_reddit_data(self):
        """Crée des données d'exemple pour Reddit."""
        sample_reddit = [
            {
                'id': len(self.documents) + 1,
                'title': 'Pourquoi Python est-il si populaire en data science?',
                'author': 'DataScientist42',
                'source': 'Reddit',
                'date': '2023-06-15',
                'text': 'Python offre une excellente compatibilité avec les bibliothèques comme Pandas, NumPy et Scikit-learn. La communauté est très active et les ressources d\'apprentissage sont nombreuses.',
                'url': 'https://reddit.com/r/datascience/12345',
                'upvotes': 245,
                'comments': 89,
                'subreddit': 'datascience'
            },
            {
                'id': len(self.documents) + 2,
                'title': 'Les modèles de langage transformer révolutionnent le NLP',
                'author': 'NLP_Enthusiast',
                'source': 'Reddit',
                'date': '2023-07-22',
                'text': 'BERT, GPT et autres modèles basés sur l\'architecture transformer ont complètement transformé le domaine du traitement du langage naturel. Les performances sont impressionnantes.',
                'url': 'https://reddit.com/r/MachineLearning/67890',
                'upvotes': 156,
                'comments': 42,
                'subreddit': 'MachineLearning'
            },
            {
                'id': len(self.documents) + 3,
                'title': 'Débat: R vs Python pour l\'analyse statistique',
                'author': 'StatsPro',
                'source': 'Reddit',
                'date': '2023-08-10',
                'text': 'R est excellent pour l\'analyse statistique pure avec ses packages spécialisés, tandis que Python est plus polyvalent pour l\'intégration dans des applications complètes.',
                'url': 'https://reddit.com/r/statistics/abcde',
                'upvotes': 89,
                'comments': 67,
                'subreddit': 'statistics'
            },
        ]
        
        self.documents.extend(sample_reddit)
        return len(sample_reddit)
    
    def load_arxiv_data(self):
        """Charge des données Arxiv."""
        arxiv_count = 0
        
        # Essayer de charger depuis un fichier
        arxiv_path = 'C:/Users/surface laptop 2/Desktop/Master1-Lyon2/PYTHON/Projet_Python/arxiv_data.json'
        
        if os.path.exists(arxiv_path):
            try:
                with open(arxiv_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    for item in data:
                        doc = {
                            'id': len(self.documents) + 1,
                            'title': item.get('title', 'Article scientifique'),
                            'author': item.get('authors', 'Auteurs inconnus'),
                            'source': 'Arxiv',
                            'date': item.get('published', ''),
                            'text': item.get('summary', '') + ' ' + item.get('abstract', ''),
                            'url': item.get('url', ''),
                            'journal': item.get('journal-ref', 'Arxiv'),
                            'citations': item.get('citation_count', 0),
                            'categories': item.get('categories', '')
                        }
                        self.documents.append(doc)
                        arxiv_count += 1
                
                print(f" Chargé depuis fichier: {arxiv_path}")
                
            except Exception as e:
                print(f" Erreur avec le fichier Arxiv: {e}")
        
        # Si pas de fichier ou erreur, créer des données d'exemple
        if arxiv_count == 0:
            arxiv_count = self._create_sample_arxiv_data()
        
        return arxiv_count
    
    def _create_sample_arxiv_data(self):
        """Crée des données d'exemple pour Arxiv."""
        sample_arxiv = [
            {
                'id': len(self.documents) + 1,
                'title': 'Attention Is All You Need',
                'author': 'Ashish Vaswani, Noam Shazeer, Niki Parmar, et al.',
                'source': 'Arxiv',
                'date': '2017-06-12',
                'text': 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.',
                'url': 'https://arxiv.org/abs/1706.03762',
                'journal': 'NeurIPS 2017',
                'citations': 85000,
                'categories': 'cs.CL'
            },
            {
                'id': len(self.documents) + 2,
                'title': 'BERT: Pre-training of Deep Bidirectional Transformers',
                'author': 'Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova',
                'source': 'Arxiv',
                'date': '2018-10-11',
                'text': 'We introduce a new language representation model called BERT. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations.',
                'url': 'https://arxiv.org/abs/1810.04805',
                'journal': 'NAACL 2019',
                'citations': 75000,
                'categories': 'cs.CL'
            },
            {
                'id': len(self.documents) + 3,
                'title': 'ImageNet Classification with Deep Convolutional Neural Networks',
                'author': 'Alex Krizhevsky, Ilya Sutskever, Geoffrey E. Hinton',
                'source': 'Arxiv',
                'date': '2012-09-30',
                'text': 'We trained a large, deep convolutional neural network to classify the 1.2 million high-resolution images in the ImageNet LSVRC-2010 contest into the 1000 different classes.',
                'url': 'https://arxiv.org/abs/1207.0580',
                'journal': 'NeurIPS 2012',
                'citations': 105000,
                'categories': 'cs.CV'
            },
        ]
        
        self.documents.extend(sample_arxiv)
        return len(sample_arxiv)
    
    def update_source_list(self):
        """Met à jour la liste des sources disponibles."""
        sources = list(set(doc.get('source', 'Inconnu') for doc in self.documents))
        sources.sort()
        self.all_sources = sources
        
        # Mettre à jour le Combobox
        if hasattr(self, 'source_combo'):
            current_value = self.source_combo.get()
            self.source_combo['values'] = ['Tous'] + sources
            if current_value in ['Tous'] + sources:
                self.source_combo.set(current_value)
            else:
                self.source_combo.set('Tous')
    
    def setup_ui(self):
        """Configure l'interface utilisateur."""
        # Configuration de la grille principale
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Panneau de contrôle gauche
        control_frame = ttk.LabelFrame(self.root, text=" REQUÊTES ET FILTRES", padding=15)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        row = 0
        
        # Recherche par mots-clés
        ttk.Label(control_frame, text="Mots-clés:", style='Section.TLabel').grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(control_frame, textvariable=self.search_var, width=35).grid(
            row=row, column=1, pady=(0, 5), padx=(10, 0))
        row += 1
        
        # Filtres avancés
        ttk.Label(control_frame, text="Auteur:", style='Section.TLabel').grid(
            row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(control_frame, textvariable=self.author_var, width=35).grid(
            row=row, column=1, pady=5, padx=(10, 0))
        row += 1
        
        ttk.Label(control_frame, text="Source:", style='Section.TLabel').grid(
            row=row, column=0, sticky=tk.W, pady=5)
        self.source_combo = ttk.Combobox(control_frame, textvariable=self.source_var, 
                                       width=33, state='readonly')
        self.source_combo.grid(row=row, column=1, pady=5, padx=(10, 0))
        self.source_combo.set('Tous')
        row += 1
        
        ttk.Label(control_frame, text="Date début (YYYY-MM-DD):", style='Section.TLabel').grid(
            row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(control_frame, textvariable=self.date_start_var, width=35).grid(
            row=row, column=1, pady=5, padx=(10, 0))
        row += 1
        
        ttk.Label(control_frame, text="Date fin (YYYY-MM-DD):", style='Section.TLabel').grid(
            row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(control_frame, textvariable=self.date_end_var, width=35).grid(
            row=row, column=1, pady=5, padx=(10, 0))
        row += 1
        
        # Boutons de recherche
        ttk.Button(control_frame, text=" Rechercher", command=self.search_documents,
                  style='Accent.TButton').grid(row=row, column=0, columnspan=2, pady=(15, 5), sticky="ew")
        row += 1
        
        ttk.Button(control_frame, text=" Réinitialiser", command=self.reset_filters).grid(
            row=row, column=0, columnspan=2, pady=5, sticky="ew")
        row += 1
        
        # Analyse comparative
        ttk.Separator(control_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, pady=15, sticky="ew")
        row += 1
        
        ttk.Label(control_frame, text=" ANALYSE COMPARATIVE", 
                 style='Title.TLabel').grid(row=row, column=0, columnspan=2, pady=(0, 10))
        row += 1
        
        button_frame = tk.Frame(control_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=5)
        
        ttk.Button(button_frame, text="Définir Corpus A", 
                  command=lambda: self.set_corpus('A'), width=15).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Définir Corpus B", 
                  command=lambda: self.set_corpus('B'), width=15).pack(side=tk.LEFT)
        row += 1
        
        ttk.Button(control_frame, text=" Comparer A vs B", 
                  command=self.compare_corpora).grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")
        row += 1
        
        # Analyse temporelle
        ttk.Separator(control_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, pady=15, sticky="ew")
        row += 1
        
        ttk.Label(control_frame, text="ANALYSE TEMPORELLE", 
                 style='Title.TLabel').grid(row=row, column=0, columnspan=2, pady=(0, 10))
        row += 1
        
        ttk.Label(control_frame, text="Mot à analyser:", style='Section.TLabel').grid(
            row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(control_frame, textvariable=self.word_var, width=35).grid(
            row=row, column=1, pady=5, padx=(10, 0))
        row += 1
        
        ttk.Button(control_frame, text=" Évolution temporelle", 
                  command=self.plot_temporal_evolution).grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")
        row += 1
        
        # Outils avancés
        ttk.Separator(control_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, pady=15, sticky="ew")
        row += 1
        
        ttk.Label(control_frame, text=" OUTILS", 
                 style='Title.TLabel').grid(row=row, column=0, columnspan=2, pady=(0, 10))
        row += 1
        
        tools = [
            ("Statistiques", self.show_statistics),
            ("Recharger", self.reload_corpus),
            ("Diagnostic", self.show_diagnostic),
            ("Exporter", self.export_results)
        ]
        
        for text, command in tools:
            ttk.Button(control_frame, text=text, command=command).grid(
                row=row, column=0, columnspan=2, pady=3, sticky="ew")
            row += 1
        
        # Zone d'affichage principale 
        notebook_frame = ttk.Frame(self.root)
        notebook_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        
        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Onglet 1: Documents
        self.doc_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.doc_frame, text="Documents")
        self.setup_document_display()
        
        # Onglet 2: Résultats TF-IDF
        self.tfidf_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tfidf_frame, text="Analyse TF-IDF")
        self.setup_tfidf_display()
        
        # Onglet 3: Visualisations
        self.viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.viz_frame, text="Visualisations")
        
        # Onglet 4: Aperçu
        self.preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.preview_frame, text="Aperçu")
        self.setup_preview_display()
    
    def setup_document_display(self):
        """Configure l'affichage des documents."""
        # Cadre principal avec scrollbar
        main_frame = ttk.Frame(self.doc_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview pour afficher les documents
        columns = ('ID', 'Titre', 'Auteur', 'Source', 'Date', 'Info')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=25)
        
        # Configurer les colonnes
        col_config = {
            'ID': {'width': 60, 'anchor': tk.CENTER},
            'Titre': {'width': 300, 'anchor': tk.W},
            'Auteur': {'width': 150, 'anchor': tk.W},
            'Source': {'width': 100, 'anchor': tk.CENTER},
            'Date': {'width': 100, 'anchor': tk.CENTER},
            'Info': {'width': 100, 'anchor': tk.CENTER}
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, **col_config[col])
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Placement des widgets
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configurer la grille
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Ajouter un double-clic pour voir le contenu
        self.tree.bind('<Double-1>', self.show_document_detail)
        
        # Menu contextuel
        self.setup_context_menu()
    
    def setup_tfidf_display(self):
        """Configure l'affichage TF-IDF."""
        frame = ttk.Frame(self.tfidf_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Analyse TF-IDF", font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        
        # Zone de texte pour afficher les résultats
        self.tfidf_text = tk.Text(frame, wrap=tk.WORD, height=20)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tfidf_text.yview)
        self.tfidf_text.configure(yscrollcommand=scrollbar.set)
        
        self.tfidf_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bouton pour calculer TF-IDF
        ttk.Button(frame, text="Calculer TF-IDF", 
                  command=self.calculate_and_display_tfidf).pack(pady=10)
    
    def setup_preview_display(self):
        """Configure l'aperçu des données."""
        frame = ttk.Frame(self.preview_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Statistiques rapides
        stats_frame = ttk.LabelFrame(frame, text="Statistiques rapides", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_label = ttk.Label(stats_frame, text="")
        self.stats_label.pack()
        
        # Aperçu des données
        preview_frame = ttk.LabelFrame(frame, text="Aperçu des données", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=15)
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bouton pour actualiser
        ttk.Button(frame, text="Actualiser l'aperçu", 
                  command=self.update_preview).pack(pady=10)
        
        # Initialiser l'aperçu
        self.update_preview()
    
    def setup_context_menu(self):
        """Configure le menu contextuel."""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Voir le détail", command=self.show_selected_document)
        self.context_menu.add_command(label="Copier l'ID", command=self.copy_document_id)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Ajouter au Corpus A", 
                                     command=lambda: self.add_to_corpus('A'))
        self.context_menu.add_command(label="Ajouter au Corpus B", 
                                     command=lambda: self.add_to_corpus('B'))
        
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def show_context_menu(self, event):
        """Affiche le menu contextuel."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def show_selected_document(self):
        """Affiche le document sélectionné."""
        selection = self.tree.selection()
        if selection:
            self.show_document_detail(None)
    
    def copy_document_id(self):
        """Copie l'ID du document sélectionné."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            doc_id = item['values'][0]
            self.root.clipboard_clear()
            self.root.clipboard_append(str(doc_id))
            messagebox.showinfo("Copié", f"ID {doc_id} copié dans le presse-papier")
    
    def add_to_corpus(self, corpus_id):
        """Ajoute le document sélectionné à un corpus."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            doc_id = item['values'][0]
            
            # Trouver le document
            for doc in self.current_corpus:
                if doc.get('id') == doc_id:
                    if corpus_id == 'A':
                        self.corpus_a.append(doc)
                        messagebox.showinfo("Corpus A", f"Document ajouté au Corpus A\nTotal: {len(self.corpus_a)} documents")
                    else:
                        self.corpus_b.append(doc)
                        messagebox.showinfo("Corpus B", f"Document ajouté au Corpus B\nTotal: {len(self.corpus_b)} documents")
                    break
    
    def display_documents(self):
        """Affiche les documents dans le Treeview."""
        # Vider le treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Afficher un message si vide
        if not self.current_corpus:
            return
        
        # Trier par ID
        sorted_corpus = sorted(self.current_corpus, key=lambda x: x.get('id', 0))
        
        for doc in sorted_corpus:
            # Formater la date
            date_str = doc.get('date', '')
            if date_str:
                try:
                    # Essayer de parser la date
                    if '-' in date_str and len(date_str) >= 10:
                        # Format YYYY-MM-DD
                        date_obj = datetime.strptime(date_str[:10], "%Y-%m-%d")
                        display_date = date_obj.strftime("%d/%m/%Y")
                    else:
                        display_date = date_str[:10]
                except:
                    display_date = date_str[:10] if date_str else ''
            else:
                display_date = ''
            
            # Information supplémentaire selon la source
            info_supp = ""
            source = doc.get('source', '')
            
            if source == 'Reddit':
                upvotes = doc.get('upvotes', 0)
                comments = doc.get('comments', 0)
                info_supp = f"↑{upvotes} {comments}"
            elif source == 'Arxiv':
                citations = doc.get('citations', 0)
                info_supp = f" {citations}c"
            elif source == 'Discours US':
                # Essayer d'extraire des informations du titre
                title = doc.get('title', '')
                if 'président' in title.lower() or 'president' in title.lower():
                    info_supp = " "
            
            # Tronquer les textes trop longs
            title = doc.get('title', '')
            if len(title) > 60:
                title = title[:57] + "..."
            
            author = doc.get('author', 'Inconnu')
            if len(author) > 25:
                author = author[:22] + "..."
            
            self.tree.insert('', tk.END, values=(
                doc.get('id', ''),
                title,
                author,
                source,
                display_date,
                info_supp
            ))
        
        # Mettre à jour le statut
        self.update_preview()
    
    def show_document_detail(self, event):
        """Affiche le détail d'un document en double-cliquant."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        doc_id = item['values'][0]
        
        # Trouver le document
        doc = None
        for d in self.current_corpus:
            if d.get('id') == doc_id:
                doc = d
                break
        
        if not doc:
            return
        
        # Créer une fenêtre modale
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Document #{doc_id} - {doc.get('title', 'Sans titre')}")
        detail_window.geometry("900x700")
        detail_window.transient(self.root)
        detail_window.grab_set()
        
        # Cadre principal
        main_frame = ttk.Frame(detail_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, text=doc.get('title', 'Sans titre'), 
                               font=('Arial', 14, 'bold'), wraplength=800)
        title_label.pack(pady=(0, 10))
        
        # Métadonnées
        meta_frame = ttk.LabelFrame(main_frame, text="Métadonnées", padding=10)
        meta_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Grille pour les métadonnées
        metadata = [
            ("ID", doc.get('id', '')),
            ("Auteur", doc.get('author', 'Inconnu')),
            ("Source", doc.get('source', 'Inconnu')),
            ("Date", doc.get('date', 'Non spécifiée')),
            ("URL", doc.get('url', 'Non disponible'))
        ]
        
        for i, (label, value) in enumerate(metadata):
            ttk.Label(meta_frame, text=f"{label}:", font=('Arial', 9, 'bold')).grid(
                row=i, column=0, sticky=tk.W, pady=2)
            ttk.Label(meta_frame, text=value, wraplength=600).grid(
                row=i, column=1, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Informations supplémentaires selon la source
        extra_frame = ttk.Frame(main_frame)
        extra_frame.pack(fill=tk.X, pady=(0, 10))
        
        source = doc.get('source', '')
        if source == 'Reddit':
            ttk.Label(extra_frame, text=f"Upvotes: {doc.get('upvotes', 0)} | "
                      f"Commentaires: {doc.get('comments', 0)} | "
                      f"Subreddit: {doc.get('subreddit', 'N/A')}").pack()
        elif source == 'Arxiv':
            ttk.Label(extra_frame, text=f"Citations: {doc.get('citations', 0)} | "
                      f"Journal: {doc.get('journal', 'N/A')} | "
                      f"Catégories: {doc.get('categories', 'N/A')}").pack()
        
        # Contenu du texte
        text_frame = ttk.LabelFrame(main_frame, text="Contenu", padding=10)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, height=20)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insérer le texte
        text_content = doc.get('text', 'Aucun contenu')
        text_widget.insert('1.0', text_content)
        text_widget.config(state=tk.DISABLED)  # Lecture seule
        
        # Boutons de fermeture
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))
        
        ttk.Button(button_frame, text="Fermer", 
                  command=detail_window.destroy).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Copier le texte", 
                  command=lambda: self.copy_to_clipboard(text_content)).pack(side=tk.LEFT, padx=5)
    
    def copy_to_clipboard(self, text):
        """Copie du texte dans le presse-papier."""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copié", "Texte copié dans le presse-papier")
    
    def update_preview(self):
        """Met à jour l'aperçu des données."""
        if not self.documents:
            self.stats_label.config(text="Aucun document chargé")
            self.preview_text.delete('1.0', tk.END)
            return
        
        # Calculer les statistiques
        total_docs = len(self.documents)
        total_current = len(self.current_corpus)
        
        sources = Counter(doc.get('source', 'Inconnu') for doc in self.documents)
        authors = Counter(doc.get('author', 'Inconnu') for doc in self.documents)
        
        # Mettre à jour les statistiques
        stats_text = (f"Documents totaux: {total_docs}\n"
                     f"Documents affichés: {total_current}\n"
                     f"Sources: {len(sources)}\n"
                     f"Auteurs uniques: {len(authors)}")
        
        self.stats_label.config(text=stats_text)
        
        # Mettre à jour l'aperçu
        self.preview_text.delete('1.0', tk.END)
        
        preview_text = "APERÇU DES DONNÉES\n"
        preview_text += "=" * 50 + "\n\n"
        
        # Top sources
        preview_text += "TOP 5 SOURCES:\n"
        for source, count in sources.most_common(5):
            percentage = (count / total_docs) * 100
            preview_text += f"  {source}: {count} documents ({percentage:.1f}%)\n"
        
        preview_text += "\n TOP 5 AUTEURS:\n"
        for author, count in authors.most_common(5):
            if author != 'Inconnu':
                preview_text += f"   {author}: {count} documents\n"
        
        preview_text += "\n RÉPARTITION TEMPORELLE:\n"
        # Essayer de trouver les dates
        dates = [doc.get('date', '') for doc in self.documents if doc.get('date')]
        if dates:
            try:
                # Convertir en dates
                date_objs = []
                for date_str in dates:
                    try:
                        if len(date_str) >= 10:
                            date_obj = datetime.strptime(date_str[:10], "%Y-%m-%d")
                            date_objs.append(date_obj)
                    except:
                        continue
                
                if date_objs:
                    min_date = min(date_objs).strftime("%d/%m/%Y")
                    max_date = max(date_objs).strftime("%d/%m/%Y")
                    preview_text += f"  • De {min_date} à {max_date}\n"
                    preview_text += f"  • {len(date_objs)} documents datés\n"
            except:
                preview_text += "  • Dates non analysables\n"
        
        self.preview_text.insert('1.0', preview_text)
        self.preview_text.config(state=tk.DISABLED)
    
    def search_documents(self):
        """Effectue une recherche avec les filtres."""
        if not self.documents:
            messagebox.showwarning("Aucun document", "Aucun document n'est chargé.")
            return
        
        filtered = self.documents
        applied_filters = []
        
        # Filtre par mots-clés
        if self.search_var.get():
            keywords = [k.lower().strip() for k in self.search_var.get().split() if k.strip()]
            if keywords:
                original_count = len(filtered)
                filtered = [doc for doc in filtered if 
                           any(keyword in doc.get('text', '').lower() or 
                              keyword in doc.get('title', '').lower() 
                              for keyword in keywords)]
                if len(filtered) != original_count:
                    applied_filters.append(f"Mots-clés: {self.search_var.get()}")
        
        # Filtre par auteur
        if self.author_var.get():
            search_author = self.author_var.get().lower().strip()
            if search_author:
                original_count = len(filtered)
                filtered = [doc for doc in filtered if 
                           search_author in doc.get('author', '').lower()]
                if len(filtered) != original_count:
                    applied_filters.append(f"Auteur: {self.author_var.get()}")
        
        # Filtre par source
        source_filter = self.source_var.get()
        if source_filter and source_filter != "Tous":
            original_count = len(filtered)
            filtered = [doc for doc in filtered if 
                       doc.get('source', '').lower() == source_filter.lower()]
            if len(filtered) != original_count:
                applied_filters.append(f"Source: {source_filter}")
        
        # Filtres de date
        if self.date_start_var.get():
            date_start = self.date_start_var.get().strip()
            if date_start:
                original_count = len(filtered)
                filtered = [doc for doc in filtered if 
                           doc.get('date', '') >= date_start]
                if len(filtered) != original_count:
                    applied_filters.append(f"Date début: {date_start}")
        
        if self.date_end_var.get():
            date_end = self.date_end_var.get().strip()
            if date_end:
                original_count = len(filtered)
                filtered = [doc for doc in filtered if 
                           doc.get('date', '') <= date_end]
                if len(filtered) != original_count:
                    applied_filters.append(f"Date fin: {date_end}")
        
        # Mettre à jour le corpus courant
        self.current_corpus = filtered
        self.display_documents()
        
        # Message de résultats
        if applied_filters:
            sources = Counter(doc.get('source', 'Inconnu') for doc in filtered)
            result_text = f"{len(filtered)} document(s) trouvé(s)\n\n"
            result_text += "Filtres appliqués:\n"
            for filt in applied_filters:
                result_text += f" {filt}\n"
            
            result_text += "\nRépartition par source:\n"
            for source, count in sources.items():
                result_text += f" {source}: {count} document(s)\n"
            
            messagebox.showinfo("Résultats de la recherche", result_text)
        else:
            messagebox.showinfo("Résultats", f"{len(filtered)} document(s) affiché(s)")
    
    def reset_filters(self):
        """Réinitialise tous les filtres."""
        self.search_var.set("")
        self.author_var.set("")
        self.source_var.set("Tous")
        self.date_start_var.set("")
        self.date_end_var.set("")
        self.current_corpus = self.documents
        self.display_documents()
        messagebox.showinfo("Filtres réinitialisés", 
                          "Tous les filtres ont été réinitialisés.\n"
                          f"Affichage de tous les documents ({len(self.documents)}).")
    
    def set_corpus(self, corpus_id):
        """Définit un corpus pour la comparaison."""
        if not self.current_corpus:
            messagebox.showwarning("Aucun document", 
                                 "Aucun document à ajouter au corpus.")
            return
        
        if corpus_id == 'A':
            self.corpus_a = self.current_corpus.copy()
            sources = Counter(doc.get('source', 'Inconnu') for doc in self.corpus_a)
            source_text = "\n".join([f"• {s}: {c} docs" for s, c in sources.items()])
            messagebox.showinfo("Corpus A défini", 
                              f"Corpus A défini avec {len(self.corpus_a)} document(s)\n\n"
                              f"Répartition:\n{source_text}")
        else:
            self.corpus_b = self.current_corpus.copy()
            sources = Counter(doc.get('source', 'Inconnu') for doc in self.corpus_b)
            source_text = "\n".join([f"• {s}: {c} docs" for s, c in sources.items()])
            messagebox.showinfo("Corpus B défini", 
                              f"Corpus B défini avec {len(self.corpus_b)} document(s)\n\n"
                              f"Répartition:\n{source_text}")
    
    def compare_corpora(self):
        """Compare deux corpus."""
        if not self.corpus_a or not self.corpus_b:
            messagebox.showerror("Erreur", 
                               "Veuillez définir les deux corpus (A et B) avant de comparer.")
            return
        
        # Créer une fenêtre de résultats
        result_window = tk.Toplevel(self.root)
        result_window.title("Comparaison de Corpus A vs B")
        result_window.geometry("1000x700")
        
        # Notebook pour organiser les résultats
        notebook = ttk.Notebook(result_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet 1: Vue d'ensemble
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="Vue d'ensemble")
        
        text_widget = tk.Text(overview_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(overview_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Calcul des statistiques
        text_widget.insert(tk.END, "COMPARAISON CORPUS A vs B\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        
        text_widget.insert(tk.END, f" CORPUS A: {len(self.corpus_a)} documents\n")
        sources_a = Counter(doc.get('source', 'Inconnu') for doc in self.corpus_a)
        for source, count in sources_a.items():
            text_widget.insert(tk.END, f"  • {source}: {count} documents\n")
        
        text_widget.insert(tk.END, f"\n CORPUS B: {len(self.corpus_b)} documents\n")
        sources_b = Counter(doc.get('source', 'Inconnu') for doc in self.corpus_b)
        for source, count in sources_b.items():
            text_widget.insert(tk.END, f"  • {source}: {count} documents\n")
        
        # Calcul des mots
        words_a = self.get_corpus_words(self.corpus_a)
        words_b = self.get_corpus_words(self.corpus_b)
        
        # Mots communs et spécifiques
        common_words = set(words_a.keys()) & set(words_b.keys())
        specific_a = set(words_a.keys()) - set(words_b.keys())
        specific_b = set(words_b.keys()) - set(words_a.keys())
        
        text_widget.insert(tk.END, "\n ANALYSE VOCABULAIRE\n")
        text_widget.insert(tk.END, "-" * 40 + "\n")
        text_widget.insert(tk.END, f"• Mots communs: {len(common_words)}\n")
        text_widget.insert(tk.END, f"• Mots spécifiques à A: {len(specific_a)}\n")
        text_widget.insert(tk.END, f"• Mots spécifiques à B: {len(specific_b)}\n")
        
        # Afficher quelques exemples
        text_widget.insert(tk.END, "\n TOP 10 MOTS COMMUNS:\n")
        common_counter = Counter({k: words_a[k] + words_b[k] for k in common_words})
        for word, count in common_counter.most_common(10):
            text_widget.insert(tk.END, f" '{word}': {count} occurrences\n")
        
        text_widget.insert(tk.END, "\n TOP 5 MOTS SPÉCIFIQUES À A:\n")
        specific_a_counter = Counter({k: words_a[k] for k in specific_a})
        for word, count in specific_a_counter.most_common(5):
            text_widget.insert(tk.END, f" '{word}': {count} occurrences\n")
        
        text_widget.insert(tk.END, "\n TOP 5 MOTS SPÉCIFIQUES À B:\n")
        specific_b_counter = Counter({k: words_b[k] for k in specific_b})
        for word, count in specific_b_counter.most_common(5):
            text_widget.insert(tk.END, f" '{word}': {count} occurrences\n")
        
        text_widget.config(state=tk.DISABLED)
        
        # Onglet 2: TF-IDF
        tfidf_frame = ttk.Frame(notebook)
        notebook.add(tfidf_frame, text="TF-IDF")
        
        tfidf_text = tk.Text(tfidf_frame, wrap=tk.WORD)
        tfidf_scrollbar = ttk.Scrollbar(tfidf_frame, orient=tk.VERTICAL, command=tfidf_text.yview)
        tfidf_text.configure(yscrollcommand=tfidf_scrollbar.set)
        
        tfidf_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tfidf_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Calcul TF-IDF
        all_documents = self.corpus_a + self.corpus_b
        tfidf_a = self.calculate_tfidf(self.corpus_a, all_documents)
        tfidf_b = self.calculate_tfidf(self.corpus_b, all_documents)
        
        tfidf_text.insert(tk.END, "SCORES TF-IDF\n")
        tfidf_text.insert(tk.END, "=" * 40 + "\n\n")
        
        tfidf_text.insert(tk.END, "TOP 15 TF-IDF - CORPUS A:\n")
        for word, score in list(tfidf_a.items())[:15]:
            tfidf_text.insert(tk.END, f"  • {word}: {score:.4f}\n")
        
        tfidf_text.insert(tk.END, "\n TOP 15 TF-IDF - CORPUS B:\n")
        for word, score in list(tfidf_b.items())[:15]:
            tfidf_text.insert(tk.END, f"  • {word}: {score:.4f}\n")
        
        tfidf_text.config(state=tk.DISABLED)
        
        # Onglet 3: Visualisation
        viz_frame = ttk.Frame(notebook)
        notebook.add(viz_frame, text="Visualisation")
        
        # Créer un graphique simple
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Graphique 1: Répartition des sources
        sources_a_counts = list(sources_a.values())
        sources_a_labels = list(sources_a.keys())
        
        axes[0].pie(sources_a_counts, labels=sources_a_labels, autopct='%1.1f%%')
        axes[0].set_title('Corpus A - Répartition par source')
        
        # Graphique 2: Répartition des sources
        sources_b_counts = list(sources_b.values())
        sources_b_labels = list(sources_b.keys())
        
        axes[1].pie(sources_b_counts, labels=sources_b_labels, autopct='%1.1f%%')
        axes[1].set_title('Corpus B - Répartition par source')
        
        plt.tight_layout()
        
        # Afficher dans Tkinter
        canvas = FigureCanvasTkAgg(fig, master=viz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def get_corpus_words(self, corpus):
        """Extrait et compte les mots d'un corpus."""
        words = []
        for doc in corpus:
            text = doc.get('text', '') + ' ' + doc.get('title', '')
            # Tokenisation simple
            tokens = re.findall(r'\b\w+\b', text.lower())
            words.extend(tokens)
        
        return Counter(words)
    
    def calculate_tfidf(self, corpus, all_documents):
        """Calcule TF-IDF pour un corpus donné."""
        # TF dans le corpus
        word_counts = self.get_corpus_words(corpus)
        total_words = sum(word_counts.values())
        
        # IDF sur tous les documents
        doc_count = len(all_documents)
        word_doc_count = {}
        
        for doc in all_documents:
            text = doc.get('text', '') + ' ' + doc.get('title', '')
            tokens = set(re.findall(r'\b\w+\b', text.lower()))
            for token in tokens:
                word_doc_count[token] = word_doc_count.get(token, 0) + 1
        
        # Calcul TF-IDF
        tfidf_scores = {}
        for word, count in word_counts.items():
            tf = count / total_words if total_words > 0 else 0
            idf = log(doc_count / (word_doc_count.get(word, 1) + 1)) + 1
            tfidf_scores[word] = tf * idf
        
        return dict(sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True))
    
    def calculate_and_display_tfidf(self):
        """Calcule et affiche le TF-IDF pour le corpus actuel."""
        if not self.current_corpus:
            messagebox.showwarning("Aucun document", 
                                 "Aucun document à analyser.")
            return
        
        # Calculer TF-IDF
        tfidf_scores = self.calculate_tfidf(self.current_corpus, self.current_corpus)
        
        # Afficher dans la zone de texte
        self.tfidf_text.delete('1.0', tk.END)
        
        self.tfidf_text.insert(tk.END, "ANALYSE TF-IDF DU CORPUS ACTUEL\n")
        self.tfidf_text.insert(tk.END, "=" * 50 + "\n\n")
        self.tfidf_text.insert(tk.END, f"Documents analysés: {len(self.current_corpus)}\n\n")
        
        self.tfidf_text.insert(tk.END, "TOP 20 MOTS PAR SCORE TF-IDF:\n")
        for i, (word, score) in enumerate(list(tfidf_scores.items())[:20], 1):
            self.tfidf_text.insert(tk.END, f"{i:2d}. {word:<20} {score:.6f}\n")
        
        # Ajouter des statistiques
        word_counts = self.get_corpus_words(self.current_corpus)
        total_words = sum(word_counts.values())
        unique_words = len(word_counts)
        
        self.tfidf_text.insert(tk.END, f"\n Statistiques:\n")
        self.tfidf_text.insert(tk.END, f"• Total mots: {total_words}\n")
        self.tfidf_text.insert(tk.END, f"• Mots uniques: {unique_words}\n")
        self.tfidf_text.insert(tk.END, f"• Moyenne mots/document: {total_words/len(self.current_corpus):.1f}\n")
        
        self.tfidf_text.config(state=tk.DISABLED)
    
    def plot_temporal_evolution(self):
        """Affiche l'évolution temporelle d'un mot."""
        word = self.word_var.get().strip().lower()
        if not word:
            messagebox.showerror("Erreur", "Veuillez entrer un mot à analyser.")
            return
        
        # Collecter les données
        period_data = {}
        source_data = {}
        
        for doc in self.documents:
            date_str = doc.get('date', '')
            if not date_str:
                continue
            
            try:
                # Extraire l'année et le mois
                if len(date_str) >= 7 and '-' in date_str:
                    period = date_str[:7]  # YYYY-MM
                elif len(date_str) >= 4:
                    period = date_str[:4]  # YYYY
                else:
                    continue
                
                text = doc.get('text', '').lower()
                source = doc.get('source', 'Inconnu')
                
                # Compter les occurrences
                count = text.count(word)
                
                # Données par période
                if period not in period_data:
                    period_data[period] = {'count': 0, 'docs': 0}
                period_data[period]['count'] += count
                period_data[period]['docs'] += 1
                
                # Données par source
                if source not in source_data:
                    source_data[source] = {'count': 0, 'docs': 0}
                source_data[source]['count'] += count
                source_data[source]['docs'] += 1
                
            except Exception as e:
                continue
        
        if not period_data:
            messagebox.showinfo("Information", 
                              "Pas de données temporelles disponibles pour ce mot.")
            return
        
        # Créer les graphiques
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()
        
        # Graphique 1: Évolution générale
        periods = sorted(period_data.keys())
        frequencies = [period_data[p]['count'] / max(period_data[p]['docs'], 1) 
                      for p in periods]
        
        axes[0].plot(periods, frequencies, marker='o', linewidth=2, color='blue')
        axes[0].set_xlabel('Période')
        axes[0].set_ylabel(f'Fréquence de "{word}"')
        axes[0].set_title(f'Évolution temporelle de "{word}"')
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(True, alpha=0.3)
        
        # Graphique 2: Barres par période
        axes[1].bar(periods, [period_data[p]['count'] for p in periods], color='orange')
        axes[1].set_xlabel('Période')
        axes[1].set_ylabel(f'Occurrences totales')
        axes[1].set_title(f'Occurrences de "{word}" par période')
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].grid(True, alpha=0.3, axis='y')
        
        # Graphique 3: Par source
        if len(source_data) > 1:
            sources = list(source_data.keys())
            source_freqs = [source_data[s]['count'] / max(source_data[s]['docs'], 1) 
                           for s in sources]
            
            axes[2].bar(sources, source_freqs, color='green')
            axes[2].set_xlabel('Source')
            axes[2].set_ylabel(f'Fréquence moyenne')
            axes[2].set_title(f'Fréquence de "{word}" par source')
            axes[2].tick_params(axis='x', rotation=45)
            axes[2].grid(True, alpha=0.3, axis='y')
        
        # Graphique 4: Top 10 périodes
        top_periods = sorted(period_data.items(), 
                            key=lambda x: x[1]['count'], 
                            reverse=True)[:10]
        top_labels = [p[0] for p in top_periods]
        top_counts = [p[1]['count'] for p in top_periods]
        
        axes[3].barh(top_labels, top_counts, color='purple')
        axes[3].set_xlabel('Occurrences')
        axes[3].set_ylabel('Période')
        axes[3].set_title(f'Top 10 périodes pour "{word}"')
        axes[3].grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        # Afficher dans Tkinter
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        canvas = FigureCanvasTkAgg(fig, master=self.viz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Boutons de contrôle
        control_frame = ttk.Frame(self.viz_frame)
        control_frame.pack(pady=10)
        
        ttk.Button(control_frame, text=" Sauvegarder", 
                  command=lambda: self.save_figure(fig)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Actualiser", 
                  command=self.plot_temporal_evolution).pack(side=tk.LEFT, padx=5)
        
        # Afficher des statistiques
        total_occurrences = sum(period_data[p]['count'] for p in period_data)
        total_docs = sum(period_data[p]['docs'] for p in period_data)
        
        stats_text = (f" Statistiques pour '{word}':\n"
                     f" Occurrences totales: {total_occurrences}\n"
                     f" Documents analysés: {total_docs}\n"
                     f" Périodes couvertes: {len(periods)}\n"
                     f" Fréquence moyenne: {total_occurrences/max(total_docs, 1):.4f}")
        
        ttk.Label(self.viz_frame, text=stats_text, 
                 font=('Arial', 10)).pack(pady=5)
    
    def save_figure(self, fig):
        """Sauvegarde le graphique dans un fichier."""
        word = self.word_var.get().strip().lower()
        if not word:
            word = "mot"
        
        filename = f"evolution_{word}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        messagebox.showinfo("Sauvegarde", 
                          f"Graphique sauvegardé sous:\n{filename}")
    
    def show_statistics(self):
        """Affiche les statistiques détaillées."""
        if not self.documents:
            messagebox.showinfo("Statistiques", "Aucun document chargé.")
            return
        
        # Créer une fenêtre de statistiques
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistiques détaillées")
        stats_window.geometry("800x600")
        
        # Notebook pour organiser
        notebook = ttk.Notebook(stats_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet 1: Vue d'ensemble
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="Vue d'ensemble")
        
        text_widget = tk.Text(overview_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(overview_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Calculer les statistiques
        total_docs = len(self.documents)
        
        # Par source
        sources = Counter(doc.get('source', 'Inconnu') for doc in self.documents)
        
        # Par auteur
        authors = Counter(doc.get('author', 'Inconnu') for doc in self.documents)
        
        # Textes
        text_lengths = [len(doc.get('text', '')) for doc in self.documents]
        avg_text_length = sum(text_lengths) / max(total_docs, 1)
        
        # Dates
        dates = [doc.get('date', '') for doc in self.documents if doc.get('date')]
        
        text_widget.insert(tk.END, " STATISTIQUES GLOBALES\n")
        text_widget.insert(tk.END, "=" * 40 + "\n\n")
        
        text_widget.insert(tk.END, f" Documents totaux: {total_docs}\n\n")
        
        text_widget.insert(tk.END, "RÉPARTITION PAR SOURCE:\n")
        for source, count in sources.most_common():
            percentage = (count / total_docs) * 100
            text_widget.insert(tk.END, f"  {source}: {count} documents ({percentage:.1f}%)\n")
        
        text_widget.insert(tk.END, f"\n AUTEURS UNIQUES: {len(authors)}\n")
        text_widget.insert(tk.END, "TOP 10 AUTEURS:\n")
        for author, count in authors.most_common(10):
            if author != 'Inconnu':
                text_widget.insert(tk.END, f" {author}: {count} documents\n")
        
        text_widget.insert(tk.END, f"\n LONGUEUR DES TEXTES:\n")
        text_widget.insert(tk.END, f"  Moyenne: {avg_text_length:.0f} caractères\n")
        text_widget.insert(tk.END, f"  Minimum: {min(text_lengths) if text_lengths else 0}\n")
        text_widget.insert(tk.END, f"  Maximum: {max(text_lengths) if text_lengths else 0}\n")
        
        if dates:
            text_widget.insert(tk.END, f"\n DOCUMENTS DATÉS: {len(dates)}\n")
            try:
                # Trouver les dates extrêmes
                date_objs = []
                for date_str in dates:
                    if len(date_str) >= 10 and '-' in date_str:
                        try:
                            date_obj = datetime.strptime(date_str[:10], "%Y-%m-%d")
                            date_objs.append(date_obj)
                        except:
                            continue
                
                if date_objs:
                    min_date = min(date_objs).strftime("%d/%m/%Y")
                    max_date = max(date_objs).strftime("%d/%m/%Y")
                    text_widget.insert(tk.END, f" Période: {min_date} à {max_date}\n")
            except:
                pass
        
        text_widget.config(state=tk.DISABLED)
        
        # Onglet 2: Analyse du vocabulaire
        vocab_frame = ttk.Frame(notebook)
        notebook.add(vocab_frame, text="Vocabulaire")
        
        vocab_text = tk.Text(vocab_frame, wrap=tk.WORD)
        vocab_scrollbar = ttk.Scrollbar(vocab_frame, orient=tk.VERTICAL, command=vocab_text.yview)
        vocab_text.configure(yscrollcommand=vocab_scrollbar.set)
        
        vocab_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vocab_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Analyser le vocabulaire
        all_words = []
        for doc in self.documents:
            text = doc.get('text', '') + ' ' + doc.get('title', '')
            tokens = re.findall(r'\b\w+\b', text.lower())
            all_words.extend(tokens)
        
        word_counts = Counter(all_words)
        total_words = len(all_words)
        unique_words = len(word_counts)
        
        vocab_text.insert(tk.END, "ANALYSE DU VOCABULAIRE\n")
        vocab_text.insert(tk.END, "=" * 40 + "\n\n")
        
        vocab_text.insert(tk.END, f" Statistiques:\n")
        vocab_text.insert(tk.END, f" Mots totaux: {total_words:,}\n")
        vocab_text.insert(tk.END, f" Mots uniques: {unique_words:,}\n")
        vocab_text.insert(tk.END, f" Taux d'unicité: {(unique_words/total_words*100 if total_words>0 else 0):.1f}%\n")
        vocab_text.insert(tk.END, f" Mots/document: {(total_words/total_docs):.1f}\n\n")
        
        vocab_text.insert(tk.END, " TOP 50 MOTS LES PLUS FRÉQUENTS:\n")
        for i, (word, count) in enumerate(word_counts.most_common(50), 1):
            percentage = (count / total_words) * 100
            vocab_text.insert(tk.END, f"{i:2d}. {word:<20} {count:>6} ({percentage:.2f}%)\n")
        
        vocab_text.config(state=tk.DISABLED)
    
    def reload_corpus(self):
        """Recharge tous les corpus."""
        response = messagebox.askyesno("Rechargement", 
                                      "Voulez-vous recharger tous les corpus?\n"
                                      "Cela effacera les filtres actuels.")
        
        if response:
            self.documents = []
            self.current_corpus = []
            self.corpus_a = []
            self.corpus_b = []
            
            self.load_all_corpora()
            self.reset_filters()
    
    def show_diagnostic(self):
        """Affiche un diagnostic du système."""
        import platform
        import sys
        
        diagnostic_window = tk.Toplevel(self.root)
        diagnostic_window.title(" Diagnostic système")
        diagnostic_window.geometry("700x500")
        
        text_widget = tk.Text(diagnostic_window, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(diagnostic_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert(tk.END, " DIAGNOSTIC SYSTÈME\n")
        text_widget.insert(tk.END, "=" * 40 + "\n\n")
        
        # Informations système
        text_widget.insert(tk.END, " SYSTÈME:\n")
        text_widget.insert(tk.END, f" OS: {platform.system()} {platform.release()}\n")
        text_widget.insert(tk.END, f" Python: {platform.python_version()}\n")
        text_widget.insert(tk.END, f" Architecture: {platform.architecture()[0]}\n\n")
        
        # Informations corpus
        text_widget.insert(tk.END, "CORPUS:\n")
        text_widget.insert(tk.END, f" Documents totaux: {len(self.documents)}\n")
        text_widget.insert(tk.END, f" Corpus actuel: {len(self.current_corpus)}\n")
        text_widget.insert(tk.END, f" Corpus A: {len(self.corpus_a)}\n")
        text_widget.insert(tk.END, f" Corpus B: {len(self.corpus_b)}\n\n")
        
        # Fichiers chargés
        text_widget.insert(tk.END, " FICHIERS:\n")
        
        files_to_check = [
            'C:/Users/surface laptop 2/Desktop/Master1-Lyon2/PYTHON/Projet_Python/V1(TD3-5)/TD9-10/corpus_discours_us_simple.json',
            'C:/Users/surface laptop 2/Desktop/Master1-Lyon2/PYTHON/Projet_Python/reddit_data.json',
            'C:/Users/surface laptop 2/Desktop/Master1-Lyon2/PYTHON/Projet_Python/arxiv_data.json'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                size_mb = size / (1024 * 1024)
                text_widget.insert(tk.END, f" {file_path}\n")
                text_widget.insert(tk.END, f"    Taille: {size_mb:.2f} MB\n")
            else:
                text_widget.insert(tk.END, f"{file_path}\n")
                text_widget.insert(tk.END, f" Fichier non trouvé\n")
        
        # Mémoire
        text_widget.insert(tk.END, "\n MÉMOIRE:\n")
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            text_widget.insert(tk.END, f" Utilisation: {memory_mb:.1f} MB\n")
        except:
            text_widget.insert(tk.END, " psutil non disponible\n")
        
        text_widget.config(state=tk.DISABLED)
        
        # Boutons
        button_frame = ttk.Frame(diagnostic_window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Fermer", 
                  command=diagnostic_window.destroy).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Copier le diagnostic", 
                  command=lambda: self.copy_to_clipboard(text_widget.get('1.0', tk.END))).pack(side=tk.LEFT, padx=5)
    
    def export_results(self):
        """Exporte les résultats au format CSV."""
        if not self.current_corpus:
            messagebox.showwarning("Aucun document", 
                                 "Aucun document à exporter.")
            return
        
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")],
            title="Exporter les résultats"
        )
        
        if not filename:
            return
        
        try:
            # Préparer les données
            data = []
            for doc in self.current_corpus:
                row = {
                    'ID': doc.get('id', ''),
                    'Titre': doc.get('title', ''),
                    'Auteur': doc.get('author', ''),
                    'Source': doc.get('source', ''),
                    'Date': doc.get('date', ''),
                    'URL': doc.get('url', ''),
                    'Texte': doc.get('text', '')[:500]  # Limiter la taille
                }
                
                # Ajouter des champs spécifiques
                if doc.get('source') == 'Reddit':
                    row['Upvotes'] = doc.get('upvotes', '')
                    row['Commentaires'] = doc.get('comments', '')
                elif doc.get('source') == 'Arxiv':
                    row['Citations'] = doc.get('citations', '')
                    row['Journal'] = doc.get('journal', '')
                
                data.append(row)
            
            # Créer un DataFrame et sauvegarder
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            messagebox.showinfo("Export réussi", 
                              f"Les données ont été exportées avec succès dans:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur d'export", 
                               f"Une erreur est survenue lors de l'export:\n{str(e)}")

# Point d'entrée principal
def main():
    """Fonction principale."""
    try:
        root = tk.Tk()
        app = CorpusExplorer(root)
        
        # Centre la fenêtre
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Gestion de la fermeture
        def on_closing():
            if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application?"):
                root.destroy()
                sys.exit(0)
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        root.mainloop()
        
    except Exception as e:
        print(f" Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("Erreur", f"Une erreur est survenue:\n{str(e)}")

if __name__ == "__main__":

    main()
