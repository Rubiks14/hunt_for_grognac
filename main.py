# TODO: eventually refactor how the states are handled since only one thing can happen
# in the current room but multiple dangers can be nearby
# TODO: Find a better name for the pick_rooms function that better describes what it is
# actually doing
# TODO: Allow crognac to move about the map.
# TODO: Change the behavior of the bats so that they move the player closer to danger
# instead of dropping them in a random room.

from random import randrange
from sys import exit

MIN_PLAYER_START = 16
MAX_PLAYER_START = 20
MIN_CROGNAC_START = 1
MAX_CROGNAC_START = 15
MAX_ARROW_COUNT = 2
CROGNAC_ATTACK_CHANCE = 75
CAVE = (
    (0, 0, 0),
    (2, 5, 8),
    (1, 3, 10),
    (2, 4, 12),
    (3, 5, 14),
    (1, 4, 6),
    (5, 7, 15),
    (6, 8, 17),
    (1, 7, 9),
    (8, 10, 18),
    (2, 9, 11),
    (10, 12, 19),
    (3, 11, 13),
    (12, 14, 20),
    (4, 13, 15),
    (6, 14, 16),
    (15, 17, 20),
    (7, 16, 18),
    (9, 17, 19),
    (11, 18, 20),
    (13, 16, 19)
)


class Game:
    def __init__(self, layout: tuple) -> None:
        self._cave = layout
        self._current_room = 0
        self._crognac_room = 0
        self._arrow_count = 0
        self._connected_rooms = [0]
        self._trap_locations = [0]
        self._bat_locations = [0]
        self._states = dict()
        self.new_game()
    
    def new_game(self) -> None:
        self._current_room = randrange(MIN_PLAYER_START, MAX_PLAYER_START+1)
        self._connected_rooms = self._cave[self._current_room]

        self._crognac_room = randrange(MIN_CROGNAC_START, MAX_CROGNAC_START+1)

        self._arrow_count = MAX_ARROW_COUNT

        occupied_rooms = {self._current_room, self._crognac_room}

        while True:
            if len(self._trap_locations) < 2 or \
            occupied_rooms.intersection(self._trap_locations):
                self._trap_locations = self.pick_rooms(2)
            elif len(self._bat_locations) < 2 or \
            occupied_rooms.intersection(self._bat_locations):
                self._bat_locations = self.pick_rooms(2)
            else:
                break

        self.get_updated_states()
        self.process_help()
    
    def process_help(self) -> None:
        answer = input("Would you like to see the instructions? (Y/N): ")
        if answer.upper() == 'Y':
            display_instructions()

    def change_room(self, new_room) -> None:
        self._current_room = new_room
        self._connected_rooms = self._cave[self._current_room]
        self.get_updated_states()
        
    def get_updated_states(self) -> None:
        room = self._current_room
        traps = self._trap_locations
        bats = self._bat_locations

        self._states['trapped'] = self.player_in_danger(room, traps)
        self._states['trap_nearby'] = self.danger_nearby(self._connected_rooms, traps)
        self._states['bats'] = self.player_in_danger(room, bats)
        self._states['bats_nearby'] = self.danger_nearby(self._connected_rooms, bats)
        self._states['crognac'] = self.player_in_danger(self._current_room, [self._crognac_room])
        self._states['crognac_nearby'] = self.danger_nearby(self._connected_rooms, [self._crognac_room])

    def process_game(self) -> None:
        if self._states['trapped']:
            self.process_gameover()
        elif self._states['bats']:
            self.process_bats()
        elif self._states['crognac']:
            self.process_crognac()
        else:
            self.process_player()

    def process_player(self) -> None:
        action = get_player_command()

        if action == 'M':
            self.process_move()
        elif action == 'S':
            self.process_shoot()
        elif action == 'Q':
            exit()

    def process_move(self) -> None:
        room = get_int_value('Enter a room number')
        if not room:
            pass
        elif room not in self._connected_rooms:
            print(f'Room {room} is not a valid room')
        else:
            self.change_room(room)

    def process_shoot(self) -> None:
        num_rooms = get_int_value('Number of rooms? (1-5)')
        num_rooms = 1 if not num_rooms else num_rooms
        room_list = []
        current_room = self._current_room

        for i in range(num_rooms):
            room = get_int_value('Enter a room number')

            if room not in self._cave[current_room]:
                room = self._cave[current_room][randrange(0, 3)]

            room_list.append(room)
            current_room = room
        
        self._arrow_count -= 1
        print(f"You fire an arrow. You have {self._arrow_count} arrows left.")

        if self._current_room in room_list:
            print("\nThe arrow whizzes into the room and strikes you in the chest.")
            print("Crognac enters the room and says 'I can't believe you shot yourself! BAHAHAHA!'")
            self.process_gameover()
        elif self._crognac_room in room_list:
            print("\nOW! Hey! You got me. I'll get you next time.")
            self.process_gameover()
        elif self._arrow_count <= 0:
            print("\nYou have run out of arrows. There is no way to defeat Crognac now.")
            self.process_gameover()  
        
    def process_crognac(self) -> None:
        attack_chance = randrange(0, 100)
        if attack_chance >= CROGNAC_ATTACK_CHANCE:
            print("\nCrognac has noticed you.")
            print("He turns around and shout 'AHA! Now you Die!'")
            print("With one swift motion he cleaves your head off")

            self.process_gameover()
        else:
            print("\nCrognac notices your approach and flees")
            
            self._crognac_room = self._connected_rooms[randrange(0, 3)]

            self.get_updated_states()

    def process_bats(self) -> None:
        self.change_room(randrange(1, 21))

    def process_gameover(self) -> None:
        while True:
            restart = input('\nWould you like to play again? (Y, N): ')
            if restart.upper() == 'Y':
                self.new_game()
                break
            elif restart.upper() == 'N':
                print("See you later!")
                exit()
            else:
                print("That is not a valid option")

    def pick_rooms(self, num_rooms: int) -> tuple:
        rooms = []
        while len(rooms) < num_rooms:
            pick = randrange(1, 21)
            if pick not in rooms:
                rooms.append(pick)
        return tuple(rooms)

    def player_in_danger(self, player_location: tuple, bad_rooms: tuple) -> bool:
        return player_location in bad_rooms

    def danger_nearby(self, adjacent_rooms: tuple, bad_rooms: tuple) -> bool:
        for i in range(len(bad_rooms)):
            if bad_rooms[i] in adjacent_rooms:
                return True
        return False


def display_instructions() -> None:
    print("\nCrognak is a grotesque orcish being that has been responsible for " +
        "the deaths of many villagers and travelling merchants. He has been " +
        "tracked to a local cave and you have been sent to dispense of him. " +
        "The cave is made of 20 rooms each connected to three other rooms " +
        "in the shape of a dodecahedron.\n\n" +
        "Beware though as Crognak has a few tricks up his sleaves. There are " +
        "traps and pitfalls as well as mysterious beings that can control your " +
        "mind and move you toward danger.\n\n" +
        "Crognak moves about the cave in the same way that you do. However, he " +
        "knows which rooms to avoid. If he enters the room after your movement " +
        "then he will kill you. If you manage to sneak up on him he is likely to flee, " +
        "but he may also kill you on the spot.\n\n" +
        "The only way to kill Crognak is to shoot one of your five magic arrows. " +
        "When you fire your arrow you can move it through 1 to 5 rooms in search " +
        "of Crognak. The rooms must be connected to each other. If your path includes " +
        "rooms that are not connected to your path then your arrow's path will be chosen " +
        "at random")


def display_room(room, connected_rooms, states: dict) -> None:
    print(f'\nYou stand in room {room}')
    rooms_str = ' '.join(map(str, connected_rooms))
    print(f'Tunnels lead to {rooms_str}')

    if states['trapped']:
        print(f'AAAAAAHHHH! You have fallen into a pitfall.')
    elif states['trap_nearby']:
        print('You feel a draft from a nearby pitfall')

    if states['bats']:
        print(f"*SCREEEEECH* What is happenin? A bat is carrying you off")
    elif states['bats_nearby']:
        print(f"You hear bats screaching nearby")

    if states['crognac']:
        print(f"Crognac stands before you")
    elif states['crognac_nearby']:
        print(f"You smell an orc")


def get_player_command() -> str:
    print('\nWhat would you like to do? (M - move, S - shoot)')
    action = input('Or type \'Q\' to quit: ')
    
    if action.upper() not in ('M', 'S', 'Q'):
        print('I do not understand your action')
        return 'N'
    else:
        return action.upper()


def get_int_value(prompt: str) -> int:
    room = input(f'{prompt}: ')

    if room.isnumeric():
        return int(room)
    else:
        print(f'{room} is not a number')
        return None


def main():  
    game = Game(CAVE)

    while True:
        display_room(game._current_room, game._connected_rooms, game._states)
        game.process_game()


if __name__ == "__main__":
    main()