import os
import time
import requests
from pathlib import Path
from filecmp import cmp

GITHUB_REPO = "AlessandroBone1/MT_MK.2"
MODEL_FILENAME = "best2.pt"
MODEL_PATH = Path(MODEL_FILENAME)
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{MODEL_FILENAME}"

def download_model(url, output_path):
    response = requests.get(url)
    response.raise_for_status()
    with open(output_path, 'wb') as file:
        file.write(response.content)

def check_and_update_model():
    temp_model_path = Path("temp_model.pt")
    download_model(GITHUB_RAW_URL, temp_model_path)
    
    if not MODEL_PATH.exists() or not cmp(MODEL_PATH, temp_model_path, shallow=False):
        print("Modello aggiornato rilevato. Aggiornamento in corso...")
        download_model(GITHUB_RAW_URL, MODEL_PATH)
        print("Modello aggiornato correttamente.")
    else:
        print("Il modello è già aggiornato.")
    
    if temp_model_path.exists():
        temp_model_path.unlink()

while True:
    check_and_update_model()
    time.sleep(300)  
