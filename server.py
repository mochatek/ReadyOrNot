import eventlet
import socketio
from random import shuffle

# Cop:0 Thief:1
pos = {0:[(330,110), (380,110) ], 1:[(680,110), (730,110)]}

# Loot items
items = {
    'item': ['W', 'C', 'PA', 'PH', 'B', 'L'],
    'pos': [(770, 430), (970, 435), (225, 640), (125, 455), (395, 690), (255, 480)]
    }

# Number of medicines remaining
meds_count = 8

# State to determine game end. (winner)
team_state = {'jailed_count': [0, 0], 'items_count': [0, 0]}

# Players in game
players = {}

sio = socketio.Server()
app = socketio.WSGIApp(sio)

# When player is connected
@sio.event
def connect(sid, environ):
    print('connected', sid)

# When any player disconenct from server:
# notify others about leaving with (player_id, ids of items he had [for dropping])
@sio.event
def disconnect(sid):
    global players
    global meds_count

    data = {'player': (sid, 0, players[sid]['items'])}
    sio.emit('status', data, skip_sid=sid) # notify others
    sio.emit('disconnect', to=sid) # terminate connection

    del players[sid] # remove data

    # If it was the last player, then reset game data
    if not players:
        meds_count = 8
        team_state = {'jailed_count': [0, 0], 'items_count': [0, 0]}
    print('disconnect ', sid)

# When player says he is ready to play
@sio.event
def ready(sid):
    global players
    global items

    players[sid]['status'] = 2
    data = {'player': (sid, 2, [])}
    sio.emit('status', data) # notify all players

    # If every player is ready, then signal players to start game
    if list(map(lambda p:p['status'],players.values())).count(2) == 2:
        shuffle(items['item'])
        shuffle(items['pos'])
        data = {'start': tuple(zip(items['item'], items['pos']))}
        sio.emit('gameStat', data)

# Player Movement
@sio.event
def move(sid, data):
    sio.emit('move', data)

# Toggling lights
@sio.event
def light(sid, flag):
    sio.emit('light', flag)

# When player try to take medicines
@sio.event
def meds(sid):
    global meds_count
    global players

    if meds_count == 0: # Nothing left
        status = 0
        sio.emit('meds', {'meds': (sid, status)}, to=sid)
    else:
        meds_count -= 1
        status = meds_count
        players[sid]['life'] = 1
        sio.emit('meds', {'meds': (sid, status)})

# When player pickup or drop items.
# status: [0: drop, 1: pickup]
@sio.event
def item(sid, data):
    global players
    global team_state

    if not players[sid]['jailed']: # confirm not in jail
        items = data['item'][1]
        status = data['item'][2]
        if status == 0: # drop
            item_id, is_loot = items[0]
            players[sid]['items'].remove(item_id)
            if is_loot == 1: # if lootable item, update game state
                team_state['items_count'][players[sid]['team']] -= 1
        else: # pickup
            for item in items:
                item_id, is_loot = item
                players[sid]['items'].append(item_id)
                if is_loot == 1:
                    team_state['items_count'][players[sid]['team']] += 1
        sio.emit('item', data)

# Open/clode door
@sio.event
def door(sid, data):
    sio.emit('door', data)

# Player escaped from jail
@sio.event
def escape(sid):
    global players
    global team_state

    data = {'jail': (0, sid, 0, 0)} # (status, player_id, position, items)
    players[sid]['jailed'] = False
    players[sid]['life'] = 1
    team_state['jailed_count'][players[sid]['team']] -= 1 # update game state
    sio.emit('jail', data) # notify all players

# Whenever a player attacks, update life
# if knocked down, send to jail
@sio.event
def attack(sid, data):
    global players
    global team_state

    if not players[sid]['jailed']:
        pid, pos, damage = data['hits']
        if pid in players: #not left
            players[pid]['life'] = max(0, players[pid]['life'] - damage)
            if players[pid]['life'] == 0: # Got knocked down
                sio.emit('jail', {'jail': (1, pid, pos, players[pid]['items'])}) # send to jail
                players[pid]['jailed'] = True
                team_state['jailed_count'][players[sid]['team']] += 1 # update game state
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


# finding the winner
# if winner found, then issue game end.
def find_winner(sio):
    global team_state

    while 1:
        winner_team = -1
        if 4 in team_state['items_count']:
            winner_team = team_state['items_count'].index(4)
        elif 1 in team_state['jailed_count']:
            winner_team = (team_state['jailed_count'].index(1) + 1) % 2
        if winner_team != -1:
            sio.emit('gameStat', {'stop': winner_team})
            team_state = {'jailed_count': [0, 0], 'items_count': [0, 0]}
            break



if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)