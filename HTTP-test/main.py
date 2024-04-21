import asyncio
import time
import random
import connection_handler as connection_handler_
from gpiozero import LED, InputDevice, LEDBoard, PWMLED
from random import randint
import socket


Gameresults = { } #dictionary med steg pasient (dic)- sokkel (dic)- typedata (dic)- liste



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
    Gamemaster = await game_master()
    print("starting gamemaster")




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