Gameplay

Hunt for Crognak is a clone of the game "Hunt The Wumpus" where you
must kill a creature hidden inside a cave while avoiding the dangers
of the cave.

Crognak is a grotesque orcish being that has been responsible for
the deaths of many villagers and travelling merchants. He has been
tracked to a local cave and you have been sent to dispense of him.
The cave is made of 20 rooms each connected to three other rooms 
in the shape of a dodecahedron.

Beware though as Crognak has a few tricks up his sleaves. There are
traps and pitfalls as well as mysterious beings that can control your
mind and move you toward danger.

Crognak moves about the cave in the same way that you do. However, he
knows which rooms to avoid. If he enters the room after your movement
then he will kill you. If you manage to sneak up on him he is likely to flee,
but he may also kill you on the spot.

The only way to kill Crognak is to shoot one of your five magic arrows.
When you fire your arrow you can move it through 1 to 5 rooms in search
of Crognak. The rooms must be connected to each other. If your path includes
rooms that are not connected to your path then your arrow's path will be chosen
at random

Implementation Details

The Map is an array of 20 elements.
Each element represents a room.
Each element also contains a tuple of 3 integers from 0-19 that represent
the rooms connected to the current room. see the image for layout of the rooms

Two numbers from 0-19 (inclusive) are chosen at random to contain the trap positions.

Two more numbers are chosen at random to contain the positions for the mysterious
beings.

The player starts in one of the five outer rooms and Crognak starts in one
of the five inner rooms

