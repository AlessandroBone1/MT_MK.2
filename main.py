import torch
from ultralytics import YOLO
import cv2
import requests
import os
from pathlib import Path

GITHUB_REPO = "AlessandroBone1/MT_MK.2"
MODEL_FILENAME = "best2.pt"
MODEL_PATH = Path(MODEL_FILENAME)
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/commits?path={MODEL_FILENAME}"

def download_model(url, output_path):
    response = requests.get(url)
    response.raise_for_status()  
    with open(output_path, 'wb') as file:
        file.write(response.content)

def check_for_model_update():
    response = requests.get(GITHUB_API_URL)
    response.raise_for_status()
    commits = response.json()

    if not commits:
        print("Nessun commit trovato per il modello.")
        return False

    latest_commit_sha = commits[0]['sha']
    latest_commit_url = commits[0]['html_url']
    latest_commit_date = commits[0]['commit']['committer']['date']
    print(f"Ultimo commit per il modello: {latest_commit_sha} ({latest_commit_date})")

    last_sha_path = Path("last_commit_sha.txt")
    if last_sha_path.exists():
        with open(last_sha_path, 'r') as file:
            last_sha = file.read().strip()
    else:
        last_sha = ""

    if latest_commit_sha != last_sha:
        print(f"Aggiornamento disponibile: {latest_commit_url}")
        download_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{MODEL_FILENAME}"
        download_model(download_url, MODEL_PATH)
        with open(last_sha_path, 'w') as file:
            file.write(latest_commit_sha)
        return True

    return False

if check_for_model_update():
    print(f"Modello aggiornato a {MODEL_PATH}")
else:
    print("Modello già aggiornato.")

model = YOLO(str(MODEL_PATH))
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    results = model(frame)
    
    for result in results:
        boxes = result.boxes
        
        if len(boxes) > 0:
            print("Fuoco rilevato!")
        else: 
            print("NULLA")    

        annotated_frame = results[0].plot()
        
        cv2.imshow("Rilevamento Fuoco", annotated_frame)
    
    # Esci con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
