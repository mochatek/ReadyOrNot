import socketio

from _thread import start_new_thread
from textwrap import wrap

import arcade
from aim import Aim
from player import Player
from item import Item

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
SCALING = 0.25
TITLE = "Ready or Not ?"
SPEED = 0.75
MARGIN = 160
BAG_CAPACITY = 4

game = None

def setupNetwork(io):
    sio = io
    global game

    @sio.event
    def connect():
        print('connected')
        view = LobbyView(game.team, sio)
        game.window.show_view(view)

    @sio.event
    def init(data):
        id, name, life, tex, team, stat, pos = data['you']
        game.player = Player(id, name, life, tex, team, stat, pos)

        for player in data['others']:
            id, name, life, tex, team, stat, pos = player
            game.others.append(Player(id, name, life, tex, team, stat, pos))
        game.joined = True


    @sio.event
    def newPlr(data):
        id, name, life, tex, team, stat, pos = data['player']
        game.others.append(Player(id, name, life, tex, team, stat, pos))

    @sio.event
    def item(data):
        pid = data['item'][0]
        action = 'picked up'
        item_ids = data['item'][1]
        status = data['item'][2]
        names = []
        for id in item_ids:
            item = list(filter(lambda i: i.id == id, game.item_list))[0]
            item.taken = status
            if len(data['item']) == 4:
                item.position = data['item'][3]
                game.player.items.pop(game.player.items.index(id))
                action = 'dropped'
            else:
                game.player.items.append(id)
            names.append(item.name)
        if pid == game.player.id:
            names = ', '.join(names)
            names = wrap(names, 40)
            game.info = 'You {} {}'.format(action, '\n'.join(names))

    @sio.event
    def move(data):
        sid, position, direction = data['player']
        speed = {-1: (0, 0), 0: (0, SPEED), 1: (0, -SPEED), 2: (-SPEED, 0), 3: (SPEED, 0)}
        if game.player.id == sid:
            game.position = position
            game.player.change_x, game.player.change_y = speed[direction]
        else:
            player = list(filter(lambda p: p.id == sid, game.others))[0]
            player.position = position
            player.change_x, player.change_y = speed[direction]

    @sio.event
    def connect_error(err):
        game.msg = "Can't connect with server. Try again later."

    @sio.event
    def door(data):
        pid, door_id = data['door']
        door = list(filter(lambda d:d.properties['id'] == door_id, game.door_list))[0]
        if door.properties['locked'] == 0:
            door.properties['locked'] = 1
            game.block_list.append(door)
            if pid == game.player.id:
                game.info = 'You Locked the door.'
        else:
            door.properties['locked'] = 0
            game.block_list.remove(door)
            if pid == game.player.id:
                game.info = 'You Opened the door.'


    @sio.event
    def gameStat(data):
        if data.get('start', -1) != -1:
            items = data['start']
            view = GameView(game.io, game.player, game.others, items)
            game.window.show_view(view)

    @sio.event
    def status(data):
        while 1:
            if game.joined == True:
                sid, stat = data['player']
                if sid == game.player.id:
                    game.player.status = stat
                    game.statusText = 'Waiting for other players ...'
                else:
                    player = list(filter(lambda p: p.id == sid, game.others))[0]
                    if stat != 0:
                        player.status = stat
                    else:
                        game.others.remove(player)
                break


    @sio.event
    def disconnect():
        print('disconnected')
        msg = "Disconnected from server. Please connect again."
        view = ScreenView(msg)
        game.window.show_view(view)

    try:
        sio.connect('http://localhost:5000')
    except:
        game.msg = "Can't connect with server. Try again later."

# Initail game screen.
class ScreenView(arcade.View):
    def __init__(self, msg=None):
        super().__init__()
        global game
        game = self
        self.msg = msg
        self.bg = arcade.load_texture('res\screen.png')
        self.team = -1

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.bg)
        if self.msg:
            arcade.draw_text(self.msg, 110, 380, arcade.color.ANTIQUE_WHITE, 8, font_name=('Times New Roman'))


    def on_mouse_press(self, x, y, button, modifiers):
        # If player pressed setting button, show info.
        if 374 <= y <= 390 and 373 <= x <= 389:
            # Show settings and other info.
            view = InfoView()
            self.window.show_view(view)

        # Find team chosen by player.
        elif 120 <= y <= 136:
            if  96 <= x <= 141:
                self.team = 0
            elif 249 <= x <= 294:
                self.team = 1

        if self.team != -1:
            self.msg = 'Trying to connect with server. Please wait.'
            self.io = socketio.Client()
            start_new_thread(setupNetwork, (self.io, ))




# Settings and Credits.
class InfoView(arcade.View):
    def __init__(self):
        super().__init__()
        self.bg = arcade.load_texture('res\info.png')

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.bg)

    def on_key_press(self, symbol, modifiers):
        # Switch back to Load screen.
        if symbol == arcade.key.ESCAPE:
            view = ScreenView()
            self.window.show_view(view)


# Shows joined players and info.
class LobbyView(arcade.View):
    def __init__(self, team, io):
        super().__init__()
        self.joined = False #true once data has been updated in client
        global game
        game = self

        self.io = io
        self.bg = arcade.load_texture('res\lobby.png')

        self.others = arcade.SpriteList()
        self.item_list = arcade.SpriteList()

        # Request join.
        self.io.emit('join', ['mocha', team])

        # Message to be displayed below. (It is based on the game status)
        self.statusText = "Press R to Ready .."

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.bg)

        # Display game message.
        arcade.draw_text(self.statusText, 20, 15, arcade.color.WHITE, 10, bold=True)

        if self.joined:
            color = {1: arcade.color.WHITE, 2: arcade.color.GREEN}

            # Draw player and his name.
            file = self.player.file
            arcade.Sprite(file, 1, center_x=120, center_y=268).draw()
            arcade.draw_text(self.player.name, 200, 255, color[self.player.status], 12, bold=True)

            y = 268
            # sort_order = {0:False, 1:True}
            # for p in sorted(self.data, key = lambda x:x[6], reverse = sort_order.get(self.player.team)):
            for i in range(3):
                y = y - 50
                # Not joined or left.
                if i >= len(self.others):
                    arcade.Sprite('res\Players\inactive.png', 1, center_x=120, center_y=y).draw()
                    arcade.draw_text("Searching...", 200, y-12, arcade.color.WHITE_SMOKE, 12, bold=True)
                else:
                    file = self.others[i].file
                    arcade.Sprite(file, 1, center_x=120, center_y=y).draw()
                    arcade.draw_text(self.others[i].name, 200, y-10, color[self.others[i].status], 12, bold=True)


    def on_mouse_press(self, x, y, button, modifiers):
    # Go back to screen view.
        if 364 <= x <= 386 and  13 <= y <= 31:
            self.io.disconnect()

    def on_key_press(self, key, modifiers):
        if self.joined:
            if key == arcade.key.R:
                self.io.emit('ready')


class GameView(arcade.View):
    def __init__(self, io, player, others, items):
        super().__init__()
        global game
        game =  self
        self.io = io
        self.view_left = 0
        self.view_bottom = 0
        self.bg = arcade.load_texture('res\BG.png')
        # Reade tilemap and gather resources.
        map = arcade.read_tmx('res\map.tmx')
        # Spacial hashing increases speed in collission detection.
        self.block_list = arcade.SpriteList(use_spatial_hash=True, is_static=True)
        self.wall_list = arcade.process_layer(map, 'Wall', SCALING)
        self.block_list.extend(self.wall_list)
        # load objects.
        self.object_list = arcade.process_layer(map, 'Object', SCALING)
        self.block_list.extend(self.object_list)
        # Load FAB and Main switch.
        self.special_list = arcade.process_layer(map, 'Other', SCALING)
        self.block_list.extend(self.special_list)
        # Load doors.
        self.door_list = arcade.process_layer(map, 'Door', SCALING)
        self.block_list.extend(self.door_list)
        # Load Jails.
        self.jail_list = arcade.process_layer(map, 'Jail', SCALING)
        self.player = player
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.others = others

        self.item_list = arcade.SpriteList()
        self.load_items()
        id = 6
        for item in items:
            item_code, position = item
            self.item_list.append(Item(id, position, item_code))
            id += 1

        self.task = {0: "Theives inside. Catch everyone.", 1: "Loot Everything you can. (Be ware of Guards)"}
        # Set initial game message.
        self.info = self.task[self.player.team]
        # Initialize Aiming control.
        self.aim = Aim(self.player.position)
        # Physics engine for the game.
        self.physics = []
        self.physics.append(arcade.PhysicsEngineSimple(self.player, self.block_list))
        for player in self.others:
            self.physics.append(arcade.PhysicsEngineSimple(player, self.block_list))


    def on_draw(self):
        arcade.start_render()

        #self.floor_list.draw()
        arcade.draw_lrwh_rectangle_textured(0, 0, 1024, 832, self.bg)
        self.block_list.draw()

        self.jail_list.draw()
        self.item_list.draw()

        # Display player and all other players.
        self.player_list.draw()
        self.others.draw()

        # Display players with life and name.
        arcade.draw_xywh_rectangle_filled(self.player.left, self.player.top + 2, self.player.width * self.player.life, 3, arcade.color.GREEN)
        # arcade.draw_text(self.player.name, self.player.center_x - 12, self.player.center_y + 16, arcade.color.BLUE, 8)

        # Display others life and name based on team.
        for player in self.others:
            if player.team == self.player.team:
                arcade.draw_xywh_rectangle_filled(player.left, player.top + 2, player.width * player.life, 3, arcade.color.GREEN)
                arcade.draw_text(player.name, player.center_x - 12, player.center_y + 15, arcade.color.BLUE, 8, bold=True)
            else:
                arcade.draw_xywh_rectangle_filled(player.left, player.top + 2, player.width * player.life, 3, arcade.color.ROSE)
                arcade.draw_text(player.name, player.center_x - 12, player.center_y + 15, arcade.color.RED, 8, bold=True)

        # Display game message
        arcade.draw_xywh_rectangle_filled(self.view_left, self.view_bottom + 360, SCREEN_WIDTH, 40, arcade.color.BLACK)
        arcade.draw_text(self.info, self.view_left + 70, self.view_bottom + 380, arcade.color.GREEN_YELLOW, 10, bold = True)
        arcade.draw_text('Loot info here', self.view_left + 70, self.view_bottom + 365, arcade.color.BLUE, 10, bold = True)

        # Draw Aim control if player is hoding any weapon.
        if self.aim.type:
            self.aim.draw()


    def on_update(self, delta_time):
        for physics in self.physics:
            physics.update()
        self.player_list.update()
        self.others.update()
        self.item_list.update()

        items = arcade.check_for_collision_with_list(self.player, self.item_list)
        if items:
            items = list(filter(lambda i: not i.taken, items))
            if len(items) > 0:
                self.info = items[0].info
            else:
                if not self.info.startswith('You'):
                    self.info = self.task[self.player.team]
        else:
            if not self.info.startswith('You'):
                self.info = self.task[self.player.team]

        # Update Viewport based on player movement.
        self.scroll_screen()

    def load_items(self):
        self.item_list.append(Item(0, (400,82), 'YELLOW'))
        self.item_list.append(Item(1, (620, 82), 'RED'))
        self.item_list.append(Item(2, (110, 370), 'BLUE'))
        self.item_list.append(Item(2, (400, 495), 'BLUE'))
        self.item_list.append(Item(3, (95, 675), 'GREEN'))
        self.item_list.append(Item(3, (815, 690), 'GREEN'))
        self.item_list.append(Item(4, (80, 305), 'K'))
        self.item_list.append(Item(4, (205, 305), 'K'))
        self.item_list.append(Item(4, (820, 305), 'K'))
        self.item_list.append(Item(4, (940, 305), 'K'))
        self.item_list.append(Item(5, (910, 585), 'G'))
        self.item_list.append(Item(5, (970, 555), 'G'))
        self.item_list.append(Item(5, (110, 585), 'G'))
        self.item_list.append(Item(5, (60, 585), 'G'))

    # Scrolling screen according to player movement.
    def scroll_screen(self):
        changed = False
        # Scroll Left
        left_boundary = self.view_left + MARGIN
        if self.player.left < left_boundary:
            self.view_left -= left_boundary - self.player.left
            changed = True

        # Scroll Right
        right_boundary = self.view_left + SCREEN_WIDTH - MARGIN
        if self.player.right > right_boundary:
            self.view_left += self.player.right - right_boundary
            changed = True

        # Scroll Top
        top_boundary = self.view_bottom + SCREEN_HEIGHT - MARGIN
        if self.player.top > top_boundary:
            self.view_bottom += self.player.top - top_boundary
            changed = True

        # Scroll Bottom
        bottom_boundary = self.view_bottom + MARGIN
        if self.player.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player.bottom
            changed = True

        # Vieport uses int, claculated values can be float.
        self.view_left = int(self.view_left)
        self.view_bottom = int(self.view_bottom)
        if changed == True:
            arcade.set_viewport(self.view_left, self.view_left + SCREEN_WIDTH, self.view_bottom, self.view_bottom + SCREEN_HEIGHT)


    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.D and self.player.change_x != SPEED:
            self.io.emit('move', {'move': (self.player.position, 3)})
        elif symbol == arcade.key.A and self.player.change_x != -SPEED:
            self.io.emit('move', {'move': (self.player.position, 2)})
        elif symbol == arcade.key.W and self.player.change_y != SPEED:
            self.io.emit('move', {'move': (self.player.position, 0)})
        elif symbol == arcade.key.S and self.player.change_y != -SPEED:
            self.io.emit('move', {'move': (self.player.position, 1)})
        elif symbol == arcade.key.SPACE and (self.player.change_x + self.player.change_y) != 0:
            self.io.emit('move', {'move': (self.player.position, -1)})


        elif symbol == arcade.key.CAPSLOCK:
            inventory = len(self.player.items)
            if inventory < BAG_CAPACITY:
                items = arcade.check_for_collision_with_list(self.player, self.item_list)
                if items:
                    items = list(filter(lambda i: not i.taken, items))
                    if len(items) > 0:
                        pickups = []
                        for item in items:
                            if inventory < BAG_CAPACITY:
                                if item.id not in self.player.items:
                                    pickups.append(item.id)
                                    inventory += 1
                                else:
                                    self.info = "You already have it with you. Can't pick up again !"
                            else:
                                self.info = 'Your inventory is full ! [ MAX: 4 items ]'

                        self.io.emit('item', {'item': (self.player.id, pickups, 1)})
            else:
                self.info = 'Your inventory is ful1 ! [ MAX: 4 items ]'


        elif symbol == arcade.key.F:
            if len(self.player.items) == 0:
                self.info = 'Your inventory is empty !'
            else:
                drop = self.player.items[-1]
                self.io.emit('item', {'item': (self.player.id, [drop], 0, self.player.position)})


        elif symbol == arcade.key.E:
            doors = arcade.check_for_collision_with_list(self.player, self.door_list)
            if len(doors) > 0:
                key = list(filter(lambda i:i.code == doors[0].properties['key'], self.item_list))[0]
                if key.id in self.player.items:
                    self.io.emit('door', {'door': (self.player.id, doors[0].properties['id'])})
                else:
                    self.info = 'You need {} to access this door.'.format(key.name)


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    # Show initial game load screen.
    view = ScreenView()
    window.show_view(view)
    arcade.run()


if __name__ == '__main__':
    main()
