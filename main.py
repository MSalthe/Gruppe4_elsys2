import asyncio
import time
import random
import connection_handler as connection_handler_
#from gpiozero import LED, InputDevice, LEDBoard, PWMLED # REST IN PEACE LMAMOAOMAOM
from random import randint
import socket
import json
import math
import copy
from periphery import GPIO

#sudo nmcli device wifi hotspot ssid Dexteritas password 12345678

debug = True

Gameresults = { } #dictionary med steg pasient (dic)- sokkel (dic)- typedata (dic)- liste

async def score(pasient, sokkel_Id_list):
    score = 1000000
    
    tid_per_sokkel = Gameresults[pasient]["Tid"]
    akselerasjon_per_tid = Gameresults[pasient]["Akselerasjon"]
    gyro_per_tid = Gameresults[pasient]["Tilt"]
    tid_multiplier = 1/(0.7*tid_per_sokkel)
    accel_multiplier = 1/akselerasjon_per_tid
    gyro_multiplier =1000/(gyro_per_tid)
    print("Tid multiplier: " + str(tid_multiplier))
    print("Accel multiplier: " + str(accel_multiplier))
    print("Gyro multiplier: " + str(gyro_multiplier))
    #lager score av hele spillet med en average per sokkel data
    '''
    for sokkel in sokkel_Id_list:
        tilt_y = 0
        tid_per_sokkel += (Gameresults[pasient][sokkel]["timestamp"][-1] - Gameresults[pasient][sokkel]["timestamp"][0])/len(sokkel_Id_list)

        accel_x = 0
        accel_y = 0
        accel_z = 0
        accel_average = 0

        for i in range(len(Gameresults[pasient][sokkel]["timestamp"])):
            tilt_y += abs(Gameresults[pasient][sokkel]["gyro_y"][i] - tilt_y_offset)
            accel_x = Gameresults[pasient][sokkel]["accel_x"][i]
            accel_y = Gameresults[pasient][sokkel]["accel_y"][i]
            accel_z = Gameresults[pasient][sokkel]["accel_z"][i]
            Accel += math.sqrt(accel_x**2+accel_y**2+accel_z**2)
    '''
    print("Score: " + str(score*tid_multiplier*gyro_multiplier*accel_multiplier))

    return score*tid_multiplier*gyro_multiplier*accel_multiplier

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
    try:
        tilt_y_offset = 0
        tilt_list = 0
        tid_list = 0
        accel_list = 0
        

        for sokkel in sokkel_Id_list:
            tilt_y = -7200
            tid = 0
            accel_x = 0
            accel_y = 0
            accel_z = 0
            Accel = 0

            for i in range(len(Gameresults[pasient][sokkel]["timestamp"])):
                tilt_y += abs(Gameresults[pasient][sokkel]["gyro_y"][i] - tilt_y_offset)
                accel_x = Gameresults[pasient][sokkel]["accel_x"][i]
                accel_y = Gameresults[pasient][sokkel]["accel_y"][i]
                accel_z = Gameresults[pasient][sokkel]["accel_z"][i]
                Accel += math.sqrt(accel_x**2+accel_y**2+accel_z**2)
            tid = Gameresults[pasient][sokkel]["timestamp"][-1]-Gameresults[pasient][sokkel]["timestamp"][0]
            tid_list += tid
            tilt_list += tilt_y/len(Gameresults[pasient][sokkel]["timestamp"])
            Accel = Accel/len(Gameresults[pasient][sokkel]["timestamp"])
            accel_list += Accel

        tid_list = tid_list/len(sokkel_Id_list)
        tilt_list = tilt_list/len(sokkel_Id_list)
        accel_list = accel_list/len(sokkel_Id_list)
    except:
        tid_list = 10
        tilt_list = 10
        accel_list = 10
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
    return Game_start, pasient, sokkel_Id_list

async def sendLastReading(socketServer, temp_dic):
    address = ('127.0.0.1', 8148)
    try:
        Reading = str(temp_dic["gyro_x"]) + " " + str(temp_dic["gyro_y"]) + " " + str(temp_dic["gyro_z"]) + " " + str(temp_dic["accel_x"]) + " " + str(temp_dic["accel_y"]) + " " + str(temp_dic["accel_z"]) + " " + str(temp_dic["timestamp"])+ " 0 0"                                                                                                                                                                                                                              
        Reading = str.encode(Reading) #codek register encoding
        socketServer.sendto(Reading, address)
        if (debug): print("sent message, im in sendLastReading")
    except:
        print("Warning: Failed to send reading!")

async def sendReadingToCup(socketServer, Gyro):
    address = (('10.42.0.1', 8081))
    #Reading = str.encode(str(Gyro)) #codek register encoding
    Reading = str.encode(Gyro[-1][0], Gyro[-1][1], Gyro[-1][2])
    socketServer.sendto(Reading, address)

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

    print("saved game")
    #filbehandlingsshit

async def Gameloop(socketReciveServer, socketSendServer, cupServer, sokkel_Id_list, Game_start1, pasient, Linked_gpio=[0,0]):
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
    temp_dic = {}
    RandomHull = 0
    RandomHull_list = list()
    for i in range(2):
        for sokkel in sokkel_Id_list:
            for i in range(len(Linked_gpio)):
                Linked_gpio[i][0].write(False)
            Gameresults[pasient][sokkel] = {}
            RandomHull = randint(0, (len(Linked_gpio)-1))
            while Linked_gpio[RandomHull][1].read() == 1:
                RandomHull = randint(0, (len(Linked_gpio)-1))
            RandomHull_list.append(RandomHull)
            Linked_gpio[RandomHull][0].write(True)
            #await client_handler.send_to_client(str(sokkel), "set_gameplay_state active")
            await  client_handler.send_command_to_client(str(sokkel), "set_gameplay_state", -1, 1)
            await client_handler.reset_client_data(str(sokkel))
            await asyncio.sleep(0.2)


            while Linked_gpio[RandomHull][1].read() == 0:
            #for i in range(10): #kjører denne siden vi ikke er i raspberry pi.
                for i in range(5): #Looper her fordi jeg er mer interresert i dataen enn de andre sjekkene i loopen.
                    await asyncio.sleep(0.125) #en arbitrary sleep som skal tillate serveren å ta inn data. 
                    await sendLastReading(socketSendServer, temp_dic)
                    temp_dic = await client_handler.get_last_reading(str(sokkel))
                    print(temp_dic)
                    #Akselerasjon.append([temp_dic["accel_x"], temp_dic["accel_y"], temp_dic["accel_z"]])
                    #Gyro.append([temp_dic["gyro_x"], temp_dic["gyro_y"], temp_dic["gyro_z"]])
                    #Time.append(temp_dic["timestamp"])
                    #print("Gamemaster Tilt: ", Gyro, "   Akselerasjon: ", Akselerasjon, "   Time: ", Time)
                
                #await sendLastReading(socketSendServer, temp_dic)             
                
                if (await client_handler.get_client_dropped(str(sokkel))):
                    break
                    
                
                #Game_start, ikkeBrukPasient = await getGamestate(socketReciveServer, Game_start)
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
            Linked_gpio[RandomHull][0].write(False)
            await saveFullreading(pasient, sokkel)
            print("collected data from sokkel run")
            if not (await client_handler.get_client_dropped(str(sokkel))):
                for i in range(4):
                    await  client_handler.send_command_to_client(str(sokkel), "set_gameplay_state", -1, 0)
            print("2 second sleep in gm for next sokkel")
            await asyncio.sleep(0.75)

    
    #sendToBackend("Game finished", Gameresults)
    Game_start = 0
    await calculate_averages(pasient, sokkel_Id_list)
    Reading = "0 0 0 0 0 0 0 1" + str(await score(pasient, sokkel_Id_list))
    Reading = str.encode(Reading) #codek register encoding
    for i in range(4):
        socketSendServer.sendto(Reading, ('127.0.0.1', 8148)) 
    #kanskje Game_start skal være lik 2 slik at backend får en oppgavekode
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
    
    cupServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cupServer.bind(('10.42.0.1', 8080))
    cupServer.settimeout(1)

    print("started gamemaster")

    #Initialiser Hall_effekt
    
    HE1=GPIO(99, "in")
    HE2=GPIO(114, "in")
    HE3=GPIO(103, "in")
    HE4=GPIO(105, "in")
    HE5=GPIO(101, "in")
    HE6=GPIO(102, "in")
    HE7=GPIO(150, "in")
    HE8=GPIO(106, "in")


    hall_effect_sensors = [HE1, HE2, HE3, HE4, HE5, HE6, HE7, HE8]



    #liste over alle initialiserte hall effekt
    #Hall_effekt = [HE1, HE2, HE3, HE4, HE5, HE6, HE7, HE8, HE9, HE10, HE11, HE12]
    
    
    LED1=GPIO(113, "out")
    LED2=GPIO(115, "out")
    LED3=GPIO(116, "out")
    LED4=GPIO(107, "out")
    LED5=GPIO(147, "out")
    LED6=GPIO(108, "out")
    LED7=GPIO(100, "out")
    LED8=GPIO(149, "out")
    #Led_lys = [LED12, LED10, LED8,LED1, LED6,LED4,LED3,LED11,LED2,LED7] # Todo rekkefølge
    Linked_gpio = [[LED1, HE1], [LED2, HE2], [LED3, HE3], [LED4, HE4], [LED5, HE5], [LED6, HE6], [LED7, HE7], [LED8, HE8]]
    for i in range(len(Linked_gpio)):
        Linked_gpio[i][0].write(False)

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
            await asyncio.sleep(0.4)
            socketReciveServer.settimeout(1)
            Game_start, pasient, sokkel_Id_list = await waitForGamestart(socketReciveServer, sokkel_Id_list)
        else:
            socketReciveServer.settimeout(0)
            await Gameloop(socketReciveServer, socketSendServer, cupServer, sokkel_Id_list, Game_start, pasient, Linked_gpio)
            await saveGame(socketReciveServer, pasient)
            Game_start = 0

# Replace hostname and port if needed
IP = '10.42.0.1'
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
    await asyncio.gather(corutine1(), corutine2())
    
    print("Test")

# Do not touch this line under any circumstances!
asyncio.run(main())
