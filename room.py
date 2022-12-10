import socket
import signal
import sys
import argparse
from urllib.parse import urlparse


DISCOVERPORT = 4444 #Discovery Service Port Number Constant
DISCOVERY = f'discovery://localhost:{DISCOVERPORT}'
discoverServer = ('localhost',DISCOVERPORT)

name = ''
description = ''
items = []
connections = []
rooms = []
north = None
south = None
east = None
west = None
up = None
down = None


# List of clients currently in the room.

client_list = []

def serverLookup(LookupName):
    room_socket.sendto(f'LOOKUP {LookupName}'.encode(), discoverServer)
    response, addr = room_socket.recvfrom(1024)
    return response.decode()


def sendRegister():
    message = f'REGISTER room://localhost:{room_socket.getsockname()[1]} {name}'
    room_socket.sendto(message.encode(),discoverServer)
    response, addr = room_socket.recvfrom(1024)
    words = response.decode().split()
    if (words[0]=='NOTOK'):
        print(response.decode())
        sys.exit(0)
    else:
        return
def sendDeregister():
    message = f'DEREGISTER {name}'
    room_socket.sendto(message.encode(),discoverServer)
    response, addr = room_socket.recvfrom(1024)
    print(response.decode())

# Signal handler for graceful exiting.  

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    sendDeregister()
    sendClients(None,'exit')
    sys.exit(0)

# Search the client list for a particular player.

def client_search(player):
    for reg in client_list:
        if reg[0] == player:
            return reg[1]
    return None

# Search the client list for a particular player by their address.

def client_search_by_address(address):
    for reg in client_list:
        if reg[1] == address:
            return reg[0]
    return None

# Add a player to the client list.

def client_add(player, address):
    registration = (player, address)
    client_list.append(registration)

# Remove a client when disconnected.

def client_remove(player):
    for reg in client_list:
        if reg[0] == player:
            client_list.remove(reg)
            break

# Summarize the room into text.

def summarize_room(addr):

    global name
    global description
    global items
    global north
    global south
    global east
    global west
    global up
    global down

    # Pack description into a string and return it.

    summary = name + '\n\n' + description + '\n\n'
    if len(items) == 0 and len(client_list) <= 1:
        summary += "The room is empty.\n"
    elif len(items) == 1 and len(client_list) == 1:
        summary += "In this room, there is:\n"
        summary += f'  {items[0]}\n'
    elif len(items) == 0 and len(client_list) == 2:
        summary += "In this room, there is:\n"
        for client in client_list:
            if client[1] != addr:
                summary += f'  {client[0]}\n'
    else:
        summary += "In this room, there are:\n"
        for item in items:
            summary += f'  {item}\n'
        for client in client_list:
            if client[1] != addr:
                summary += f'  {client[0]}\n'
    
    return summary

# Print a room's description.

def print_room_summary():

    print(summarize_room(None)[:-1])


def sendClients(addr, message):
    for client in client_list:
        if client[1]!= addr:
            room_socket.sendto(message.encode(),client[1])

# Process incoming message.

def process_message(message, addr):

    # Parse the message.
 
    words = message.split()
    name = client_search_by_address(addr)
    # If player is joining the server, add them to the list of players.

    if (words[0] == 'join'):
        if (len(words) == 2):
            client_add(words[1],addr)
            print(f'User {words[1]} joined from address {addr}')
            for client in client_list:
                if client[1]!= addr:
                    room_socket.sendto(f'\nUser {words[1]} entered the room.'.encode(),client[1])
            return summarize_room(addr)[:-1]
        else:
            return "Invalid command"

    # If player is leaving the server. remove them from the list of players.

    elif (message == 'exit'):
        client_remove(client_search_by_address(addr))
        sendClients(addr, f'\n{name} left the game.')
        return 'Goodbye'

    # If player looks around, give them the room summary.

    elif (message == 'look'):
        return summarize_room(addr)[:-1]

    elif (message == 'north'):
        res = serverLookup(north)
        if (res.split()[0] == 'OK'):
            sendClients(addr, f'\n{name} left the room, heading north.')
            client_remove(name)
        return serverLookup(north)
    elif (message == 'south'):
        res = serverLookup(south)
        if (res.split()[0] == 'OK'):
            sendClients(addr, f'\n{name} left the room, heading south.')
            client_remove(name)
        return serverLookup(south)
    elif (message == 'east'):
        res = serverLookup(east)
        if (res.split()[0] == 'OK'):
            sendClients(addr, f'\n{name} left the room, heading east.')
            client_remove(name)
        return serverLookup(east)
    elif (message == 'west'):
        res = serverLookup(west)
        if (res.split()[0] == 'OK'):
            sendClients(addr, f'\n{name} left the room, heading west.')
            client_remove(name)
        return serverLookup(west)
    elif (message == 'up'):
        res = serverLookup(up)
        if (res.split()[0] == 'OK'):
            sendClients(addr, f'\n{name} left the room, heading up.')
            client_remove(name)
        return serverLookup(up)
    elif (message == 'down'):
        res = serverLookup(down)
        if (res.split()[0] == 'OK'):
            sendClients(addr, f'\n{name} left the room, heading down.')
            client_remove(name)
        return serverLookup(down)
        
    # Say Command
    elif (words[0] == 'say'):
        if (len(words) > 1):
            user_message = message[4:]
            sendClients(addr,f'{name} said "{user_message}".')
            return f'You said "{user_message}.'
        else:
            return "What did you want to say?"
    # If player takes an item, make sure it is here and give it to the player.

    elif (words[0] == 'take'):
        if (len(words) == 2):
            if (words[1] in items):
                items.remove(words[1])
                return f'{words[1]} taken'
            else:
                return f'{words[1]} cannot be taken in this room'
        else:
            return "Invalid command"

    # If player drops an item, put in in the list of things here.

    elif (words[0] == 'drop'):
        if (len(words) == 2):
            items.append(words[1])
            return f'{words[1]} dropped'
        else:
            return "Invalid command"
    

    # Otherwise, the command is bad.

    else:
        return "Invalid command"
    

def checkUrl(url):
    try:
        server_address = urlparse(url)
        if ((server_address.scheme != 'room') or (server_address.port == None) or (server_address.hostname == None)):
            raise ValueError
    except ValueError:
        print('Error:  Invalid Room Server.  Enter a URL of the form:  room://host:port')
        sys.exit(1)

# Our main function.

def main():

    global name
    global description
    global items
    global connections
    global room_socket
    global north
    global south
    global east
    global west
    global up
    global down
    global rooms

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Check command line arguments for room settings.

    parser = argparse.ArgumentParser()
    parser.add_argument('-n',dest='north', help='Optional argument to specify another room to the North')
    parser.add_argument('-s',dest='south', help='Optional argument to specify another room to the South')
    parser.add_argument('-e',dest='east', help='Optional argument to specify another room to the East')
    parser.add_argument('-w',dest='west', help='Optional argument to specify another room to the West')
    parser.add_argument('-u',dest='up', help='Optional argument to specify another room in Up direction')
    parser.add_argument('-d',dest='down', help='Optional argument to specify another room in Down direction')
    parser.add_argument("name", help="name of the room")
    parser.add_argument("description", help="description of the room")
    parser.add_argument("item", nargs='*', help="items found in the room by default")
    args = parser.parse_args()

    name = args.name
    description = args.description
    items = args.item

    if args.north:
        north = args.north
        rooms.append(('north',north))
    if args.south:
        south = args.south
        rooms.append(('south',south))
    if args.east:
        east = args.east
        rooms.append(('east',east))
    if args.west:
        west = args.west
        rooms.append(('west',west))
    if args.up:
        up = args.up
        rooms.append(('up',up))
    if args.down:
        down = args.down
        rooms.append(('down',down))


    # Create the socket.  We will ask this to work on any interface and to use
    # the port given at the command line.  We'll print this out for clients to use.

    room_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    room_socket.bind(('', 0))

    sendRegister()

    # Report initial room state.
    print('Room Starting Description:\n')
    print_room_summary()

    print('\nRoom will wait for players at port: ' + str(room_socket.getsockname()[1]))

    # Loop forever waiting for messages from clients.

    while True:

        # Receive a packet from a client and process it.

        message, addr = room_socket.recvfrom(1024)

        # Process the message and retrieve a response.

        response = process_message(message.decode(), addr)

        # Send the response message back to the client.

        room_socket.sendto(response.encode(),addr)


if __name__ == '__main__':
    main()

