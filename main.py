import torch
from ultralytics import YOLO
import cv2
import requests
import os
from pathlib import Path
import serial
import time

GITHUB_REPO = "AlessandroBone1/MT_MK.2"
MODEL_FILENAME = "best2.pt"
MODEL_PATH = Path(MODEL_FILENAME)
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/commits?path={MODEL_FILENAME}"

esp32 = serial.Serial('COM3', 9600)  

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

def invia_dati_esp32(distanza, posizione):
    """
    Funzione per inviare i dati all'ESP32.
    distanza: float, posizione: tuple (x, y)
    """
    # Invia i dati di distanza e posizione concatenati all'ESP32
    messaggio = f"Distanza:{distanza} Posizione:{posizione[0]},{posizione[1]}\n"
    esp32.write(messaggio.encode())  # Invia il messaggio
    time.sleep(0.1)  # Pausa breve per garantire la corretta trasmissione
    # print per controllare la recezione dei messaggi ⚠ potrebbe fermare il programma
    # print(esp32.readline())

# Variabili per il controllo manuale della telecamera
manual_mode = False
mouse_position = (0, 0)

def mouse_callback(event, x, y, flags, param):
    global manual_mode, mouse_position
    if event == cv2.EVENT_LBUTTONDOWN:
        manual_mode = not manual_mode  
        if manual_mode:
            print("Controllo manuale attivato")
        else:
            print("Controllo manuale disattivato")
    elif event == cv2.EVENT_MOUSEMOVE and manual_mode:
        mouse_position = (x, y)

if check_for_model_update():
    print(f"Modello aggiornato a {MODEL_PATH}")
else:
    print("Modello già aggiornato.")

model = YOLO(str(MODEL_PATH))
cap = cv2.VideoCapture(0)

cv2.namedWindow("Rilevamento Fuoco")
cv2.setMouseCallback("Rilevamento Fuoco", mouse_callback)

while True:
    ret, frame = cap.read()
    
    if not ret:
        break

    # Controllo automatico tramite rilevamento YOLO
    if not manual_mode:
        results = model(frame)
        
        fire_detected = False
        for result in results:
            boxes = result.boxes
            
            if len(boxes) > 0:
                print("Fuoco rilevato!")
                for box in boxes:
                    # Calcola la distanza e la posizione (esempio: centro del box)
                    box_data = box.xywh.cpu().numpy()[0]  # Ottieni le coordinate xywh come numpy array
                    distanza = box_data[2]  # La larghezza del box come esempio di distanza
                    fire_position = (box_data[0], box_data[1])  # Posizione x, y del centro del box
                    fire_detected = True

                    # Invia i dati all'ESP32
                    invia_dati_esp32(distanza, fire_position)
                    
            else: 
                ...   

        annotated_frame = results[0].plot()
        
     # Controllo manuale tramite mouse
    else:
        print(f"Controllo manuale attivo - Posizione: {mouse_position}")
        invia_dati_esp32(0, mouse_position)  # Invia la posizione del fuoco all'ESP32
        annotated_frame = frame

    cv2.imshow("Rilevamento Fuoco", annotated_frame)
    
    # Esci con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    if cv2.getWindowProperty("Rilevamento Fuoco", cv2.WND_PROP_VISIBLE) < 1:
        break
    
cap.release()
cv2.destroyAllWindows()
