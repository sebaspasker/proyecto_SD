import socket
import sys



########## MAIN ##########
if  (len(sys.argv) == 1):
    IP = '127.0.0.6' #puerto de escucha
    MAXJUGADORES = 3
    PUERTO_WEATHER = 8080
    ADDR = (IP, PUERTO_WEATHER)
    
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR) # nada mas conectarse con el servidor de clima este hace la select de las 4 ciudades
    print (f"Establecida conexión en [{ADDR}]")

    

            
    client.close()
else:
    print ("Oops!. Parece que algo falló. Necesito estos argumentos: <Puerto de escucha> <Número máximo de jugadores> <Puerto AA_Weather>")