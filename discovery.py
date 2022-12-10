import socket
import signal
import sys
import argparse
from urllib.parse import urlparse

PORT = 4444 #Discovery Service Port Number Constant


rooms = {} #Dictionary of Rooms, Mapping Names to Addresses

def process_message(message, addr):

    # Parse the message.
 
    words = message.split()

    if (words[0] == 'REGISTER'):
        roomAddress = words[1]
        roomName = words[2]
        if (roomName in rooms or roomAddress in rooms.values()):
            return 'NOTOK server with that name already exists.'
        elif(checkUrl(roomAddress)):
            rooms[roomName] = roomAddress
            print(f'REGISTERED Server - Name: {roomName} , Address: {roomAddress}')
            return 'OK'
        else:
            return 'NOTOK invalid server address.'


    elif (words[0] == 'DEREGISTER'):
        roomName = words[1]
        if (roomName in rooms):
            rooms.pop(roomName)
            print(f'DEREGISTERED Server - Name: {roomName}')
            return 'OK'
        else:
            return 'NOTOK server is not registered. Failed to delete server registration.'

    elif (words[0] == 'LOOKUP'):
        roomName = words[1]
        if (roomName in rooms):
            print(f'LOOKUP Server - Name: {roomName}')
            return f'OK {rooms[roomName]}'
        else:
            return 'NOTOK server not found.'
    else:
        return 'NOTOK invalid command.'

def checkUrl(url):
  
    server_address = urlparse(url)
    if ((server_address.scheme != 'room') or (server_address.port == None) or (server_address.hostname == None)):
        return False
    else:
        return True


def main():

    global discovery_socket

    # Create the socket.  We will ask this to work on any interface and to use
    # the port given at the command line.  We'll print this out for clients to use.

    discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discovery_socket.bind(('', PORT))
    print(f'Listening at PORT: {PORT}')

    # Loop forever waiting for messages from clients AND rooms.

    while True:

        # Receive a packet from a client or room and process it.

        message, addr = discovery_socket.recvfrom(1024)

        # Process the message and retrieve a response.

        response = process_message(message.decode(), addr)

        # Send the response message back to the client.

        discovery_socket.sendto(response.encode(),addr)


if __name__ == '__main__':
    main()