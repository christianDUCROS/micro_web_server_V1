######################################
#serveur web avec variables dynamiques issues de données de capteurs
# toutes les infos sur youtube  christian ducros
#mail christian.ducros@laposte.net
######################################

#version définitive
import network
import socket
import time
#parametre du serveur
import parametre  
repertoire = parametre.repertoire
index_page=parametre.index_page
ssid=parametre.ssid
password=parametre.password

#module de changements dynamiques des variables 
import mdvd 

#led allumée durant les échanges client-serveur
from machine import Pin
Led_builtin = Pin('LED', Pin.OUT)
Led_builtin.off()

def connexion_wifi_STA(pssid,ppassword) : # Connexion wifi mode STATION
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(pssid, ppassword)

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )
        Led_builtin.on()
        time.sleep(3)
        Led_builtin.off()

def connexion_wifi_AP(pssid,ppassword): #Connexion wifi mode ACCESS POINT
    wlan = network.WLAN(network.AP_IF)
    wlan.config(essid= pssid , password = ppassword)
    wlan.active(True)
    wlan.config(pm = 0xa11140) #augmente la réactivité
    while wlan.active == False :
        pass
    print("Access point actif")
    print(wlan.ifconfig())
    print('Réseau wifi : PicoW et mot de passe : 123456789')
    Led_builtin.on()
    time.sleep(3)
    Led_builtin.off()

def construction_dico_dynamiques(dico): #construction du dico_valeurs_dynamiques à partir de dico.txt
    with open(repertoire + 'dico.txt', 'r') as file:   
        ligne = file.readline()
        while ligne != "":
            ligne_split = ligne.split(':')
            dico[ligne_split[0]] = ligne_split[1][:-2]
            ligne = file.readline()
    return(dico)

def insertion_valeurs_dynamiques (fichier_lu) :
    debut_recherche = 0
    while True :
        # recherche du premier {{
        start = fichier_lu.find(b"{{", debut_recherche)
        if start ==-1 :
            break
        end = fichier_lu.find(b"}}", start)
        nom_variable = fichier_lu[start + 2:end].strip()
        nom_variable_str = nom_variable.decode()
        valeur_nom_variable = dico_valeurs_dynamiques.get(nom_variable_str)
        if valeur_nom_variable != None :
            fichier_lu = fichier_lu[0:start]+ valeur_nom_variable + fichier_lu[end+2::]   
        #recherche de la prochaine insertion capteur 
        debut_recherche = end + 2
    return fichier_lu


def get_request_file(request_file_name):
    #page index par défaut
    if request_file_name == '/' :  
        request_file_name = index_page
    with open(repertoire + request_file_name, 'rb') as file:   #byte
        file_requested= file.read()
    file_requested = insertion_valeurs_dynamiques(file_requested)  # commenter alors tailles des images plus grandes mais pas d'insertion dynamique de données
    return file_requested   

#debut programme principal
#connexion wifi
if parametre.mode_wifi== 'AP' : 
    connexion_wifi_AP(ssid,password)
elif parametre.mode_wifi== 'STA' :
    connexion_wifi_STA(ssid,password)

#Construction dico_valeurs_dynamiques à partir du fichier dico.txt
dico_valeurs_dynamiques = {} 
dico_valeurs_dynamiques = construction_dico_dynamiques(dico_valeurs_dynamiques)

# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(5)
print('listening on', addr) # Listen for connections

while True:
    #Mise à jour donnéees dynamiques : Capteurs....
    dico_valeurs_dynamiques= mdvd.modifications_dico_valeurs_dynamiques(dico_valeurs_dynamiques)
    try:
        cl, addr = s.accept()
        #Allume LED pour indiquer un client connecté 
        Led_builtin.on()
        #reception de la demande
        request = cl.recv(1024)
        #turns the request into a string
        request = str(request)        
        #recherche des données demandées
        request = request.split()[1]
        if '.html' in request:
            file_header = 'HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n'
        elif '.css' in request:
            file_header = 'HTTP/1.1 200 OK\r\nContent-type: text/css\r\n\r\n'
        elif '.js' in request:
            file_header = 'HTTP/1.1 200 OK\r\nContent-type: text/javascript\r\n\r\n'
        elif '.svg' in request:
            file_header = 'HTTP/1.1 200 OK\r\nContent-type: image/svg+xml\r\n\r\n'
        elif '.json' in request:
            file_header = 'HTTP/1.1 200 OK\r\nContent-type: application/json\r\n\r\n'  #json
        elif '.svgz' in request:
            file_header = 'HTTP/1.1 200 OK\r\nContent-type: image/svg+xml\r\n\r\n'
        elif '.png' in request:
            file_header = 'HTTP/1.1 200 OK\r\nContent-type: image/png\r\n\r\n'
        elif '.ico' in request:
            file_header = 'HTTP/1.1 200 OK\r\nContent-type: image/x-icon\r\n\r\n'
        elif '.jpg' in request:
            file_header = 'HTTP/1.1 200 OK\r\nContent-type: image/jpg\r\n\r\n'
        elif '.webp' in request:
            file_header = 'HTTP/1.1 200 OK\r\nContent-type: image/webp\r\n\r\n'   #webp
        # serve index if you don't know
        else:
            # doesnt send a header type if not extension not listed. In many cases the file will still load - but you may be better to look up the MIME type for the file and add to the above list
            file_header = ''
        #lecture du ficher demandé + insertion data 
        response = get_request_file(request)
        #envoie file header
        cl.send(file_header)
        #envoie réponse
        cl.sendall(response)
        cl.close()
        #eteindre la led  : fin de la communication
        Led_builtin.off()
        
    except :
        cl.close()
        Led_builtin.off()
        print('pas de connexion')
    time.sleep(0.1)    
        