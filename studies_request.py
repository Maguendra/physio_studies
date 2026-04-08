import requests
import json
import os
from pathlib import Path


def load_env_file(file_name: str = ".env") -> None:
    """Charge les variables d'un fichier .env sans ecraser l'environnement existant."""
    env_path = Path(__file__).with_name(file_name)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)

# Requête 1
# Recherche des études sur le concept Mulligan en kinésithérapie (physiotherapy) en libre accès
load_env_file()
api_key = os.getenv("OPENALEX_API_KEY")

if not api_key:
    raise RuntimeError("La variable d'environnement OPENALEX_API_KEY est manquante.")

# Requête 1
# Recherche des études sur le concept Mulligan en kinésithérapie (physiotherapy) en libre accès

url = "https://api.openalex.org/works"
params_mulligan = {
    "search": "Mulligan physiotherapy",
    "filter": "is_oa:true",
    "api_key": api_key,
}

res_mulligan = requests.get(url, params=params_mulligan, timeout=30)
res_mulligan.raise_for_status()

with open("mulligan_studies.json", "w", encoding="utf-8") as f:
    json.dump(res_mulligan.json(), f, indent=4, ensure_ascii=False)


# Requête 2
# Recherche des études sur le concept Mckenzie-MDT en kinésithérapie (physiotherapy) en libre accès
url = "https://api.openalex.org/works"
params_mdt = {
    "search": "McKenzie physiotherapy",
    "filter": "is_oa:true",
    "api_key": api_key,
}

res_mdt = requests.get(url, params=params_mdt, timeout=30)
res_mdt.raise_for_status()

with open("mdt_studies.json", "w", encoding="utf-8") as f:
    json.dump(res_mdt.json(), f, indent=4, ensure_ascii=False)

