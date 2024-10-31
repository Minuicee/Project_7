import threading
import socket
import sys



#*Get IP and PORT
HOST = socket.gethostbyname(socket.gethostname())
PORT = 9998

#*Init server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print("Server is listening...")

#*Init clients
clients = {}
handle_threads = {}

#*Start accepting connections
def acceptConnections():       
    
    while True:
        client, address = server.accept()
        
        player_information = client.recv(1024).decode("utf-8")
        name, color_r, color_g, color_b = player_information.split(",")

        clients[client] = {"name": name,"color": (color_r,color_g,color_b) , "position": (500,400)}
        handle_threads[client] = threading.Thread(target=handle, args=(client, ))
        handle_threads[client].start()
        
        print(f"{address} connected..")
        
acceptConnections_thread = threading.Thread(target=acceptConnections)
acceptConnections_thread.start()

              
def sendInfos(infos):
    try: 
        for client in clients:
            client.send(infos.encode("utf-8"))
    except (BrokenPipeError, ConnectionResetError):
        print("Player connection lost")
        sys.exit()

def handle(client):
    while True:
        try:
            personal_data  = client.recv(1024).decode("utf-8")
            clients[client]["position"] = (personal_data.split(","))
            sendInfos(f"{clients[client]["name"]}!{clients[client]["color"]}!{clients[client]["position"]}") #exclamation mark is for data splitting
        except:
            sendInfos(f"!PlayerLeft!{clients[client]["name"]}")
            clients.pop(client)
            break