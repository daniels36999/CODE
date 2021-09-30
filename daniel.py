import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import spidev
import time
from datetime import datetime

GPIO.setmode(GPIO.BOARD)
GPIO.setup(29, GPIO.IN)
#GPIO.setup(7, GPIO.OUT)

estadoA1='Baja'
estadoB1='Alta'

# Abre el bus para la comunicacion SPI
spi=spidev.SpiDev()
spi.open (0,0)

# Definicion del canal para el sensor
Canal0 = 0

# Pulsador
def Sensor1():
    if GPIO.input(29):
        DatoS1=estadoA1
        return DatoS1
    else:
        DatoS1=estadoB1
        return DatoS1

#leer los datos del chip MCP3008
def LeeCanal(channel):
   adc=spi.xfer2([1,(8+channel)<<4,0])
   data=((adc[1]&3)<<8)+adc[2]
   return data #retorna datos de 0 a 1024

#funcion para calcular la temperatura esta funcion acondiciona la informacion a escala de temperatura 
def ConvTemperatura(data,places):
   temp = ((data*330)/float(1023))
   temp = round(temp,places)
   return temp # retorna valores de 0 a 330 grados 

#funcion para almacenamiento de datos
def Almacenar():
	#print(time.ctime())
	#Hora=str(datetime.now())time.strftime("%H:%M:%S")
	Hora=str(time.strftime("%H:%M:%S"))
	sen_1=Sensor1()
	sen_2=str(ConvTemperatura(LeeCanal(Canal0),2))
	ArchS1= open("Historial1.txt","a")
	ArchS1.write("Sensor 1= "+sen_1+" : "+Hora+"<br>"+"\n")
	ArchS1.close()

	ArchS2= open("Historial2.txt","a")
	ArchS2.write("Sensor 2= "+sen_2+" : "+Hora+"<br>"+"\n")
	ArchS2.close()

#funcion para asignar el historial 1 a una variable.
def hist1():
	ArchS1=open("Historial1.txt","r")
	pos=ArchS1.seek(0,0)
	RArchS1=ArchS1.read()
	ArchS1.close()
	return RArchS1

#funcion para asignar el historial 2 a una variable.
def hist2():
	ArchS2=open("Historial2.txt","r")
	pos=ArchS2.seek(0,0)
	RArchS2=ArchS2.read()
	ArchS2.close()
	return RArchS2

#funcion para enviar de cada sensor
def EnvSensores():
	sen_1=Sensor1()
	sen_2=str(ConvTemperatura(LeeCanal(Canal0),3))
	#print(sen_1)
	#print(sen_2)
	vector=(sen_1+";"+sen_2)
	mqttc.publish("dyautibug.fie@unach.edu.ec/test", vector) 
	
#funcion para enviar el historial1
def EnvHist1():
	sen_1=Sensor1()
	sen_2=str(ConvTemperatura(LeeCanal(Canal0),3))
	envRArchS1=hist1()
	vector=(sen_1+";"+sen_2+";"+envRArchS1)
	mqttc.publish("dyautibug.fie@unach.edu.ec/test", vector) 
	print(vector)

#funcion para enviar el historial2
def EnvHist2():
	sen_1=Sensor1()
	sen_2=str(ConvTemperatura(LeeCanal(Canal0),3))
	envRArchS2=hist2()
	vector=(sen_1+";"+sen_2+";"+"---"+";"+envRArchS2)
	mqttc.publish("dyautibug.fie@unach.edu.ec/test", vector) 

#funcion para recivir comando desde la web
def on_message(client, obj, msg):    
	#print(str(msg.topic)+" "+str(msg.qos)+" "+str(msg.payload))
	datoWeb=msg.payload.decode('utf-8')
	print(datoWeb) 

	s1='HISTORIAL1'
	s2='HISTORIAL2'
	if (datoWeb==s1):
	 EnvHist1()
	elif (datoWeb==s2):
	 EnvHist2()


mqttc=mqtt.Client()
mqttc.on_message = on_message
mqttc.username_pw_set("dyautibug.fie@unach.edu.ec","daniels")
mqttc.connect("maqiatto.com", 1883)
mqttc.subscribe("dyautibug.fie@unach.edu.ec/test1", 0)

rc=0
ArchS1= open("Historial1.txt","w")
ArchS1.write("HISTORIAL DEL SENSOR 1"+"<br>"+"\n")
ArchS1.close()

ArchS2= open("Historial2.txt","w")
ArchS2.write("HISTORIAL DEL SENSOR 2"+"<br>"+"\n")
ArchS2.close()


print("inicio...")
   
# Define los tiepos para cada lectura de los datos 
while rc ==0:
	rc=mqttc.loop()
	Almacenar()
	EnvSensores()
	time.sleep(2)
