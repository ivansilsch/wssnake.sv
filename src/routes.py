import websockets
import json
import storage

from routes_def import EventRouterBaseClass


def broadcast_games():
    """Updates the games list to other users"""
    games_data = [
        dict(id=game["id"], players=len(game["players"]))
        for game in storage.games
    ]
    games = json.dumps(games_data)
    payload = dict(state="games-updated", games=games)
    websockets.broadcast(storage.clients.values(), json.dumps(payload))


class EventRouter(EventRouterBaseClass):
    """Defines the websocket events"""

    async def connect(self, client, data):
        """First connection test"""
        payload = dict(state="connected")
        await client.send(json.dumps(payload))
        # websockets.broadcast(storage.clients.values(), json.dumps(payload))

    async def login(self, client, data):

        """Saves the client websocket and nickname as id"""
        nickname = data["nickname"]
        if nickname in storage.clients.keys():
            payload = dict(state="already-logged")
            await client.send(json.dumps(payload))
        else:
            storage.clients[nickname] = client
            payload = dict(state="logged")
            await client.send(json.dumps(payload))
            broadcast_games()

    async def join(self, client, data):
        """Adds the player to the players data"""

        # Initial values of the player
        nickname = data.get("nickname")
        game_id = data.get("gameID")
        position = dict(x=0, y=0)
        player = dict(position=position)

        # Register the player to the selected game
        for index, game in enumerate(storage.games):
            if game.get("id") == game_id:
                storage.games[index]["players"][nickname] = player

        payload = dict(state="joined", gameID=game_id)
        await client.send(json.dumps(payload))
        broadcast_games()

        # send_update_joined_game(game_id)

    async def move(self, client, data):
        game_id = data.get("gameID")
        nickname = data.get("nickname")
        position = data.get("position")
        index_game = None

        for ig, game in enumerate(storage.games):
            found = game_id == game["id"]
            if found:
                index_game = ig
                storage.games[ig]["players"][nickname]["position"] = position

        # Broadcast the current game
        game = storage.games[index_game]
        payload = dict(state="moved", game=game)
        websockets.broadcast(storage.clients.values(), json.dumps(payload))

    async def void(self, client, data):
        """Handles a message with an invalid structure"""
        payload = dict(state="void", message="No method defined")
        await client.send(json.dumps(payload))

    async def disconnect(self, client, data):
        """Handles the connection loss of a client"""

        # Removes the disconnected websocket
        key = storage.get_client_key(client)
        if key:
            client = storage.clients.get(key)
            if client:
                del storage.clients[key]

            # Removes the disconnected player from the game
            storage.remove_player(key)

        broadcast_games()
