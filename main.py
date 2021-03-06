# TODO: add arrow count and limit the number of shots
# TODO: force game over when player runs out of arrows
# TODO: create a function to update the current room to get rid of some repeated code
# TODO: eventually refactor how the states are handled since only one thing can happen
# in the current room but multiple dangers can be nearby.

from random import randrange
from sys import exit

MIN_PLAYER_START = 16
MAX_PLAYER_START = 20
MIN_CROGNAC_START = 1
MAX_CROGNAC_START = 5
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
    def __init__(self, layout: tuple):
        self._cave = layout
        self._current_room = 0
        self._crognac_room = 0
        self._connected_rooms = [0]
        self._trap_locations = [0]
        self._bat_locations = [0]
        self._states = dict()
        self.new_game()
    
    def new_game(self):
        self._current_room = randrange(MIN_PLAYER_START, MAX_PLAYER_START+1)
        self._connected_rooms = self._cave[self._current_room]

        self._crognac_room = randrange(MIN_CROGNAC_START, MAX_CROGNAC_START+1)

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
        
    def get_updated_states(self):
        room = self._current_room
        traps = self._trap_locations
        bats = self._bat_locations

        self._states['trapped'] = self.player_in_danger(room, traps)
        self._states['trap_nearby'] = self.danger_nearby(self._connected_rooms, traps)
        self._states['bats'] = self.player_in_danger(room, bats)
        self._states['bats_nearby'] = self.danger_nearby(self._connected_rooms, bats)
        self._states['crognac'] = self.player_in_danger(self._current_room, [self._crognac_room])
        self._states['crognac_nearby'] = self.danger_nearby(self._connected_rooms, [self._crognac_room])

    def process_game(self):
        if self._states['trapped']:
            self.process_gameover()
        elif self._states['bats']:
            self.process_bats()
        elif self._states['crognac']:
            self.process_crognac()
        else:
            self.process_player()

    def process_player(self):
        action = get_player_command()

        if action == 'M':
            self.process_move()
        elif action == 'S':
            self.process_shoot()
        elif action == 'Q':
            exit()

    def process_move(self):
        room = get_int_value('Enter a room number')
        if not room:
            pass
        elif room not in self._connected_rooms:
            print(f'Room {room} is not a valid room')
        else:
            self._current_room = room
            self._connected_rooms = self._cave[room]
            self.get_updated_states()

    def process_shoot(self):
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
        
        if self._crognac_room in room_list:
            print("\nOW! Hey! You got me. I'll get you next time.")
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
        self._current_room = randrange(1, 21)
        self._connected_rooms = self._cave[self._current_room]
        self.get_updated_states()

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

    def player_in_danger(self, player_location, bad_rooms):
        return player_location in bad_rooms

    def danger_nearby(self, adjacent_rooms, bad_rooms):
        for i in range(len(bad_rooms)):
            if bad_rooms[i] in adjacent_rooms:
                return True
        return False


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