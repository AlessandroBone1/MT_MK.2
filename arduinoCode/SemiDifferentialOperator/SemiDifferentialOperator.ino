#include <Servo.h>

//initialating the servos

Servo servodx;
Servo servosx;

int degdx = 90;
int degsx = 90;

byte incomingByte;

String x; 
void setup() {
  //attaching the servos
  servodx.attach(5);
  servosx.attach(7);
  
  //starting deg
  servodx.write(degdx);
  servosx.write(degsx);
  Serial.begin(9600); 
} 


void loop() { 
  //does nothing while waiting for available serial
  while (!Serial.available()); 

  //reads some Serial
  x = Serial.readString();

  Serial.print("ho ricevuto: ");
  Serial.println(x);

  switch(x[0]){

  //se la stringa inizia con x, roterà lungo quell'asse
  case 'x':{
    
    //normalmente la posizione di partenza si trova a 180°, dandoci la possibilità di andare - in senso orario - a 360° o - in senso antiorario - a 0°
    Serial.println("--------x--------");
    int degrs = x.substring(1).toInt();
    int toSX;
    int toDX;
    
    //lungo l'asse x è possibile roteare lungo tutti e 360°, modificando il motore che subirà la sottrazione dei gradi, andando così in senso orario o antiorario
    Serial.println("Gradi da raggiungere: ");
    toSX = 180-(degrs/2);
    toDX = degrs/2;
    Serial.print("To Sx: ");
    Serial.println(toSX);

    Serial.print("To Dx: ");
    Serial.println(toDX);
  

    Serial.print("Gradi precedentemente segnalati: sx- ");
    Serial.print(degsx);
    Serial.print(" dx-");
    Serial.println(degdx);

    while(degsx != toSX && degdx != toDX){
      servosx.write(degsx);
      servodx.write(degdx);
      if(degsx> toSX)
          degsx--;
      else
          degsx++;
      
      if(degdx<toDX)
          degdx++;
      else
          degdx--;
    //delay(13);
  }

    Serial.print("Gradi ora segnalati: sx- ");
    Serial.print(degsx);
    Serial.print(" dx-");
    Serial.println(degdx);
      break;
  }
  

  //se il messaggio inizia con z, svolgerà una rotazione sull'asse omonimo
  case 'z':{

    int degrs = x.substring(1).toInt();
    Serial.println("--------z--------");
    Serial.print("Gradi da raggiungere: ");
    Serial.println(degrs);
    Serial.print("Gradi ora segnalati: sx- ");
    Serial.print(degsx);
    Serial.print(" dx-");
    Serial.println(degdx);

    while(degsx != degrs && degdx != degrs){
      servosx.write(degsx);
      servodx.write(degdx);
      //se i gradi del motore di destra e sinistra sono maggiori del necessario li diminuirà fino a risoluzione della condizione del while, altrimenti li aumenterà
      if(degsx> degrs)
          degsx--;
      else
          degsx++;
      
      if(degdx<degrs)
          degdx++;
      else
          degdx--;
      //delay(13);
    }
    break;
  }


  //se il messaggio inizia con d, svolegerà una rotazione sull'asse x utlizzando solo il motore destro, effettuando una torsione
  case 'd':{
    Serial.println("--------d--------");
    int degrs = x.substring(1).toInt();
    
    Serial.print("Gradi da raggiungere: ");
    Serial.println(degrs);
    Serial.print("Gradi ora segnalati: ");
    Serial.println(degdx);

    while( degdx != degrs){
      servodx.write(degdx);
      if(degdx<degrs)
          degdx++;
      else
          degdx--;
      //delay(13);
    }
    break;
  }

  case 's':{
    Serial.println("--------s--------");
    int degrs = x.substring(1).toInt();
    
    Serial.print("Gradi da raggiungere: ");
    Serial.println(degrs);
    Serial.print("Gradi ora segnalati: ");
    Serial.println(degsx);

    while( degsx != degrs){
      servosx.write(degsx);
      if(degsx<degrs)
          degsx++;
      else
          degsx--;
      //delay(13);
    }
    break;
  }
  case 't':
   Serial.print("Gradi ora segnalati: sx- ");
    Serial.print(degsx);
    Serial.print(" dx-");
    Serial.println(degdx);
    break;


  default:
  degsx = 90;
  degdx = 90;
  
  servodx.write(degdx);
  servosx.write(degsx);
    break;
  }
  }

/*

      if(Serial.available()>0){
    incomingByte = Serial.read();
    Serial.println(incomingByte);
    
  if(incomingByte == 49){
        for(int i = 0; i< 90; i+= 1){
            servodx.write(90-i);
            servosx.write(90-i);
         
        }
      }
      if(incomingByte == 50){
        for(int i = 0; i< 90; i+= 1){
            servodx.write(90+i);
            servosx.write(90+i);
        }
      }

        if(incomingByte == 51){
          for(int i = 0; i< 90; i+= 1){
              servosx.write(90+i);
              servodx.write(90-i);
          }
        }
        if(incomingByte == 52){
        for(int i = 0; i< 90; i+= 1){
            servosx.write(90+i);
        }
        }
        if(incomingByte == 53){
        for(int i = 0; i< 90; i+= 1){
            servosx.write(90-i);
        }
        }
        if(incomingByte == 54){
        for(int i = 0; i< 90; i+= 1){
            servodx.write(90+i);
        }
        }
        if(incomingByte == 55){
        for(int i = 0; i< 90; i+= 1){
            servodx.write(90-i);
        }
        }
        }

      
*/

/*//does nothing while waiting for available serial
  while (!Serial.available()); 

  //reads some Serial
  x = Serial.readString();

  Serial.print("ho ricevuto: ");
  Serial.println(x);
  
  if(x.startsWith("z")){
    int degrs = x.substring(1).toInt();

    Serial.println(degrs);

  }
  
  if(x.startsWith("x")){
    servosx.write(180);
    int degrs = x.substring(1).toInt();
    while(degsx == degrs && degdx == degrs){
      servosx.write(degsx);
      servodx.write(degdx);
      if(degsx> degrs)
          degsx--;
      else
          degsx++;
      
      if(degdx<degrs)
          degdx++;
      else
          degdx--;
      //delay(13);
    }
  }*/