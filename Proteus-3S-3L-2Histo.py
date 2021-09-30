import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO
import spidev
from datetime import datetime

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(17, GPIO.IN)

# Abre el bus para la comunicacion SPI
spi=spidev.SpiDev()
spi.open (0,0)

# Definicion del canal para el sensor
ch0 = 0
ch1 = 1

#leer los datos del chip MCP3008
def ReadChannel(channel):
   adc=spi.xfer2([1,(8+channel)<<4,0])
   data=((adc[1]&3)<<8)+adc[2]
   return data #retorna datos de 0 a 1024

#funcion para calcular la temperatura esta funcion acondiciona la informacion a escala de temperatura 
def ConvertTemp(data,places):
   temp = ((data*330)/float(1023))
   temp = round(temp,places)
   return temp # retorna valores de 0 a 330 grados 

#funcion para almacenamiento de datos
def seveData1():
	senT=str(datetime.now())
	sen_1=str(ConvertTemp(ReadChannel(ch0),3))
	sen_2=str(ConvertTemp(ReadChannel(ch1),3))
	file1= open("Dato1.txt","a")
	file1.write("Valor del sensor 1= "+sen_1+" : "+senT+"<br>"+"\n")
	file1.close()

	file2= open("Dato2.txt","a")
	file2.write("Valor del sensor 2= "+sen_2+" : "+senT+"<br>"+"\n")
	file2.close()

#funcion para asignar el historial 1 a una variable.
def hist1():
	file1=open("Dato1.txt","r")
	pos=file1.seek(0,0)
	Rfile1=file1.read()
	file1.close()
	return Rfile1

#funcion para asignar el historial 2 a una variable.
def hist2():
	file2=open("Dato2.txt","r")
	pos=file2.seek(0,0)
	Rfile2=file2.read()
	file2.close()
	return Rfile2

#funcion para enviar de cada sensor
def setData():
	sen_1=str(ConvertTemp(ReadChannel(ch0),3))
	sen_2=str(ConvertTemp(ReadChannel(ch1),3))
	vector=(sen_1+";"+sen_2)
	mqttc.publish("kbtz14k@gmail.com/test", vector) 
	
#funcion para enviar el historial1
def setData1():
	sen_1=str(ConvertTemp(ReadChannel(ch0),3))
	sen_2=str(ConvertTemp(ReadChannel(ch1),3))
	envRfile1=hist1()
	vector=(sen_1+";"+sen_2+";"+envRfile1)
	mqttc.publish("kbtz14k@gmail.com/test", vector) 
	print(vector)
#funcion para enviar el historial2
def setData2():
	sen_1=str(ConvertTemp(ReadChannel(ch0),3))
	sen_2=str(ConvertTemp(ReadChannel(ch1),3))
	envRfile2=hist2()
	vector=(sen_1+";"+sen_2+";"+"p"+";"+envRfile2)
	mqttc.publish("kbtz14k@gmail.com/test", vector) 

#funcion para recivir comando desde la web
def on_message(client, obj, msg):    
	#print(str(msg.topic)+" "+str(msg.qos)+" "+str(msg.payload))
	datoWeb=msg.payload.decode('utf-8')
	print(datoWeb) 
	s1='hist1'
	s2='hist2'
	
	if (datoWeb==s1):
	 setData1()
	elif (datoWeb==s2):
	 setData2()


mqttc = mqtt.Client() 
mqttc.on_message = on_message 
mqttc.username_pw_set("kbtz14k@gmail.com","playboy1995") 
mqttc.connect("maqiatto.com", 1883) 
mqttc.subscribe("kbtz14k@gmail.com/test1", 0) 
rc=0
file1= open("Dato1.txt","w")
file1.write("\n")
file1.close()

file2= open("Dato2.txt","w")
file2.write("\n")
file2.close()


print("inicio...")
   
# Define los tiepos para cada lectura de los datos 
while rc ==0:
	rc=mqttc.loop()
	time.sleep(1)
	hist1()
	hist2()
	seveData1()
	time.sleep(2)
	setData()
	
