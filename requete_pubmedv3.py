import argparse
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


def save_results(df, json_path, excel_path="PubMed_resultsx.xlsx", csv_path="", no_excel=False):
    if not no_excel:
        df.to_excel(excel_path, index=False)

    df.to_json(json_path, orient="records", force_ascii=False, indent=2)

    if csv_path:
        df.to_csv(csv_path, index=False)

    return df


def get_pubmed_dataframe(
    email="maguendra@gmail.com",
    query="",
    retmax=5,
    save=False,
    excel_path="PubMed_resultsx.xlsx",
    json_path="resultats_pubmed.json",
    csv_path="",
    no_excel=False,
    verbose=False,
):
    Entrez.email = email

    pmids = fetch_pmids(query, retmax)
    rows = fetch_rows(pmids, verbose=verbose)
    df = build_dataframe(rows)

    if save:
        save_results(
            df,
            json_path=json_path,
            excel_path=excel_path,
            csv_path=csv_path,
            no_excel=no_excel,
        )

    return df


def parse_args():
    parser = argparse.ArgumentParser(
        description="Recherche PubMed et export des resultats (Excel, JSON, CSV)."
    )
    parser.add_argument(
        "--query",
        required=True,
        help='Requete PubMed, ex: "physiotherapy AND mckenzie"',
    )
    parser.add_argument("--email", required=True, help="Email requis par NCBI Entrez")
    parser.add_argument("--retmax", type=int, default=5, help="Nombre max de resultats")
    parser.add_argument("--excel", default="PubMed_resultsx.xlsx", help="Fichier Excel")
    parser.add_argument("--json", default="resultats_pubmed.json", help="Fichier JSON")
    parser.add_argument("--csv", default="", help="Fichier CSV optionnel")
    parser.add_argument(
        "--no-excel",
        action="store_true",
        help="Desactive l export Excel (utile si openpyxl absent)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Affiche les enregistrements bruts Entrez",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    df = get_pubmed_dataframe(
        email=args.email,
        query=args.query,
        retmax=args.retmax,
        save=True,
        excel_path=args.excel,
        json_path=args.json,
        csv_path=args.csv,
        no_excel=args.no_excel,
        verbose=args.verbose,
    )

    print(f"Termine: {len(df)} etudes exportees")


if __name__ == "__main__":
    main()