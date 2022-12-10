import socket
import signal
import sys
import argparse
from urllib.parse import urlparse
import selectors
import os


TIMEOUT = 5
PORT = 4444 #Discovery Service Port Number Constant
DISCOVERY = f'discovery://localhost:{PORT}'
discoverServer = ('localhost',PORT)

# Socket for sending messages.

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(TIMEOUT)

# Server address.

server = ('', '')

# User name for player.

name = ''

# Inventory of items.

inventory = []

# Signal handler for graceful exiting.  Let the server know when we're gone.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    message='exit'
    client_socket.sendto(message.encode(),server)
    for item in inventory:
        message = f'drop {item}'
        client_socket.sendto(message.encode(), server)
    sys.exit(0)

# Simple function for setting up a prompt for the user.

def do_prompt(skip_line=False):
    if (skip_line):
        print("")
    print("> ", end='', flush=True)

# Function to join a room.

def receiveResponse():
    try:
        response, addr = client_socket.recvfrom(1024)
        message = response.decode()
        return message
    except socket.timeout:
        print('Error: Timeout. Have not received response from server for more than 5 seconds.')
        sys.exit(1)

def serverLookup(LookupName):
    client_socket.sendto(f'LOOKUP {LookupName}'.encode(), discoverServer)
    response, addr = client_socket.recvfrom(1024)
    return response.decode()

def join_room(LookupResponse):
    global server

    words = LookupResponse.split()

    #IF SERVER FOUND IN DISCOVERY SERVICE, THEN JOIN IT
    if (words[0]=='OK'):
        serverAddress = urlparse(words[1])
        server = (serverAddress.hostname,serverAddress.port)
        message = f'join {name}'
        client_socket.sendto(message.encode(), server)
        response = receiveResponse()
        print(response)
        return 'OK'
    else:
        print(LookupResponse)
        return 'NOTOK'



# Function to handle commands from the user, checking them over and sending to the server as needed.

def process_command(command, arg2):

    global server
    
    # Parse command.
    if (command != 'exit'):
        command = command.read().strip()
    words = command.split()
    # Check if we are dropping something.  Only let server know if it is in our inventory.

    if (words[0] == 'drop'):
        if (len(words) != 2):
            print("Invalid command")
            return
        elif (words[1] not in inventory):
            print(f'You are not holding {words[1]}')
            return

    # Send command to server, if it isn't a local only one.

    if (command != 'inventory'):
        message = f'{command}'
        client_socket.sendto(message.encode(), server)

    # Check for particular commands of interest from the user.

    if (command == 'exit'):
        for item in inventory:
            message = f'drop {item}'
            client_socket.sendto(message.encode(), server)
        sys.exit(0)
    elif (command == 'look'):
        print(receiveResponse())
    elif (command == 'inventory'):
        print("You are holding:")
        if (len(inventory) == 0):
            print('  No items')
        else:
            for item in inventory:
                print(f'  {item}')
    # ROOM TO THE NORTH
    elif (command == 'north'):
        join_room(receiveResponse())
        
    # ROOM TO THE SOUTH
    elif (command == 'south'):
        join_room(receiveResponse())

    # ROOM TO THE EAST
    elif (command == 'east'):
        join_room(receiveResponse())

    # ROOM TO THE WEST
    elif (command == 'west'):
        join_room(receiveResponse())

    # ROOM UP
    elif (command == 'up'):
        join_room(receiveResponse())

    # ROOM DOWN
    elif (command == 'down'):
        join_room(receiveResponse())
                
    elif (words[0] == 'say'):
        print(receiveResponse())

    elif (words[0] == 'take'):
        response = receiveResponse()
        print(response)
        words = response.split()
        if ((len(words) == 2) and (words[1] == 'taken')):
            inventory.append(words[0])
    elif (words[0] == 'drop'):
        response = receiveResponse()
        print(response)
        inventory.remove(words[1])
    else:
        print(receiveResponse())

def server_message(arg1, arg2):
    response, addr = arg1.recvfrom(1024)
    message = response.decode()
    if (message == 'exit'):
        print('\nDisconnected from server ... exiting!')
        process_command('exit', None)
    else:
        print(response.decode())
# Our main function.

def main():

    global name
    global client_socket
    global server

    os.set_blocking(sys.stdin.fileno(), False)

    client_selector = selectors.DefaultSelector()

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Check command line arguments to retrieve a URL.

    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name for the player in the game")
    parser.add_argument("serverName", help="name of room to start in.")
    args = parser.parse_args()

    # Check the URL passed in and make sure it's valid.  If so, keep track of
    # things for later.

    # try:
    #     server_address = urlparse(args.server)
    #     if ((server_address.scheme != 'room') or (server_address.port == None) or (server_address.hostname == None)):
    #         raise ValueError
    #     host = server_address.hostname
    #     port = server_address.port
    #     server = (host, port)
    # except ValueError:
    #     print('Error:  Invalid server.  Enter a URL of the form:  room://host:port')
    #     sys.exit(1)
    
    name = args.name
    serverName = args.serverName


    # Send message to enter the room.

    firstJoin = serverLookup(serverName)
    if (firstJoin.split()[0] == 'NOTOK'):
        print(firstJoin)
        sys.exit(0)
    join_room(firstJoin)
   
    # We now loop forever, sending commands to the server and reporting results

    client_selector.register(sys.stdin, selectors.EVENT_READ, process_command)
    client_selector.register(client_socket, selectors.EVENT_READ, server_message)
    while True:

        # Prompt the user before beginning.

        # do_prompt()

        sys.stdout.write('>')
        sys.stdout.flush()
        for k, mask in client_selector.select():
            callback = k.data
            callback(k.fileobj, mask)

        # Get a line of input.

        # line=sys.stdin.readline()[:-1]

        # Process command and send to the server.

        # process_command(line)
 
    client_selector.close()
if __name__ == '__main__':
    main()
