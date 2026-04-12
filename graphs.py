import pandas as pd
import plotly.express as px


#compte le nombre d'études par an et produit un graphique

def build_publications_by_year_df(json_path="resultats_pubmed.json"):
    df = pd.read_json(json_path)

    if "PublicationDate" not in df.columns:
        raise ValueError("La colonne 'PublicationDate' est absente des donnees.")

    # Extrait l'annee meme si la date n'est pas strictement au format ISO.
    year_series = df["PublicationDate"].astype(str).str.extract(r"(\d{4})", expand=False)
    year_series = pd.to_numeric(year_series, errors="coerce")

    publications_by_year = (
        year_series.dropna()
        .astype(int)
        .value_counts()
        .sort_index()
        .rename_axis("Year")
        .reset_index(name="StudyCount")
    )

    return publications_by_year


def plot_publications_by_year(json_path="resultats_pubmed.json"):
    publications_by_year = build_publications_by_year_df(json_path)

    fig = px.bar(
        publications_by_year,
        x="Year",
        y="StudyCount",
        text="StudyCount",
        title="Nombre d'etudes publiees par annee",
        labels={"Year": "Annee", "StudyCount": "Nombre d'etudes"},
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis=dict(dtick=1), xaxis=dict(type="category"))

    return fig


if __name__ == "__main__":
    fig = plot_publications_by_year("resultats_pubmed.json")
    fig.show()
