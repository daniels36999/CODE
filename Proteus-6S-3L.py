import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import spidev
import time
from datetime import datetime

GPIO.setmode(GPIO.BOARD)
GPIO.setup(29, GPIO.IN)
GPIO.setup(31, GPIO.IN)
GPIO.setup(32, GPIO.IN)
GPIO.setup(7,GPIO.OUT)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(12,GPIO.OUT)
#---------------------------------------------------------------
estadoA1='Alta'
estadoB1='Baja'
estadoA2='Lejos'
estadoB2='Cerca'
estadoA3='Lleno'
estadoB3='Vacio'

spi=spidev.SpiDev()
spi.open(0,0)
N_Canal=0
N_Canal2=1
N_Canal3=2

def ReadChannel(channel):
	adc=spi.xfer2([1,(8+channel)<<4,0])
	data=((adc[1]&3)<<8)+adc[2]
	return data


def ConvertTemp(data,places):
	temp=((data*330)/float(1023))
	temp=round(temp,places)
	return temp



#---------------------------------------------------------------
def Sensor1():
    if GPIO.input(29):
        DatoS1=estadoA1
        return DatoS1
    else:
        DatoS1=estadoB1
        return DatoS1

def Sensor2():
    if GPIO.input(31):
        DatoS1=estadoB2
        return DatoS1
    else:
        DatoS1=estadoA2
        return DatoS1

def Sensor3():
    if GPIO.input(32):
        DatoS1=estadoB3
        return DatoS1
    else:
        DatoS1=estadoA3
        return DatoS1
#-------------------------------------------------------------   
def Almacenar():     

        AlmacenaS0=str(datetime.now())
        AlmacenaS1=str(i)
        AlmacenaS2=Sensor2()
        AlmacenaS3=Sensor3()
        AlmacenaS4=str(ConvertTemp(ReadChannel(N_Canal),2))
        AlmacenaS5=str(ConvertTemp(ReadChannel(N_Canal2),2))
        AlmacenaS6=str(ReadChannel(N_Canal3))

        base=open("Sensores.txt","a")
        base.write(AlmacenaS0+" S1="+AlmacenaS1+" S2="+AlmacenaS2+" S3="+AlmacenaS3+" S4="+AlmacenaS4+" S5="+AlmacenaS5+" S6="+AlmacenaS6+"  <br>"+"\n")
        base.close() 
#------------------------------------------------------------
def Mostrar(): 
        base=open("Sensores.txt","r")
        position = base.seek(0, 0);
        valores=base.read()
        base.close()
        return valores      
        #mqttc.publish("dyautibug.fie@unach.edu.ec/test1",valores ) 
#--------------------------------------------------------------
def Enviar1():
    Vector=(str(i)+";"+Sensor2()+";"+Sensor3())
    mqttc.publish("dyautibug.fie@unach.edu.ec/test",Vector) 

def Enviar2():
    Vector=(str(i)+";"+Sensor2()+";"+Sensor3()+";"+Mostrar())
    mqttc.publish("dyautibug.fie@unach.edu.ec/test",Vector) 

#--------------------------------------------------------------
def on_message(client,obj,msg):
    valor=(msg.payload.decode("utf-8"))
    print(valor)

    if(valor=='LED1_ON'):
        GPIO.output(7,True)
    elif(valor=='LED1_OFF'):
        GPIO.output(7,False)
    elif(valor=='LED2_ON'):
        GPIO.output(11,True)
    elif(valor=='LED2_OFF'):
        GPIO.output(11,False)
    elif(valor=='LED3_ON'):
        GPIO.output(12,True)
    elif(valor=='MOSTRAR_HISTORIAL'):
        Enviar2()


#------------------------------------------------------------------------------------------------
mqttc=mqtt.Client()
mqttc.on_message = on_message
mqttc.username_pw_set("dyautibug.fie@unach.edu.ec","daniels")
mqttc.connect("maqiatto.com", 1883)
mqttc.subscribe("dyautibug.fie@unach.edu.ec/test1", 0)
#--------------------------------------------------------------------------------------------------
base=open("Sensores.txt","w")
base.write("\n")
base.close() 

var=0
Vector=''
rc=0
i=0
a=5
print("inicio...")
while rc==0:
    #temp_level=ReadChannel(N_Canal)
    #temp_level2=ReadChannel(N_Canal2)
    #temp_level3=ReadChannel(N_Canal3)

    #temp=ConvertTemp(temp_level,2)
    #temp2=ConvertTemp(temp_level2,2)
    #temp3= temp_level3
    #print(str(temp))
    #print(str(temp2))
    #print(str(temp3))

    rc=mqttc.loop()
    time.sleep(1)
    Almacenar()
    time.sleep(0.5)
    Enviar1()
    if(Sensor1()=='Baja'):
        i=i+1
    else:
        i=i