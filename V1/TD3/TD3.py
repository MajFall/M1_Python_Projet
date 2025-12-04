# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

# %%
# Partie 1.1 : Reddit
import praw
reddit = praw.Reddit(client_id='rszoFwH_2YUIELX9D3FGWw',
                     client_secret='1t2sraMxx3vtC6_S9_4jW0aRNgCE9w',
                     user_agent='docs')

theme = "football"

# Liste pour Reddit uniquement
docs_reddit = []

for post in reddit.subreddit(theme).hot(limit=10):
    texte = post.selftext.replace("\n", " ").strip()
    if texte:
        docs_reddit.append(texte)

print(f"{len(docs_reddit)} documents extraits depuis Reddit.")
print(f"{docs_reddit} ")
# %%

# Partie 1.2 : ArXiv
import urllib.request
import xmltodict
import ssl, certifi

#  Thème de recherche
theme = "football"

#  Requête à l'API ArXiv (version HTTPS)
url = f"https://export.arxiv.org/api/query?search_query=all:{theme}&start=0&max_results=5"

#  Contexte SSL sécurisé (utilise les certificats certifi)
context = ssl.create_default_context(cafile=certifi.where())

# Récupération des données XML depuis ArXiv
with urllib.request.urlopen(url, context=context) as response:
    data = response.read()

#  Conversion XML → dictionnaire Python
feed = xmltodict.parse(data)

#  Exploration des champs disponibles
print(feed["feed"]["entry"][0].keys())

#  Extraction des résumés
docs_arxiv = []
entries = feed["feed"]["entry"]
if isinstance(entries, dict):
    entries = [entries]  # cas où il n’y a qu’un seul résultat

for entry in entries:
    summary = entry["summary"].replace("\n", " ").strip()
    docs_arxiv.append(summary)

# Résumé des résultats
print(f"{len(docs_arxiv)} documents extraits depuis ArXiv.")
for i, doc in enumerate(docs_arxiv, 1):
    print(f"\n--- Résumé {i} ---\n{doc}")
# %%


# Partie 2 : sauvegarde
import pandas as pd 

#2.1 Combiner les deux sources
texts = docs_reddit + docs_arxiv
origins = ["reddit"] * len(docs_reddit) + ["arxiv"] * len(docs_arxiv)
ids = list(range(1, len(texts) + 1))

df = pd.DataFrame({
    "id": ids,
    "texte": texts,
    "origine": origins
})

#2.2 Sauvegarder en TSV
df.to_csv("documents.tsv", sep="\t", index=False)

# 2.3Recharger pour vérifier
df_loaded = pd.read_csv("documents.tsv", sep="\t")
print(df_loaded.head())
# %%
# Partie 3 :
# 3.1 Taille du corpus
print("Taille du corpus :", len(df_loaded))

# 3.2 Nombre de mots et de phrases
for i, row in df_loaded.iterrows():
    mots = row["texte"].split(" ")  
    phrases = row["texte"].split(".")  
    print(f"Doc {row['id']} ({row['origine']}) → {len(mots)} mots, {len(phrases)} phrases")  # CORRECTION : 'source' → 'origine'

# 3.3 Suppression des documents trop courts
df_loaded = df_loaded[df_loaded["texte"].str.len() >= 20]

# 3.4 Création d'une chaîne unique
texte_total = " ".join(df_loaded["texte"].tolist())
print("Longueur totale du texte fusionné :", len(texte_total))