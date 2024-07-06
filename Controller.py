import pygame
from Cell import *
from Constants import *
from View import *
from Food import *
import socket
import threading
# Global variables
client = None

scene = 1 # 0 = main; 1 = game; 2 = end
isRunning = True
isConnected = False

cellMap = dict()
foodList = [[[Food(lin,col,l) for l in range(NB_BY_FOODBOX)] for col in range(NBHOR_FOODBOX)] for lin in range(NBVERT_FOODBOX)]

currCellId = -1
currCell = None
clock = pygame.time.Clock()
MAX_FRAME_RATE = 30


# Connect
def connect():
    global client, isConnected
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ADDRESS)
    isConnected = True
    print("yey")


# to send messages to server
def sendMessage(msg):
    message = msg.encode(FORMAT)
    msgLength = str(len(msg)).encode(FORMAT)
    msgLength += b" "*(HEADER-len(msgLength))

    if isConnected:
        # first message (HEADER bytes) = 2nd message's length
        client.send(msgLength+message)

def getblock(conn, length):
    buffer = "".encode(FORMAT)
    while len(buffer) < length:
        buffer += conn.recv(length-len(buffer))
    return buffer


# message receiver handler
def receiveMessage():
    global scene
    while scene == 1:
        if isConnected:
            msgLength = client.recv(HEADER).decode(FORMAT) #first msg received = length of msg that's about to come
            if msgLength != None:   #avoid first default blank message
                
                msgLength = int(msgLength)
                message = getblock(client, msgLength).decode(FORMAT).split(";")

                if message[0] == "ID":
                    global currCellId
                    currCellId = int(message[1])
                elif message[0] == "CREATE":
                    for i in range(1,len(message)):
                        message[i]=message[i].split(",")
                        cellMap[int(message[i][0])] = Cell(int(message[i][0]), float(message[i][1]), float(message[i][2]), float(message[i][3]), True)
                        if int(message[i][0]) < NB_BOTS:
                            cellMap[int(message[i][0])].bot = True
                elif message[0] == "UPDATE":
                    for i in range(1,len(message)):
                        message[i]=message[i].split(",")
                        cellMap[int(message[i][0])].Update(float(message[i][1]),float(message[i][2]))
                        cellMap[int(message[i][0])].UpdateRadius(float(message[i][3]))

                elif message[0] == "FOOD_UPDATE":
                    for i in range(1,len(message)):
                        msg = message[i].split(",")
                        lin,col,id = int(msg[0]), int(msg[1]), int(msg[2])
                        foodList[lin][col][id].active = bool(int(msg[3]))
                        foodList[lin][col][id].x = int(msg[4])
                        foodList[lin][col][id].y = int(msg[5])


                elif message[0] == "FOOD_CREATE":
                    pass
                elif message[0] == "INACTIVE":
                    if int(message[1]) == currCellId:
                        scene = 2
                        drawEnd(screen)
                        return
                    else:
                        cellMap.pop(int(message[1]))
                elif message[0] == "END":
                    for cell in cellMap.values():
                        cell.isRunning = False
                    return


def main():
    global scene, isRunning, cellMap, currCellId, currCell, scene
    while isRunning:    
        if currCellId != -1:
            if scene == 1:
                # Draw the scene
                drawScene(screen, currCellId, cellMap, foodList)

            #Preparing next frame
            mousex,mousey = pygame.mouse.get_pos()
            move_x, move_y = (mousex-SCREEN_WIDTH/2)*cellMap[currCellId].speed,(mousey-SCREEN_HEIGHT/2)*cellMap[currCellId].speed
            sendMessage(f"UPDATE;{move_x};{move_y}")

            clock.tick(MAX_FRAME_RATE)

        # if close
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRunning = False
                sendMessage("DISCONNECT")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if scene == 2:
                    print("[RECONNECTING]")
                    cellMap = dict()
                    currCellId = -1
                    currCell = None
                    scene = 1
                    try:
                        connect()
                    except:
                        print("Connection error")

                    #run parallel thread for receiving messages
                    thread = threading.Thread(target = receiveMessage)
                    thread.daemon = True
                    thread.start()



    pygame.display.quit()
    pygame.quit()
    client.close()


# Start pygame

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
screen.fill((255,255,255))
pygame.display.set_caption(("GAME"))

# connect to server
try:
    connect()
except:
    print("Connection error")

#run parallel thread for receiving messages
thread = threading.Thread(target = receiveMessage)
thread.daemon = True
try:
    thread.start()
except:
    pass

try:
    # main thread
    main()
except:
    pass