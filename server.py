import eventlet
import socketio
from random import choice

# Cop:0 Thief:1
pos = {0:[(330,110), (380,110) ], 1:[(680,110), (730,110)]}

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
    sio.emit('disconnect', to=sid)
    sio.emit('status', data, skip_sid=sid)
    print('disconnect ', sid)


@sio.event
def ready(sid):
    players[sid]['status'] = 2
    data = {'player': (sid, 2)}
    sio.emit('status', data)

    if list(map(lambda p:p['status'],players.values())).count(2) == 2:
        print('start')
        sio.emit('start', 1)

@sio.event
def move(sid, direction):
    data = {'player': (sid, direction)}
    sio.emit('move', data)

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