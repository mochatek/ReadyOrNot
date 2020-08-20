import eventlet
import socketio
from random import choice, shuffle

# Cop:0 Thief:1
pos = {0:[(330,110), (380,110) ], 1:[(680,110), (730,110)]}
items = {
    'item': ['W', 'C', 'PA', 'PH', 'B', 'L'],
    'pos': [(770, 430), (970, 435), (225, 640), (125, 455), (395, 690), (255, 480)]
    }

players = {}

sio = socketio.Server()
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print('connected', sid)

@sio.event
def disconnect(sid):
    del players[sid]
    data = {'player': (sid, 0)}
    sio.emit('status', data, skip_sid=sid)
    sio.emit('disconnect', to=sid)
    print('disconnect ', sid)


@sio.event
def ready(sid):
    players[sid]['status'] = 2
    data = {'player': (sid, 2)}
    sio.emit('status', data)

    if list(map(lambda p:p['status'],players.values())).count(2) == 2:
        shuffle(items['item'])
        shuffle(items['pos'])
        data = {'start': tuple(zip(items['item'], items['pos']))}
        sio.emit('gameStat', data)

@sio.event
def move(sid, data):
    sio.emit('move', data)

@sio.event
def item(sid, data):
    sio.emit('item', data)

@sio.event
def door(sid, data):
    sio.emit('door', data)

@sio.event
def join(sid, data):
    name, team =  data
    players[sid] = {
        'id': sid,
        'name': name,
        'life': 1,
        'tex': 0,
        'team': team,
        'status': 1,
        # 'pos': choice(pos[team])
        'pos': pos[0][0]
    }
    new = tuple(players[sid].values())
    data = {
        'you': new,
        'others': tuple(map(lambda id:tuple(players[id].values()) ,list(filter(lambda id: id != sid, players))))
    }
    sio.emit('init', data, to=sid) #send other players data to joined player

    data = {
        'player': new
    }
    sio.emit('newPlr', data, skip_sid=sid) #broadcast new player data

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)