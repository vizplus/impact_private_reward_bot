from viz import Client
from pprint import pprint

node = 'wss://node.viz.cx/ws'
# node = 'https://api.viz.world/'

viz = Client(node=node)
pprint(viz.info())
