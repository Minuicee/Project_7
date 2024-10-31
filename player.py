import socket
import pygame
import sys
import random
import threading

players = {}

class Game():
    def __init__(self): 
        
        #* Ask for name so it can be displayed
        nameEntered = False
        print("")
        while not nameEntered:
            name = input("Enter your name:  ")
            if name == "":
                print("Must enter a name!")
            else:
                nameEntered = True
                
        #* Frame
        pygame.init()
        game_width, game_height = 1000, 800
        game = pygame.display.set_mode((game_width,game_height))

        #*own character info
        char_x, char_y = game_width//2, game_height//2
        char_width, char_height = 100, 100
        velocity = 1 #move velocity
        color = [random.randint(1,255),random.randint(1,255),random.randint(1,255)] #color of character
        
        
        #* Variables for network connection
        HOST = "" #!! Enter hosts IP
        PORT = 9998
        
        #* Connect to server
        try:
            global client
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST,PORT))
        except:
            print("Server is offline!")
            client.close()
            pygame.quit()
            sys.exit()
        
        information_data = f"{name},{color[0]},{color[1]},{color[2]}"
        client.send(information_data.encode("utf-8")) #send name and color
        
        receive_thread = threading.Thread(target=self.receiveFromServer)
        receive_thread.start()
        
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # quit connection if program was closed
                    client.close()
                    pygame.quit()
                    sys.exit()
                    
            keys = pygame.key.get_pressed()
            #Moving Diagonal
            if keys[pygame.K_w] and keys[pygame.K_d] and char_y > 0 and char_x < game_width - char_width: 
                char_y -= velocity / 1.414 
                char_x += velocity / 1.414
            elif keys[pygame.K_s] and keys[pygame.K_d] and char_y < game_height - char_height and char_x < game_width - char_width:  
                char_y += velocity / 1.414
                char_x += velocity / 1.414
            elif keys[pygame.K_a] and keys[pygame.K_s] and char_x > 0 and char_y < game_height - char_height:  
                char_y += velocity / 1.414
                char_x -= velocity / 1.414
            elif keys[pygame.K_a] and keys[pygame.K_w] and char_x > 0 and char_y > 0:  # Nordwest
                char_y -= velocity / 1.414
                char_x -= velocity / 1.414
            
            #Moving normal
            elif keys[pygame.K_w] and char_y > 0:
                char_y -= velocity
            elif keys[pygame.K_s] and char_y < game_height - char_height:
                char_y += velocity
            elif keys[pygame.K_a] and char_x > 0:
                char_x -= velocity
            elif keys[pygame.K_d] and char_x < game_width - char_width:
                char_x += velocity

            #Fill background
            game.fill((135,175,255))
            
            #*Send location to server
            position_data = f"{int(char_x)},{int(char_y)}"
            self.send_data(position_data)
            
            
            #*Draw all players
            for player in players:
                position_str = players[player]["position"].strip("[]")
                x_pos, y_pos =  map(int, position_str.replace("'", "").split(", "))
                color_string = players[player]["color"]
                cleaned_colors = color_string.strip("[]()").replace("'", "").split(",")
                r_color, g_color, b_color = map(int, cleaned_colors)


                pygame.draw.rect(game, (r_color,g_color,b_color), (x_pos,y_pos,char_width,char_height))
                
             
            pygame.display.flip() #update frame
            
    def receiveFromServer(self):
        while True:
            received_data = client.recv(1024).decode("utf-8")
            if received_data[:12] == "!PlayerLeft!":
                name = received_data[12:]
                #del players[name]
            else:
                name, color, position = received_data.split("!")
                players[name] = {"color": color, "position": position}

    def send_data(self, data):
        try:
            client.send(data.encode("utf-8"))
        except (BrokenPipeError, ConnectionResetError):
            print("Lost connection to server")
            pygame.quit()
            sys.exit()

            
if __name__ == "__main__":
    Game()