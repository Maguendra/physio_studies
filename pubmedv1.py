import pandas as pd
import json
from Bio import Entrez

#code inspiré du travail de TLDWTutorials : https://github.com/TLDWTutorials/PubmedAPI/tree/main

Entrez.email = 'maguendra@gmail.com'


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


# Recherche dans pubmed les études en kinésithérapie et mulligan
handle = Entrez.esearch(db='pubmed', retmax=5, term="physiotherapy and mulligan")
record = Entrez.read(handle)
id_list = record['IdList'] #obtention des PMID, les identifiants uniques de chaque étude

# Creation d'un DataFrame pour enregistrer les données
df = pd.DataFrame(columns=['PMID', 'Title', 'Abstract', 'Authors', 'Journal', 'Keywords', 'URL', 'PublicationDate'])

# Récupération des informations pour chaque PMID
for pmid in id_list:
    handle = Entrez.efetch(db='pubmed', id=pmid, retmode='xml')
    records = Entrez.read(handle)

    # Process each PubMed article in the response
    for record in records['PubmedArticle']:
        # Print the record in a formatted JSON style
        print(json.dumps(record, indent=4, default=str))  # default=str handles types JSON can't serialize like datetime
        title = record['MedlineCitation']['Article']['ArticleTitle']
        abstract = ' '.join(record['MedlineCitation']['Article']['Abstract']['AbstractText']) if 'Abstract' in record['MedlineCitation']['Article'] and 'AbstractText' in record['MedlineCitation']['Article']['Abstract'] else ''
        authors = ', '.join(author.get('LastName', '') + ' ' + author.get('ForeName', '') for author in record['MedlineCitation']['Article']['AuthorList'])
                
        journal = record['MedlineCitation']['Article']['Journal']['Title']
        keywords = ', '.join(keyword['DescriptorName'] for keyword in record['MedlineCitation']['MeshHeadingList']) if 'MeshHeadingList' in record['MedlineCitation'] else ''
        url = f"https://www.ncbi.nlm.nih.gov/pubmed/{pmid}"
        publication_date = get_publication_date(record)

        new_row = pd.DataFrame({
            'PMID': [pmid],
            'Title': [title],
            'Abstract': [abstract],
            'Authors': [authors],
            'Journal': [journal],
            'Keywords': [keywords],
            'URL': [url], 
            'PublicationDate': [publication_date]          
        })

        df = pd.concat([df, new_row], ignore_index=True)

# Save DataFrame to an Excel file
df.to_excel('PubMed_resultsx.xlsx', index=False)

#Enregistrer dans un json
df.to_json('resultats_pubmed.json')