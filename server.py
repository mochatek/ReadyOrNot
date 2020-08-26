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
    global team_state

    sio.emit('status', [sid, 0, players[sid]['items']], skip_sid=sid) # notify others
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
    sio.emit('status', [sid, 2, []]) # notify all players

    # If every player is ready, then signal players to start game
    if list(map(lambda p:p['status'],players.values())).count(2) == 2:
        shuffle(items['item'])
        shuffle(items['pos'])
        data = [1] # status: [0: stop, 1: start]
        data.append(tuple(zip(items['item'], items['pos']))) # loot items
        sio.emit('gameState', data)

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
        sio.emit('meds', [sid, status], to=sid)
    else:
        meds_count -= 1
        status = meds_count
        players[sid]['life'] = 1
        sio.emit('meds', [sid, status])

# When player pickup or drop items.
# status: [0: drop, 1: pickup]
@sio.event
def item(sid, data):
    global players
    global team_state

    items = data[1]
    status = data[2]
    if status == 0: # drop
        item_id, is_loot = items[0]
        players[sid]['items'].remove(item_id)
        if is_loot == 1: # if lootable item, update game state
            team_state['items_count'][players[sid]['team']] -= 1
        data.append(team_state['items_count']) # send loot count also
        sio.emit('item', data)
    else: # pickup
        for item in items:
            item_id, is_loot = item
            players[sid]['items'].append(item_id)
            if is_loot == 1:
                team_state['items_count'][players[sid]['team']] += 1
        data.append(team_state['items_count'])
        sio.emit('item', data)

        winner_team = check_for_winner() # checking for game end
        if winner_team != -1:
            sio.emit('gameState', [0, winner_team])

# Open/clode door
@sio.event
def door(sid, data):
    sio.emit('door', data)

# Player escaped from jail
@sio.event
def escape(sid):
    global players
    global team_state

    players[sid]['jailed'] = False
    players[sid]['life'] = 1
    team_state['jailed_count'][players[sid]['team']] -= 1 # update game state
    sio.emit('jail', [0, sid, 0, 0]) # notify all players (status, player_id, position, items)

# Whenever a player attacks, update life
# if knocked down, send to jail
@sio.event
def attack(sid, data):
    global players
    global team_state

    if not players[sid]['jailed']:
        pid, pos, damage = data
        if pid in players: # not left
            players[pid]['life'] = max(0, round(players[pid]['life'] - damage, 1))
            if players[pid]['life'] == 0: # Got knocked down
                sio.emit('jail', [1, pid, pos, players[pid]['items']]) # send to jail
                players[pid]['jailed'] = True
                team_state['jailed_count'][players[sid]['team']] += 1 # update game state

                winner_team = check_for_winner() # checking for game end
                if winner_team != -1:
                    sio.emit('gameState', [0, winner_team])
            else:
                sio.emit('attack', [pid, players[pid]['life']])

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

    player = tuple(players[sid].values())[:4]
    data = [player, tuple(map(lambda id:tuple(players[id].values())[:4], filter(lambda id: id != sid, players)))]

    sio.emit('init', data, to=sid) #send player's and other players data to joined player

    sio.emit('newPlr', [player], skip_sid=sid) #broadcast new player data


# checks for the winner
# if winner found, then return winning team.
def check_for_winner():
    global team_state

    winner_team = -1
    if 6 in team_state['items_count']:
        winner_team = team_state['items_count'].index(4)
    elif 2 in team_state['jailed_count']:
        winner_team = (team_state['jailed_count'].index(1) + 1) % 2

    return winner_team



if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)