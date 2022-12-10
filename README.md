# Python-Client-Server-Text-Adventure-Game
Python Client-Server text adventure game using python UDP sockets
Each room is a server and each client is a player. Rooms can be connected to each other so players can move freely between servers. Rooms have starting descriptions as well as items inside. Players have their own inventory, can move between rooms, can look around in rooms, can pick up items in a room, can drop items into a room, and can say things and all other clients in the same room will hear what they say.

Commands available to player (Client):
 - say sayWhatYouWantHere
 - look (to get a description of the room you are currently in)
 - pickup itemName
 - drop itemName
 - nort/south/east/west/up/down (if there is a room in the typed direction, the player will move from its current room to that room)
 - exit (to exit the game)


There are three python files: discovery.py , room.py (sever) and player.py (client)

FIRST RUN THE DISCOVERY SERVICE LIKE THIS:

python3 discovery.py


SECOND RUN THE SERVERS (ROOMS) USING FORMAT:

python3 room.py -n name -s name -e name -w name -u name -d name "roomName" "RoomDescription" items  ( WHERE the -n -s -e -w -u -d are optional to specify rooms in other directions, they must be followed by their name)
Example Usage for room.py (Server) this will create 2 rooms (servers) that are linked to each other. One in the south and one in the north.

	python3 room.py -n "NorthRoom" "MainRoom" "The Main Room, there is a door to the North" "vase" "sword" "shield"
	python3 room.py -s "MainRoom" "NorthRoom" "The Northern Room, there is a door to the South" "flowers" "coins"

THIRD RUN CLIENTS USING FORMAT:

python3 player.py playerName roomName

Example Usage for player.py (Client)

	python3 player.py Zach MainRoom



use command north/south/east/west/up/down to move between rooms if there are rooms
