import torch
from ultralytics import YOLO
import cv2
import requests
import os
from pathlib import Path
import serial
import sys
import time

GITHUB_REPO = "AlessandroBone1/MT_MK.2"
MODEL_FILENAME = "best2.pt"
MODEL_PATH = Path(MODEL_FILENAME)
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/commits?path={MODEL_FILENAME}"

esp32 = serial.Serial('COM7', 9600)  
time.sleep(.1)
ex_posizione = []


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
    #distanza : 0-120 altezza - lunghezza  
    #messaggio = f":{distanza} Posizione:{posizione[0]},{posizione[1]}\n"
    messaggio = ""
    
    global ex_posizione
    if ex_posizione == []:
        ex_posizione = posizione
    else:

        boolX = False
        boolY = False
        

        #funzione per ruotare solo z grad_sinistra = gradi_destra
        #funzione per ruotare solo x gradi_sinistra = -gradi_destra + 180

        dX = posizione[0] - ex_posizione[0]
        dY = posizione[1] - ex_posizione[1]
        half = cap.get(4)/2
        #elimino un 5% di possibile errore
        # print(f"exposizione {ex_posizione[0]} - {ex_posizione[1]}")
        # print(f"posizione {posizione[0]} - {posizione[1]}")
        if ((posizione[0] < (ex_posizione[0]- (ex_posizione[0]/100)*2) or posizione[0] > (ex_posizione[0]+ (ex_posizione[0]/100)*2)) and posizione[0] != ex_posizione[0]):
            print("movimento lungo")
            calcoloZ = posizione[0]/3.5
            messaggio = f"z{calcoloZ}"
            
            esp32.write(messaggio.encode("utf-8"))
            esp32.flush()
            print(messaggio)

        if ((posizione[1] < (ex_posizione[1]- (ex_posizione[1]/100)*2) or posizione[1] > (ex_posizione[1]+ (ex_posizione[1]/100)*2)) and posizione[1] != ex_posizione[1]):

                calcoloZ = posizione[0]/3.5
                
                calcoloS = calcoloZ + 30 - (posizione[1])/8
            
                calcoloD = calcoloZ + (posizione[1]-half)/8

                if posizione[1] > half:
                    messaggio = f"d{calcoloD}"  
                    calcoloS = calcoloZ - (posizione[1]-half)*1/8 
                else:
                    messaggio = f"s{calcoloS}"

                time.sleep(2)
                esp32.write(messaggio.encode("utf-8"))
                esp32.flush()
                print(messaggio)

                if posizione[1] > half:
                    messaggio = f"s{calcoloS}"  
          
                else:
                    messaggio = f"d{calcoloD}"

                time.sleep(2)
                esp32.write(messaggio.encode("utf-8"))
                esp32.flush()
                print(messaggio)


                ex_posizione = posizione


    #messaggio = "s" + n per N:{n<180, n>0}

    #--condizione-- alto e destra

    #messaggio = "d" + n per N:{n<180, n>0}
        
    

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

model = YOLO(str(MODEL_PATH), verbose=False)
cap = cv2.VideoCapture(0)

cv2.namedWindow("Rilevamento Fuoco")
cv2.setMouseCallback("Rilevamento Fuoco", mouse_callback)

#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   Imposta la larghezza del frame
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  Imposta l'altezza del frame
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
        time.sleep(1)
        annotated_frame = frame

    cv2.imshow("Rilevamento Fuoco", annotated_frame)
    
    # Esci con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    if cv2.getWindowProperty("Rilevamento Fuoco", cv2.WND_PROP_VISIBLE) < 1:
        break
    
cap.release()
cv2.destroyAllWindows()
