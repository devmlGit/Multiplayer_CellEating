import socket
import threading
from Constants import *
from Cell import *
from Food import *
import random
import pygame

# Global variables
cellMap = dict()
foodList = [[[Food(lin,col,l) for l in range(NB_BY_FOODBOX)] for col in range(NBHOR_FOODBOX)] for lin in range(NBVERT_FOODBOX)]
connMap = dict()
idCounter = 0
clock = pygame.time.Clock()
isPlaying = True


# send message to client (via conn socket)
def sendMessage(msg, conn):
    #print(msg)
    message = msg.encode(FORMAT)
    #print(len(msg), len(message))
    msgLength = str(len(message)).encode(FORMAT)
    msgLength += b" " * (HEADER-len(msgLength))

    # first message (HEADER bytes) = 2nd message's length
    conn.send(msgLength+message)


def getblock(conn, length):
    buffer = "".encode(FORMAT)
    while len(buffer) < length:
        buffer += conn.recv(length-len(buffer))
    return buffer

# when client connection
def handleClient(conn, addr, id):

    print(f"\n[SERVER] New connection by {addr}\n")
    print(id)
    clientCell = cellMap[id]

    # wait for messages
    while isPlaying:
        msgLength = conn.recv(HEADER) #first msg received = length of msg that's about to come

        if msgLength:   #avoid first default blank message
            msgLength = msgLength.decode(FORMAT)
            msgLength = int(msgLength) 
            message = getblock(conn,msgLength).decode(FORMAT).split(";")

            if message[0] == "UPDATE":
                clientCell.Update(clientCell.x+ float(message[1]), clientCell.y+float(message[2]))

            elif message[0] == "DISCONNECT":
                print(f"[CLIENT {addr[0]} PORT {addr[1]}] Disconnected")
                sendMessage("END",connMap[clientCell.id])
                connMap.pop(clientCell.id)
                cellMap.pop(clientCell.id)

                for otherconn in connMap.values():
                    sendMessage(f"INACTIVE;{id}", otherconn)

                return


# send various messages to clients
def sendUpdates():
    while isPlaying:

        for cell in list(cellMap.values()):
            if cell.bot:
                cell.Update(cell.x+(random.randint(0,SCREEN_WIDTH)-SCREEN_WIDTH/2)*cell.speed, cell.y+(random.randint(0,SCREEN_WIDTH)-SCREEN_WIDTH/2)*cell.speed)

        for cell1_key in list(cellMap):
            for cell2_key in list(cellMap):
                try:
                    if cellMap[cell1_key].id != cellMap[cell2_key].id and cellMap[cell1_key].isEaten(cellMap[cell2_key]):
                        cellMap[cell2_key].UpdateRadius((cellMap[cell1_key].radius**2+cellMap[cell2_key].radius**2)**0.5)
                        
                        print(f"[PLAYER {cell1_key}] lost")
                        for conn in connMap.values():
                            sendMessage(f"INACTIVE;{cell1_key}", conn)
                        if cellMap[cell1_key].bot == False:
                            connMap.pop(cell1_key)
                        cellMap.pop(cell1_key)

                except:
                    pass
        
        msg1 = "FOOD_UPDATE"

        for cell_key in list(cellMap):
            for lin in range(NBHOR_FOODBOX):
                for col in range(NBVERT_FOODBOX):
                    for food in foodList[lin][col]:
                        if food.active and food.isEaten(cellMap[cell_key]):
                            cellMap[cell_key].UpdateRadius(cellMap[cell_key].radius+FOOD_GROWTH_RATE/cellMap[cell_key].radius)
                            pass
                        msg1+=f";{lin},{col},{food.id},{int(food.active)},{food.x},{food.y}"
        for key in list(connMap):
            sendMessage(msg1, connMap[key])


        msg2 = "UPDATE"
        for key in list(cellMap):
            msg2 += f";{cellMap[key].id},{cellMap[key].x},{cellMap[key].y},{cellMap[key].radius}"

        for key in list(connMap):
            sendMessage(msg2, connMap[key])


        clock.tick(30)

def main():
    global idCounter
    for i in range(NB_BOTS):
        cellMap[idCounter] = Cell(idCounter,random.randint(0, GRID_WIDTH), random.randint(0,GRID_HEIGHT), 20)
        cellMap[idCounter].bot = True

        idCounter += 1

    while isPlaying:

        # wait for new clients
        conn, addr = server.accept()

        print(f"\n[SERVER] {threading.active_count()-3} active connection(s)\n")

        # update map of cells and conn
        cellMap[idCounter] = Cell(idCounter,random.randint(0, GRID_WIDTH), random.randint(0,GRID_HEIGHT), 20)
        connMap[idCounter] = conn

        # inform the new cell of the existing ones
        msg = "CREATE"
        for cell in cellMap.values():
            msg += f";{cell.id},{cell.x},{cell.y},{cell.radius}"

        sendMessage(msg, conn)

        # inform existing cells of this creation
        for cell in cellMap.values():
            if cell.bot == False:
                sendMessage(f"CREATE;{cellMap[idCounter].id},{cellMap[idCounter].x},{cellMap[idCounter].y},{cellMap[idCounter].radius}", connMap[cell.id])

        sendMessage(f"ID;{idCounter}", conn)

        idCounter += 1
        #new connexion
        thread = threading.Thread(target = handleClient, args = (conn, addr, idCounter-1))
        thread.daemon = True
        thread.start()

############### MAIN ###################

# Configure server
print("[SERVER] server starting")
print(f"[SERVER] server listening on {SERVER}")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)
server.listen()

# launch thread to send updtates to players
thread = threading.Thread(target = sendUpdates)
thread.daemon = True
thread.start()

# run main thread 
thread = threading.Thread(target = main)
thread.daemon = True
thread.start()


while input() != "a":
    pass