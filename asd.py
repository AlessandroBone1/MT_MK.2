import serial
esp32 = serial.Serial('COM7', 9600)  

while True:
    
    esp32.write(input("inserisci ").encode())
    print(esp32.readline())