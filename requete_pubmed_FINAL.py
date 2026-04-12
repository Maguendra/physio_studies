# *******************************************************
# Nom ......... : requete_pubmed_FINAL.py
# Role ........ : Interroger PubMed (API Entrez) et renvoyer les resultats sous forme de DataFrame pandas
# Auteur ...... : Maguendra Codandamourty
# Version ..... : V0.1 du 12/04/2026
# Licence ..... : Realise dans le cadre du cours de S2 Outils Collaboratifs (Licence Informatique)
# Dependencies  : Python 3.x, pandas, biopython
# Compilation . : Aucune (langage interprete)
# Execution ... : python3 requete_pubmed_FINAL.py
# Usage ....... : Depuis un notebook/script :
#                 from physio_studies.requete_pubmed_FINAL import get_pubmed_dataframe
#                 df = get_pubmed_dataframe(email="maguendra@gmail.com", query="mulligan and physiotherapy", retmax=50)
# *******************************************************

import json
import pandas as pd
from Bio import Entrez


def get_publication_date(record):
    article = record.get("MedlineCitation", {}).get("Article", {})

    article_dates = article.get("ArticleDate", [])
    if article_dates:
        d = article_dates[0]
        y = d.get("Year", "")
        m = d.get("Month", "")
        day = d.get("Day", "")
        return "-".join(part for part in [y, m, day] if part)

    pub_date = article.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
    if isinstance(pub_date, dict):
        y = pub_date.get("Year", "")
        m = pub_date.get("Month", "")
        day = pub_date.get("Day", "")
        if y or m or day:
            return "-".join(part for part in [y, m, day] if part)
        return pub_date.get("MedlineDate", "")

    return ""


def extract_authors(article):
    author_list = article.get("AuthorList", [])
    parts = []
    for author in author_list:
        collective = author.get("CollectiveName")
        if collective:
            parts.append(str(collective))
            continue
        last_name = author.get("LastName", "")
        fore_name = author.get("ForeName", "")
        full_name = (str(last_name) + " " + str(fore_name)).strip()
        if full_name:
            parts.append(full_name)
    return ", ".join(parts)


def extract_keywords(record):
    mesh = record.get("MedlineCitation", {}).get("MeshHeadingList", [])
    words = []
    for item in mesh:
        descriptor = item.get("DescriptorName")
        if descriptor:
            words.append(str(descriptor))
    return ", ".join(words)


def fetch_pmids(query, retmax):
    handle = Entrez.esearch(db="pubmed", retmax=retmax, term=query)
    search_record = Entrez.read(handle)
    return search_record.get("IdList", [])


def fetch_rows(pmids, verbose=False):
    rows = []

    for pmid in pmids:
        handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
        records = Entrez.read(handle)

        for record in records.get("PubmedArticle", []):
            if verbose:
                print(json.dumps(record, indent=2, default=str))

            article = record.get("MedlineCitation", {}).get("Article", {})
            title = article.get("ArticleTitle", "")

            abstract = ""
            if "Abstract" in article and "AbstractText" in article["Abstract"]:
                abstract = " ".join(str(x) for x in article["Abstract"]["AbstractText"])

            authors = extract_authors(article)
            journal = article.get("Journal", {}).get("Title", "")
            keywords = extract_keywords(record)
            url = "https://www.ncbi.nlm.nih.gov/pubmed/" + str(pmid)
            publication_date = get_publication_date(record)

            rows.append(
                {
                    "PMID": pmid,
                    "Title": title,
                    "Abstract": abstract,
                    "Authors": authors,
                    "Journal": journal,
                    "Keywords": keywords,
                    "URL": url,
                    "PublicationDate": publication_date,
                }
            )

    return rows


def build_dataframe(rows):
    return pd.DataFrame(
        rows,
        columns=[
            "PMID",
            "Title",
            "Abstract",
            "Authors",
            "Journal",
            "Keywords",
            "URL",
            "PublicationDate",
        ],
    )


def get_pubmed_dataframe(
    email="maguendra@gmail.com",
    query="",
    retmax=5 #nombre de requête par défaut    
    ):
    Entrez.email = email

    pmids = fetch_pmids(query, retmax)
    rows = fetch_rows(pmids)
    df = build_dataframe(rows)
    return df




