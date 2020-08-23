import eventlet
import socketio
from random import shuffle
from _thread import start_new_thread

# Cop:0 Thief:1
pos = {0:[(330,110), (380,110) ], 1:[(680,110), (730,110)]}
items = {
    'item': ['W', 'C', 'PA', 'PH', 'B', 'L'],
    'pos': [(770, 430), (970, 435), (225, 640), (125, 455), (395, 690), (255, 480)]
    }
meds_count = 8
team_state = {0:{'jailed_count': 0, 'items_count': 0},
            1:{'jailed_count': 0, 'items_count': 0}}
players = {}

sio = socketio.Server()
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print('connected', sid)

@sio.event
def disconnect(sid):
    global players
    global meds_count
    data = {'player': (sid, 0, players[sid]['items'])}
    sio.emit('status', data, skip_sid=sid)
    sio.emit('disconnect', to=sid)
    del players[sid]
    if not players:
        meds_count = 8
    print('disconnect ', sid)


@sio.event
def ready(sid):
    global players
    global items
    players[sid]['status'] = 2
    data = {'player': (sid, 2, [])}
    sio.emit('status', data)

    if list(map(lambda p:p['status'],players.values())).count(2) == 2:
        shuffle(items['item'])
        shuffle(items['pos'])
        data = {'start': tuple(zip(items['item'], items['pos']))}
        sio.emit('gameStat', data)
        start_new_thread(find_winner, (sio, ))

@sio.event
def move(sid, data):
    sio.emit('move', data)

@sio.event
def meds(sid):
    global meds_count
    global players
    if meds_count == 0:
        status = 0
        sio.emit('meds', {'meds': (sid, status)}, to=sid)
    else:
        meds_count -= 1
        status = meds_count
        players[sid]['life'] = 1
        sio.emit('meds', {'meds': (sid, status)})

@sio.event
def item(sid, data):
    global players
    if not players[sid]['jailed']:
        items = data['item'][1]
        status = data['item'][2]
        if status == 0:
            players[sid]['items'].pop(players[sid]['items'].index(items[0]))
            team_state[players[sid]['team']]['items_count'] -= 1
        else:
            for item in items:
                players[sid]['items'].append(item)
                team_state[players[sid]['team']]['items_count'] += 1
        sio.emit('item', data)

@sio.event
def door(sid, data):
    sio.emit('door', data)

@sio.event
def escape(sid):
    global players
    data = {'jail': (0, sid, 0, 0)}
    players[sid]['jailed'] = False
    players[sid]['life'] = 1
    team_state[players[sid]['team']]['jailed_count'] -= 1
    sio.emit('jail', data)

@sio.event
def attack(sid, data):
    global players
    if not players[sid]['jailed']:
        pid, pos, damage = data['hits']
        if pid in players: #not left
            players[pid]['life'] = max(0, players[pid]['life'] - damage)
            if players[pid]['life'] == 0:
                sio.emit('jail', {'jail': (1, pid, pos, players[pid]['items'])})
                players[pid]['jailed'] = True
                team_state[players[pid]['team']]['jailed_count'] += 1
            else:
                sio.emit('attack', {'hits': (pid, players[pid]['life'])})

@sio.event
def join(sid, data):
    global players
    name, team =  data
    players[sid] = {
        'id': sid,
        'name': name,
        'team': team,
        'pos': pos[0][0],
        'status': 1,
        'life': 1,
        'items': [],
        'jailed': False
    }
    new = tuple(players[sid].values())[:4]
    data = {
        'you': new,
        'others': tuple(map(lambda id:tuple(players[id].values())[:4], filter(lambda id: id != sid, players)))
    }
    sio.emit('init', data, to=sid) #send other players data to joined player

    data = {
        'player': new
    }
    sio.emit('newPlr', data, skip_sid=sid) #broadcast new player data


def find_winner(sio):
    global team_state
    while 1:
        winner_team = -1
        items_count = [team_state[0]['items_count'], team_state[1]['items_count']]
        if 4 in items_count:
            winner_team = items_count.index(4)
        else:
            jailed_count = [team_state[0]['jailed_count'], team_state[1]['jailed_count']]
            if 1 in jailed_count:
                winner_team = (jailed_count.index(1) + 1) % 2
        if winner_team != -1:
            sio.emit('gameStat', {'stop': winner_team})
            team_state = {0:{'jailed_count': 0, 'items_count': 0},
                        1:{'jailed_count': 0, 'items_count': 0}}
            break



if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)