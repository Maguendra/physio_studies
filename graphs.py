import json
from collections import Counter
from pathlib import Path

import plotly.graph_objects as go


MULLIGAN_FILE = Path("mulligan_studies.json")
MDT_FILE = Path("mdt_studies.json")
OUTPUT_HTML = Path("publications_evolution.html")

#Compte le nombre d'étude selon le concept
def study_count(fichier):
    with open(fichier, 'r') as f:
        data = json.load(f)
        results =data.get("results", [])
        print(len(results))


study_count(MULLIGAN_FILE)