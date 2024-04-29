import asyncio
import time
import random
import connection_handler as connection_handler_
from gpiozero import LED, InputDevice, LEDBoard, PWMLED
from random import randint
import socket
import json
import math


Gameresults = { } #dictionary med steg pasient (dic)- sokkel (dic)- typedata (dic)- liste


async def score(sokkel_Id_list):
    score = 0
    

    return 

async def saveFullreading(pasient, sokkel):
    global Gameresults

    readings = await client_handler.get_all_readings(str(sokkel))
    Gameresults[pasient][sokkel]["timestamp"] = readings["timestamp"]
    Gameresults[pasient][sokkel]["accel_x"] = readings["accel_x"]
    Gameresults[pasient][sokkel]["accel_y"] = readings["accel_y"]
    Gameresults[pasient][sokkel]["accel_z"] = readings["accel_z"]
    Gameresults[pasient][sokkel]["gyro_x"] = readings["gyro_x"]
    Gameresults[pasient][sokkel]["gyro_y"] = readings["gyro_y"]
    Gameresults[pasient][sokkel]["gyro_z"] = readings["gyro_z"]

async def calculate_averages(pasient, sokkel_Id_list):
    global Gameresults

    tilt_y_offset = -9200
    tilt_list = 0
    tid_list = 0
    accel_list = 0
    

    for sokkel in sokkel_Id_list:
        tilt_y = 0
        tid = 0
        accel_x = 0
        accel_y = 0
        accel_z = 0
        accel_average = 0

        for i in range(len(Gameresults[pasient][sokkel]["timestamp"])):
            tilt_y += abs(Gameresults[pasient][sokkel]["gyro_y"] - tilt_y_offset)
            accel_x = Gameresults[pasient][sokkel]["accel_x"]
            accel_y = Gameresults[pasient][sokkel]["accel_y"]
            accel_z = Gameresults[pasient][sokkel]["accel_z"]
            Accel += math.sqrt(accel_x**2+accel_y**2+accel_z**2)
        tid = Gameresults[pasient][sokkel]["timestamp"][-1]-Gameresults[pasient][sokkel]["timestamp"][0]
        tid_list += tid
        tilt_list += tilt_y/len(Gameresults[pasient][sokkel]["timestamp"])
        Accel = Accel/len(Gameresults[pasient][sokkel]["timestamp"])
        accel_list += Accel
        
    tid_list = tid_list/len(sokkel_Id_list)
    tilt_list = tilt_list/len(sokkel_Id_list)
    accel_list = accel_list/len(sokkel_Id_list)

    Gameresults[pasient]["Tilt"] = tilt_list
    Gameresults[pasient]["Tid"] = tid_list
    Gameresults[pasient]["Akselerasjon"] = accel_list

    #alle data er integers
    #Data ønsket: score, average tilt alle brikkene sammen, average tid per sokkel

async def getGamestate(socketServer, preGamestart):
    #henter data fra backend
    #formater data riktig
    #hvis data ikke blir hentet return 
    address = ('127.0.0.1', 8004)
    message = "b"
    # Receive the client packet along with the address it is coming from
    try: 
        message, address = socketServer.recvfrom(1024)
        message = message.decode("utf-8")
        # Capitalize the message from the client
        message = message.lower()
    except:
        print("Did not recieve Game_start update")
    finally:

        try:
            Game_start, pasient = message.split(' ', 1)
        except:
            Game_start = preGamestart
            pasient = "errorpatient"

        #format: message = "1 pasient1"
        #eller: message = "0 whaterver (denne dataen brukes ikke)"
        return Game_start, pasient

async def waitForGamestart(socketServer, sokkel_Id_list):
    global client_handler
    Game_start = 0
    #En status hvor den har initiert og venter på å starte spillet
    pasient = ""
    Game_start, pasient = await getGamestate(socketServer, Game_start)
    #Game_start = int(input("trykk 1 for å starte et game "))
    for sokkel in sokkel_Id_list:
        if (await client_handler.get_connected(str(sokkel)) == False):
            print("Lost communication with sokkel with id " + str(sokkel))
        await asyncio.sleep(0.5)
    sokkel_Id_list = await client_handler.get_IDs()
    return Game_start, pasient




async def sendLastReading(socketServer, temp_dic):

    address = ('127.0.0.1', 8148)
    Reading = str(temp_dic["gyro_x"]) + " " + str(temp_dic["gyro_y"]) + " " + str(temp_dic["gyro_z"]) + " " + str(temp_dic["accel_x"]) + " " + str(temp_dic["accel_y"]) + " " + str(temp_dic["accel_z"]) + " " + str(temp_dic["timestamp"])
    Reading = str.encode(Reading) #codek register encoding
    socketServer.sendto(Reading, address) 
    return 0


async def saveGame(socketServer, pasient):
    global Gameresults

    #åpner fil og json dumper i filen

    save_data = {}

    # Attempt to open the pasient file
    try:
        with open(f"{pasient}.json", "r") as f:
            data = json.load(f)
    except:
        data = {}

    # Set first key of the save data to the highest session number in data + 1 (or 0 if data is empty)
    save_data[str(max((int(k) for k in data.keys()), default=-1) + 1)] = Gameresults[pasient]
    # Update the data with the new save data
    data.update(save_data)

    # Write the data back to the file as a styled JSON
    with open(f"{pasient}.json", "w") as f:
        json.dump(data, f, indent=4)

    #Create json
    #json.dump(Gameresults, open("GameResults.json", "w"))

    '''
    #sender game ended
    address = ('127.0.0.1', 8004)

    Reading = "Game_start 0"
    Reading = str.encode(Reading)
    
    socketServer.sendto(Reading, address) 
    socketServer.close()
    '''
    #filbehandlingsshit

async def Gameloop(socketReciveServer, socketSendServer, sokkel_Id_list, Game_start1, pasient, Hall_effekt=[0,0], Led_lys=[0,0]):
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
        await asyncio.sleep(0.2)


        #while Hall_effekt[RandomHull].value == 0:
        for i in range(10): #kjører denne siden vi ikke er i raspberry pi.
            for i in range(15): #Looper her fordi jeg er mer interresert i dataen enn de andre sjekkene i loopen.
                await asyncio.sleep(0.125) #en arbitrary sleep som skal tillate serveren å ta inn data. 
                temp_dic = await client_handler.get_last_reading(str(sokkel))
                await sendLastReading(socketSendServer, temp_dic)
                Akselerasjon.append([temp_dic["accel_x"], temp_dic["accel_y"], temp_dic["accel_z"]])
                Gyro.append([temp_dic["gyro_x"], temp_dic["gyro_y"], temp_dic["gyro_z"]])
                Time.append(temp_dic["timestamp"])
                print("Gamemaster Tilt: ", Gyro, "   Akselerasjon: ", Akselerasjon, "   Time: ", Time)

            #await sendLastReading(socketSendServer, temp_dic)
            Game_start, ikkeBrukPasient = await getGamestate(socketReciveServer, Game_start)
            if Game_start == 0:
                print("Game cancelled")
                await saveFullreading(pasient, sokkel)
                print("collected data from sokkel run")
                Reading = "0 0 0 0 0 0 "+ str(temp_dic["timestamp"])
                Reading = str.encode(Reading) #codek register encoding
                socketSendServer.sendto(Reading, ('127.0.0.1', 8148)) 
                return 0
            if (await client_handler.get_connected(str(sokkel)) == False):
                print("lost sokkel connection")
        #Led_lys[RandomHull].off()
        saveFullreading(pasient, sokkel)
        print("collected data from sokkel run")

    #sendToBackend("Game finished", Gameresults)
    Game_start = 0
    Reading = "0 0 0 0 0 0 "+ str(temp_dic["timestamp"])
    Reading = str.encode(Reading) #codek register encoding
    socketSendServer.sendto(Reading, ('127.0.0.1', 8148)) 
    #kanskje Game_start skal være lik 2 slik at backend får en oppgavekode
    await client_handler.send_to_client(str(sokkel), "set_gameplay_state idle")

    #calculate averages
    return 0

async def GameMaster2():

    socketSendServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address1 = ('127.0.0.1', 8003)
    socketSendServer.bind(address1)
    socketSendServer.settimeout(1)

    socketReciveServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketReciveServer.settimeout(1)
    address2 = ('127.0.0.1', 8004)
    socketReciveServer.bind(address2)  
    socketReciveServer.settimeout(1)


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
            asyncio.sleep(0.4)
            socketReciveServer.settimeout(1)
            Game_start, pasient = await waitForGamestart(socketReciveServer, sokkel_Id_list)
        else:
            socketReciveServer.settimeout(0)
            await Gameloop(socketReciveServer, socketSendServer, sokkel_Id_list, Game_start, pasient)
            await saveGame(socketReciveServer, pasient)
            Game_start = 0

async def game_master(pasient):
    global client_handler
    server_ip = "127.0.0.1"
    port = 8003
    sockServer = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
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
        sokkel_Id_list = await client_handler.get_IDs()
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
            if (await client_handler.get_connected(str(sokkel)) == False):
                print("Lost communication with sokkel with id " + str(sokkel))
            await asyncio.sleep(0.5)
        sokkel_Id_list = await client_handler.get_IDs()
            
    #jeg forestiller meg at programmet kjører parallelt med back end og annet, men #har ikke jobbet så mye med det før, antar at sleep ikke egt trengs men ønsker #raspberry setter av tid til at andre programmer skal kunne gjøres. 




        while (Game_start == 1):
    #når spillet starter aktiveres en sokkel, en halleffekt og et LED lyst. #Aktivering av sokkelen betyr at den må requeste send data

            for sokkel in sokkel_Id_list:
                Gameresults[pasient][sokkel] = {}
                #RandomHull = randint(0, len(Hall_effekt))
                #Led_lys[RandomHull].on()
                await client_handler.send_to_client(str(sokkel), "set_gameplay_state active")
                await client_handler.reset_client_data(str(sokkel))
                #while Hall_effekt[RandomHull].value == 0:
                for i in range(100):
                    for i in range(10): #Looper her fordi jeg er mer interresert i dataen enn de andre sjekkene i loopen.
                        await asyncio.sleep(0.125)
                        temp_dic = await client_handler.get_last_reading(str(sokkel))
                        Akselerasjon.append([temp_dic["accel_x"], temp_dic["accel_y"], temp_dic["accel_z"]])
                        Gyro.append([temp_dic["gyro_x"], temp_dic["gyro_y"], temp_dic["gyro_z"]])
                        Time.append(temp_dic["timestamp"])
                        print("Gamemaster Tilt: ", Gyro, "   Akselerasjon: ", Akselerasjon, "   Time: ", Time)
                        #send data to backend
                    #Game_start = getBackEnd()
                    if Game_start == 0:
                        print("Game cancelled")
                        break
                    if (await client_handler.get_connected(str(sokkel)) == False):
                        print("lost sokkel connection")
                #Led_lys[RandomHull].off()
                
                Gameresults[pasient][sokkel].append(client_handler.collectFullData(str(sokkel)))
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



# Replace hostname and port if needed
IP = 'localhost'
PORT = 5001
client_handler = connection_handler_.connection_handler()

async def corutine1():
    global client_handler
    print("started serverroutine")
    server = await asyncio.start_server(client_handler.handle_client, IP, PORT)  
    print(f'Serving on {server.sockets[0].getsockname()}')

    # I am not sure whether this blocks further async execution. If it does, you might have to run this as a separate thread.
    async with server:
        await server.serve_forever()

async def corutine2():
    Gamemaster = await GameMaster2()




async def main():

    # Client server initialization
    #client_handler = connection_handler_.connection_handler() # This is mad ugly, consider renaming file
    #server = await asyncio.start_server(client_handler.handle_client, IP, PORT)  
    #print(f'Serving on {server.sockets[0].getsockname()}')

    # I am not sure whether this blocks further async execution. If it does, you might have to run this as a separate thread.
    #async with server:
    #    await server.serve_forever()

    # Start Game Master here. 
    # Only global variables and a main routine! Don't put any other code here pls. Keep main() clean.
    # Run it as an asyncio task so that it runs concurrently with the client handler.
    # Remember to pass the client_handler object to the Game Master program as a parameter. 
    # This way you can access the public methods like send_to_client from the Game Master program.
    
    await asyncio.gather(corutine1(), corutine2())
    

    print("Test")
    # Start new backend thread here to handle communication with front end. 
    # Only global variables and a main routine! Don't put any other code here pls. Keep main() clean.
    # Run it as a separate thread so that it runs concurrently with the Game Master.
    # You shouldn't have to pass the client_handler to this thread, but you might have to pass the Game Master object.
    #
    #
    #

# Do not touch this line under any circumstances!
asyncio.run(main())