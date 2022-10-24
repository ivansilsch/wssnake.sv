import random


clients = dict()

pointer_id = 0


def get_client_key(client):
    for nickname in clients.keys():
        if (client == clients.get(nickname)):
            return nickname


def create_ID(size):
    return "".join(chr(random.randint(48, 122)) for i in range(0, size))


games = [
    dict(id=create_ID(6), players={})
]


def remove_player(nickname):
    """Removes the disconnected player from the game"""
    for game in games:
        player = game["players"].get(nickname)
        if player:
            del game["players"][nickname]
