import asyncio
import time
import random
import connection_handler as connection_handler_
from gpiozero import LED, InputDevice, LEDBoard, PWMLED
from random import randint
import socket

client_handler = connection_handler_.connection_handler()
Gameresults = { } #dictionary med steg pasient (dic)- sokkel (dic)- typedata (dic)- liste
latest_reading = []
#NB SENDER TIL PORT 8003 RECIEVER PÅ 8004

async def getGamestate(socketServer):
    #henter data fra backend
    #formater data riktig
    #hvis data ikke blir hentet return 
    address = ('127.0.0.1', 8004)
    socketServer.bind(address)
    message = "b"
    # Receive the client packet along with the address it is coming from
    try: 
        message, address = socketServer.recvfrom(1024)
    except:
        print("Game didnt start")
        socketServer.close()
        return 0
    finally:

        # Capitalize the message from the client
        message = message.lower()
        Game_start, pasient = message.split(' ', 1)

        #format: message = "1 pasient 1"
        #eller: message = "0 whaterver (denne dataen brukes ikke)"
        socketServer.close()
        return Game_start, pasient

async def waitForGamestart(UDPserver):
    global client_handler
    #En status hvor den har initiert og venter på å starte spillet
    pasient = ""
    #Game_start, pasient = getGamestate(socketServer)
    Game_start = int(input("trykk 1 for å starte et game "))
    for sokkel in sokkel_Id_list:
        if (await client_handler.get_connected(str(sokkel)) == False):
            print("Lost communication with sokkel with id " + str(sokkel))
        await asyncio.sleep(0.5)
    sokkel_Id_list = await client_handler.get_IDs()
    return Game_start, pasient


 
    #jeg forestiller meg at programmet kjører parallelt med back end og annet, men #har ikke jobbet så mye med det før, antar at sleep ikke egt trengs men ønsker #raspberry setter av tid til at andre programmer skal kunne gjøres. 

async def sendLastReading(socketServer, temp_dic):

    address = ('127.0.0.1', 8003)
    socketServer.bind(address)
    Reading = (str(temp_dic["gyro_x"]), str(temp_dic["gyro_y"], str(temp_dic["gyro_z"])), str(temp_dic["accel_x"]), str(temp_dic["accel_y"]), str(temp_dic["accel_z"]), str(temp_dic["timestamp"]))
    
    socketServer.sendto(Reading, address) 
    socketServer.close()

async def saveGame(socketServer):
    global Gameresults

    #åpner fil og json dumper i filen


    #sender game ended
    address = ('127.0.0.1', 8004)
    socketServer.bind(address)
    Reading = "Game_start 0"
    
    socketServer.sendto(Reading, address) 
    socketServer.close()
    #filbehandlingsshit

async def Gameloop(socketServer, sokkel_Id_list, Game_start1, pasient, Hall_effekt=0, Led_lys=0):
    global client_handler
    global Gameresults

    Gameresults[pasient] = {}
    Score = 0
    Game_start = Game_start1

    Data = list()
    Gyro = list(list())
    Akselerasjon = list(list())
    time = 0
    Time = list()

    RandomHull = 0
    RandomHull_list = list()

    for sokkel in sokkel_Id_list:


        Gameresults[pasient][sokkel] = {}
        RandomHull = randint(0, len(Hall_effekt))
        #Led_lys[RandomHull].on()
        await client_handler.send_to_client(str(sokkel), "set_gameplay_state active")
        await client_handler.reset_client_data(str(sokkel))


        #while Hall_effekt[RandomHull].value == 0:
        for i in range(100): #kjører denne siden vi ikke er i raspberry pi.
            for i in range(15): #Looper her fordi jeg er mer interresert i dataen enn de andre sjekkene i loopen.
                await asyncio.sleep(0.125) #en arbitrary sleep som skal tillate serveren å ta inn data. 
                temp_dic = await client_handler.get_last_reading(str(sokkel))
                sendLastReading(socketServer, temp_dic)
                Akselerasjon.append([temp_dic["accel_x"], temp_dic["accel_y"], temp_dic["accel_z"]])
                Gyro.append([temp_dic["gyro_x"], temp_dic["gyro_y"], temp_dic["gyro_z"]])
                Time.append(temp_dic["timestamp"])
                print("Gamemaster Tilt: ", Gyro, "   Akselerasjon: ", Akselerasjon, "   Time: ", Time)
                #send data to backend
            Game_start, pasient = getGamestate(socketServer)
            if Game_start == 0:
                print("Game cancelled")
                Gameresults[pasient][sokkel].append(client_handler.collectFullData(str(sokkel)))
                print("collected data from sokkel run")
                return 0
            if (await client_handler.get_connected(str(sokkel)) == False):
                print("lost sokkel connection")
        #Led_lys[RandomHull].off()
        
        Gameresults[pasient][sokkel].append(client_handler.collectFullData(str(sokkel)))
        print("collected data from sokkel run")

    #sendToBackend("Game finished", Gameresults)
    Game_start = 0

    #kanskje Game_start skal være lik 2 slik at backend får en oppgavekode

    return 0

async def GameMaster2():


    server_ip = "127.0.0.1"
    port = 8003

    socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketServer.settimeout(1)


    print("started gamemaster")


    #Initialiser Hall_effekt
    '''
    HE1 = InputDevice(4)
    HE2 = InputDevice(17)
    HE3 = InputDevice(18)
    HE4 = InputDevice(27)
    HE5 = InputDevice(22)
    HE6 = InputDevice(23)
    HE7 = InputDevice(24)
    HE8 = InputDevice(25)
    HE9 = InputDevice(5)
    HE10 = InputDevice(6)
    HE11= InputDevice(12)
    HE12 = InputDevice(13)



    #liste over alle initialiserte hall effekt
    Hall_effekt = [HE1, HE2, HE3, HE4, HE5, HE6, HE7, HE8, HE9, HE10, HE11, HE12]


    #Initialiser LED
    
    LED1 = LED(1)
    LED2 = LED(2)
    LED3 = LED(1)
    LED4 = LED(2)
    LED5 = LED(1)
    LED6 = LED(2)
    LED7 = LED(1)
    LED8 = LED(2)
    LED9 = LED(1)
    LED10 = LED(2)
    LED11 = LED(1)
    LED12 = LED(2)
    
    #LEDn = LED(#tallet inni her refererer til GPIO nummer, den er ikke det samme som LED nummer pre se)


    #liste over alle initialiserte LED
    #Led_lys og Hall_effekt burde ha samme lengde ettersom en realisert Hall_effekt burde medføre en realisert LED (mulig dette må endres senere)

    Led_lys = [LED1, LED2, LED3,LED4, LED5,LED6,LED7,LED8,LED9,LED10,LED11,LED12]
    '''

    #en liste med alle sokkelene som er koblet til
    sokkel_Id_list = list()

    JobDone = False




    while len(sokkel_Id_list) == 0:
        sokkel_Id_list = await client_handler.get_IDs()
        await asyncio.sleep(2)
    

    #Først må kommunikasjon etableres mellom sokkelene og Game master slik at begge er klar over hverandr

    #neste er en variabel for gamestart og en variabel som tracker hvilken sokkel vi er på (0 betyr sokkel(id1), 1 betyr …, LED12)

    Game_start = 0
    pasient = ""

    #Initialisering ferdig
    #----------------------

    while True:
        if Game_start == 0:
            socketServer.settimeout(1)
            Game_start, pasient = waitForGamestart()
        else:
            socketServer.settimeout(0)
            Gameloop(socketServer, sokkel_Id_list, Game_start, pasient)
            saveGame(socketServer)



asyncio.run(GameMaster2())


    

async def game_master(pasient):

    server_ip = "127.0.0.1"
    port = 8003

    sockServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockServer.bind((server_ip, port))

    sockServer.listen(0)
    print(f"Listening on {server_ip}:{port}")

    client_socket, client_address = sockServer.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")


    Gameresults[pasient] = {}
    print("started gamemaster")


    #Initialiser Hall_effekt
    '''
    HE1 = InputDevice(4)
    HE2 = InputDevice(17)
    HE3 = InputDevice(18)
    HE4 = InputDevice(27)
    HE5 = InputDevice(22)
    HE6 = InputDevice(23)
    HE7 = InputDevice(24)
    HE8 = InputDevice(25)
    HE9 = InputDevice(5)
    HE10 = InputDevice(6)
    HE11= InputDevice(12)
    HE12 = InputDevice(13)



    #liste over alle initialiserte hall effekt
    Hall_effekt = [HE1, HE2, HE3, HE4, HE5, HE6, HE7, HE8, HE9, HE10, HE11, HE12]


    #Initialiser LED
    
    LED1 = LED(1)
    LED2 = LED(2)
    LED3 = LED(1)
    LED4 = LED(2)
    LED5 = LED(1)
    LED6 = LED(2)
    LED7 = LED(1)
    LED8 = LED(2)
    LED9 = LED(1)
    LED10 = LED(2)
    LED11 = LED(1)
    LED12 = LED(2)
    
    #LEDn = LED(#tallet inni her refererer til GPIO nummer, den er ikke det samme som LED nummer pre se)


    #liste over alle initialiserte LED
    #Led_lys og Hall_effekt burde ha samme lengde ettersom en realisert Hall_effekt burde medføre en realisert LED (mulig dette må endres senere)

    Led_lys = [LED1, LED2, LED3,LED4, LED5,LED6,LED7,LED8,LED9,LED10,LED11,LED12]
    '''
    Score = 0

    #en liste med alle sokkelene som er koblet til
    sokkel_Id_list = list()

    JobDone = False




    while len(sokkel_Id_list) == 0:
        sokkel_Id_list = await connection_handler.get_IDs()
        await asyncio.sleep(2)
    

    #Først må kommunikasjon etableres mellom sokkelene og Game master slik at begge er klar over hverandr

    #neste er en variabel for gamestart og en variabel som tracker hvilken sokkel vi er på (0 betyr sokkel(id1), 1 betyr …, LED12)

    Game_start = 0
    Sokkel = 0

    #til slutt trenger vi variabler som jobber med akselerasjon og tilt og tid

    Data = list()
    Gyro = list(list())
    Akselerasjon = list(list())
    time = 0
    Time = list()


    RandomHull = 0

    while True:
        #En status hvor den har initiert og venter på å starte spillet
        
        #Game_start = getBackEnd()
        Game_start = int(input("trykk 1 for å starte et game "))
        for sokkel in sokkel_Id_list:
            if (await connection_handler.get_connected(str(sokkel)) == False):
                print("Lost communication with sokkel with id " + str(sokkel))
            await asyncio.sleep(0.5)
        sokkel_Id_list = await connection_handler.get_IDs()
            
    #jeg forestiller meg at programmet kjører parallelt med back end og annet, men #har ikke jobbet så mye med det før, antar at sleep ikke egt trengs men ønsker #raspberry setter av tid til at andre programmer skal kunne gjøres. 




        while (Game_start == 1):
    #når spillet starter aktiveres en sokkel, en halleffekt og et LED lyst. #Aktivering av sokkelen betyr at den må requeste send data

            for sokkel in sokkel_Id_list:
                Gameresults[pasient][sokkel] = {}
                #RandomHull = randint(0, len(Hall_effekt))
                #Led_lys[RandomHull].on()
                await connection_handler.send_to_client(str(sokkel), "set_gameplay_state active")
                await connection_handler.reset_client_data(str(sokkel))
                #while Hall_effekt[RandomHull].value == 0:
                for i in range(100):
                    for i in range(10): #Looper her fordi jeg er mer interresert i dataen enn de andre sjekkene i loopen.
                        await asyncio.sleep(0.125)
                        temp_dic = await connection_handler.get_last_reading(str(sokkel))
                        Akselerasjon.append([temp_dic["accel_x"], temp_dic["accel_y"], temp_dic["accel_z"]])
                        Gyro.append([temp_dic["gyro_x"], temp_dic["gyro_y"], temp_dic["gyro_z"]])
                        Time.append(temp_dic["timestamp"])
                        print("Gamemaster Tilt: ", Gyro, "   Akselerasjon: ", Akselerasjon, "   Time: ", Time)
                        #send data to backend
                    #Game_start = getBackEnd()
                    if Game_start == 0:
                        print("Game cancelled")
                        break
                    if (await connection_handler.get_connected(str(sokkel)) == False):
                        print("lost sokkel connection")
                #Led_lys[RandomHull].off()
                
                Gameresults[pasient][sokkel].append(connection_handler.collectFullData(str(sokkel)))
                print("collected data from sokkel run")
                if Game_start == 0:
                    break
            if Game_start == 0:
                print("Going back to true loop in Gamemaster")
                break
            #sendToBackend("Game finished", Gameresults)
            Game_start = 0

            #kanskje Game_start skal være lik 2 slik at backend får en oppgavekode

    return 0