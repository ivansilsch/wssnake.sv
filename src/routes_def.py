class EventRouterBaseClass:
    """Defines the websocket events. 
    Reads its own declared methods with dir() and creates a factory object to call them.
    """

    def __init__(self):

        self.routes = [
            method for method in dir(self)
            if not method.startswith("__")
        ]

    async def call(self, method, client=None, data=None):

        if not method:
            await getattr(self, "void")(client, data)

        for route in self.routes:
            if route == method:
                callable = getattr(self, route)
                await callable(client, data)
