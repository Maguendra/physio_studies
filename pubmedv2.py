import pandas as pd
import json
from Bio import Entrez

#code inspiré du travail de TLDWTutorials : https://github.com/TLDWTutorials/PubmedAPI/tree/main
def configuration(email):
    Entrez.email = email

def build_query():
    return "physiotherapy and mulligan"

def get_publication_date(record):
    article = record.get('MedlineCitation', {}).get('Article', {})

    # 1) Date la plus précise si disponible
    article_dates = article.get('ArticleDate', [])
    if article_dates:
        d = article_dates[0]
        y = d.get('Year', '')
        m = d.get('Month', '')
        day = d.get('Day', '')
        return '-'.join(part for part in [y, m, day] if part)

    # 2) Sinon date du journal
    pub_date = article.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
    if isinstance(pub_date, dict):
        y = pub_date.get('Year', '')
        m = pub_date.get('Month', '')
        day = pub_date.get('Day', '')
        if y or m or day:
            return '-'.join(part for part in [y, m, day] if part)
        return pub_date.get('MedlineDate', '')

    return ''


def fetch_pmids(query, retmax=5):
# Recherche dans pubmed les études en kinésithérapie et mulligan
    handle = Entrez.esearch(db='pubmed', retmax=5, term="physiotherapy and mulligan")
    record = Entrez.read(handle)
    return record['IdList'] #obtention des PMID, les identifiants uniques de chaque étude


def fetch_articles(pmids):
# Récupération des informations pour chaque PMID
    rows = []

    for pmid in pmids:
        handle = Entrez.efetch(db='pubmed', id=pmid, retmode='xml')
        records = Entrez.read(handle)
        
        for record in records['PubmedArticle']:
            # Print the record in a formatted JSON style
            print(json.dumps(record, indent=4, default=str)) 
            
            title = record['MedlineCitation']['Article']['ArticleTitle']
            abstract = ' '.join(record['MedlineCitation']['Article']['Abstract']['AbstractText']) if 'Abstract' in record['MedlineCitation']['Article'] and 'AbstractText' in record['MedlineCitation']['Article']['Abstract'] else ''
            authors = ', '.join(author.get('LastName', '') + ' ' + author.get('ForeName', '') for author in record['MedlineCitation']['Article']['AuthorList'])
            journal = record['MedlineCitation']['Article']['Journal']['Title']
            keywords = ', '.join(keyword['DescriptorName'] for keyword in record['MedlineCitation']['MeshHeadingList']) if 'MeshHeadingList' in record['MedlineCitation'] else ''
            url = f"https://www.ncbi.nlm.nih.gov/pubmed/{pmid}"
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

def save_results(rows, excel_path="PubMed_resultsx.xlsx", json_path="resultats_pubmed.json"):
    df = pd.DataFrame(rows)
    df.to_excel(excel_path, index=False)
    df.to_json(json_path, orient="records", force_ascii=False)


def main():
    configuration("maguendra@gmail.com")
    query = build_query()
    pmids = fetch_pmids(query, retmax=5)
    rows = fetch_articles(pmids)
    save_results(rows)


if __name__ == "__main__":
    main()