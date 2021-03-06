"""
LIB Changes
___________
easygui > boxes > multi_fillable_box.py > class GUItk > __init__() : Line 272 = self.set_pos('300x200+300+200')
pyglet > gl > lib.py > errcheck() > Line 108 = #raise GLException(msg)
"""

import socketio
from random import randrange
from textwrap import wrap

import arcade
from arcade.experimental.lights import Light, LightLayer

from aim import Aim
from player import Player
from item import Item
from blood import Blood
from config import Config

import os

#########################################################################################################################


SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
SCALING = 0.25
TITLE = "Ready or Not ?"
SPEED = 0.75
MARGIN = 160
BAG_CAPACITY = 4
AMBIENT_COLOR = (10, 10, 10)

game = None
config = Config()

#########################################################################################################################


# Home screen.
class HomeView(arcade.View):
    def __init__(self, io, msg=None, light_layer=None):
        super().__init__()
        global game

        self.io = io
        self.msg = msg
        self.team = -1 # [0:Guards, 1: Thief]
        self.lock = False # [True: once connected to server]
        self.light_layer = light_layer

        self.bg = arcade.load_texture('res\screen.png')
        self.click_sound = arcade.load_sound('res\sound\click.mp3')

    def on_draw(self):
        arcade.start_render()
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        self.light_layer.draw()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.bg)
        if self.msg:
            arcade.draw_text(self.msg, 110, 380, arcade.color.ANTIQUE_WHITE, 8, font_name=('Times New Roman'))

    def on_mouse_press(self, x, y, button, modifiers):
        # Click on setting button.
        if 374 <= y <= 390 and 373 <= x <= 389:
            arcade.play_sound(self.click_sound, 0.15)
            view = SettingsView(self.io, self.light_layer)
            self.window.show_view(view)

        # Choosing team.
        elif 120 <= y <= 136:
            if  96 <= x <= 141:
                arcade.play_sound(self.click_sound, 0.15)
                self.team = 0
            elif 249 <= x <= 294:
                arcade.play_sound(self.click_sound, 0.15)
                self.team = 1

        # Check whether any team was selected.
        if self.team != -1 and not self.lock:
            global game
            self.msg = 'Trying to connect with server. Please wait.'
            game = self
            try:
                # Get player name and host IP from user input
                config.getConfigFromUser()

                self.io.connect(f'http://{config.host}:5000')
            except Exception as e:
                print(e)
                msg = "Can't connect with server. Try again later."
                self.team = -1
                self.lock = False


#########################################################################################################################


# Settings and Credits.
class SettingsView(arcade.View):
    def __init__(self, io, light_layer):
        super().__init__()
        self.io = io
        self.light_layer = light_layer

        self.bg = arcade.load_texture('res\info.png')
        self.click_sound = arcade.load_sound('res\sound\click.mp3')

    def on_draw(self):
        arcade.start_render()
        self.light_layer.draw()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.bg)

    def on_key_press(self, symbol, modifiers):
        # Switch back to home screen.
        if symbol == arcade.key.ESCAPE:
            arcade.play_sound(self.click_sound, 0.15)
            view = HomeView(self.io, None, self.light_layer)
            self.window.show_view(view)


#########################################################################################################################


# Shows joined players and info.
class LobbyView(arcade.View):
    def __init__(self, team, io, light_layer):
        super().__init__()
        self.joined = False # [True: once data from server has been assigned in client]
        global game

        game = self
        self.io = io
        self.statusText = "Press R to Ready .."
        self.light_layer = light_layer

        self.bg = arcade.load_texture('res\lobby.png')
        self.click_sound = arcade.load_sound('res\sound\click.mp3')
        self.others = arcade.SpriteList()
        self.item_list = arcade.SpriteList()

        # Request to join game.
        self.io.emit('join', [config.name, team])

    def on_draw(self):
        arcade.start_render()
        self.light_layer.draw()

        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.bg)
        arcade.draw_text(self.statusText, 20, 15, arcade.color.WHITE, 10, bold=True)

        if self.joined:
            color = {1: arcade.color.WHITE, 2: arcade.color.GREEN}

            # Draw player and his name.
            file = self.player.file
            arcade.Sprite(file, 1, center_x=120, center_y=268).draw()
            arcade.draw_text(self.player.name, 200, 255, color[self.player.status], 12, bold=True)

            # Draw other players and name.
            y = 268
            for i in range(3):
                y = y - 50
                # Not joined or left.
                if i >= len(self.others):
                    arcade.Sprite('res\Players\inactive.png', 1, center_x=120, center_y=y).draw()
                    arcade.draw_text("Searching...", 200, y-12, arcade.color.WHITE_SMOKE, 12, bold=True)
                else:
                    try:
                        file = self.others[i].file
                        arcade.Sprite(file, 1, center_x=120, center_y=y).draw()
                        arcade.draw_text(self.others[i].name, 200, y-10, color[self.others[i].status], 12, bold=True)
                    except Exception as e:
                        print(e)

    def on_mouse_press(self, x, y, button, modifiers):
        # Go back to home.
        if 364 <= x <= 386 and  13 <= y <= 31:
            arcade.play_sound(self.click_sound, 0.15)
            self.io.disconnect()

    def on_key_press(self, key, modifiers):
        # Ready to play.
        if self.joined:
            if key == arcade.key.R:
                arcade.play_sound(self.click_sound, 0.15)
                self.io.emit('ready')


#########################################################################################################################


# Shows Win/Lose status after game ends.
class GameEndView(arcade.View):
    def __init__(self, io, winner, team, light_layer):
        super().__init__()
        self.io = io
        self.light_layer = light_layer

        # Choose end screen image.
        texture = findTexture(team, winner)
        self.bg = arcade.load_texture(texture)
        self.click_sound = arcade.load_sound('res\sound\click.mp3')

    def on_draw(self):
        arcade.start_render()
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

        self.light_layer.draw()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.bg)

    def on_mouse_press(self, x, y, button, modifiers):
        # Go back to Home.
        if 364 <= x <= 386 and  13 <= y <= 31:
            arcade.play_sound(self.click_sound, 0.15)
            self.io.disconnect()


#########################################################################################################################


class GameView(arcade.View):
    def __init__(self, io, player, others, items, light_layer):
        super().__init__()
        global game

        self.player = player # Player
        self.others = others # Other players
        self.joined = True
        game =  self
        self.io = io
        self.light_layer = light_layer
        self.view_left = 0
        self.view_bottom = 0
        self.loots_collected = {0: 0, 1: 0}

        # Cache for items and players
        self.item_cache = {-1: arcade.load_texture('res\Items\\none.png')}
        self.player_cache = dict(map(lambda p: (p.id, p), self.others))


        self.life_texture = arcade.load_texture('res\life.png')
        self.bg = arcade.load_texture('res\BG.png')

        # Load map and process layers.
        Map = arcade.read_tmx('res\map.tmx')
        self.block_list = arcade.SpriteList(use_spatial_hash=True, is_static=True) # Spacial hash: Faster collission detection.
        self.wall_list = arcade.process_layer(Map, 'Wall', SCALING) # Walls
        self.object_list = arcade.process_layer(Map, 'Object', SCALING) # Furnitures and objects
        self.special_list = arcade.process_layer(Map, 'Other', SCALING) # FAB and Main switch
        self.door_list = arcade.process_layer(Map, 'Door', SCALING) # Doors
        self.jail_list = arcade.process_layer(Map, 'Jail', SCALING) # Jails

        # All blocking sprites.
        self.block_list.extend(self.wall_list)
        self.block_list.extend(self.object_list)
        self.block_list.extend(self.special_list)
        self.block_list.extend(self.door_list)

        # Blood splash on hit
        self.blood_list = arcade.SpriteList()

        # SpriteList for player sprite.
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        # Items available to pickup.
        self.item_list = arcade.SpriteList()
        # Load cards and weapons
        self.load_items()
        # Load lootable items as per data from server
        id = 14
        for item in items:
            item_code, position = item
            item_obj = Item(id, position, item_code)
            self.item_list.append(item_obj)
            self.item_cache[id] = item_obj
            id += 1

        # Set initial game message.
        task = {0: "Theives inside. Catch everyone.", 1: "Loot Everything you can (Be ware of Guards)."}
        self.info = task[self.player.team]
        self.prevInfo = self.info # Toggle between item-info and other game message.

        # Initialize Aiming control.
        self.aim = Aim(self.player.position)

        # Physics engine for players.
        self.physics = []
        self.physics.append(arcade.PhysicsEngineSimple(self.player, self.block_list))
        for player in self.others:
            self.physics.append(arcade.PhysicsEngineSimple(player, self.block_list))

        self.player_light = Light(0, 0, 80, arcade.color.GREEN, 'soft') # Light to follow player
        self.has_light = 1 # [0:main switch off, 1:main switch on]

        # Load sounds
        self.gun_sound = arcade.load_sound('res\sound\gun.mp3')
        self.stab_sound = arcade.load_sound('res\sound\stab.mp3')
        self.door_sound = arcade.load_sound('res\sound\door.mp3')
        self.item_sound = arcade.load_sound('res\sound\item.mp3')
        self.hurt_sound = arcade.load_sound('res\sound\hurt.mp3')
        self.jail_sound = arcade.load_sound('res\sound\jail.mp3')
        self.error_sound = arcade.load_sound('res\sound\error.mp3')
        self.light_sound = arcade.load_sound('res\sound\light.mp3')
        self.health_sound = arcade.load_sound('res\sound\health.mp3')
        self.bgm = arcade.load_sound('res\sound\\bgm.mp3')
        self.bgm.play(0.2)

    def on_draw(self):
        arcade.start_render()

        # If main switch is off, then set to night mode and activate player_light
        if not self.has_light:
            self.light_layer.add(self.player_light)
            with self.light_layer: # All objects to be lit by light is drawn inside this.
                self.draw_all_game_objects()
            self.light_layer.draw(ambient_color=AMBIENT_COLOR) # Draw lights (night + player_light)

        # If main switch is on, then no need of light effects.
        else:
            if self.player_light in self.light_layer:
                self.light_layer.remove(self.player_light)
            self.light_layer.draw()

            self.draw_all_game_objects()

        arcade.draw_xywh_rectangle_filled(self.view_left, self.view_bottom + 360, SCREEN_WIDTH, 60, arcade.color.BLACK)

        # Show player life in number
        arcade.draw_texture_rectangle(self.view_left + 30, self.view_bottom + 385, 15, 15, self.life_texture, alpha=190)
        arcade.draw_text(str(int(self.player.life * 100)), self.view_left + 23, self.view_bottom + 365, arcade.color.RED, font_size=11, bold=True)

        # Display game message
        arcade.draw_text(self.info, self.view_left + 70, self.view_bottom + 370, arcade.color.GREEN_YELLOW, 10, bold = True)

        # Display team and enemy loot counts.
        arcade.draw_text(str(self.loots_collected[self.player.team]), self.view_left + 352, self.view_bottom + 377, arcade.color.GREEN, 14, bold = True)
        arcade.draw_text(str(self.loots_collected[not self.player.team]), self.view_left + 352, self.view_bottom + 362, arcade.color.RED, 14, bold = True)

        # Show current item
        arcade.draw_texture_rectangle(self.view_left + 380, self.view_bottom + 380, 40, 40, self.get_item_texture(), alpha=190)

    def on_update(self, delta_time):
        for physics in self.physics:
            physics.update()
        self.player_list.update()
        self.others.update()
        self.item_list.update()
        self.blood_list.update()

        # During night mode, player light must follow player.
        if not self.has_light:
            self.player_light.position = self.player.position

        # Check whether player escaped from jail.
        if self.player.jailed:
            if not arcade.check_for_collision_with_list(self.player, self.jail_list):
                self.io.emit('escape')

        if self.aim.toggle:
            self.update_aim() # Manage aim status and lock target

        self.toggle_item_info() # Toggle between item_info and other game messages.

        # Update Viewport based on player movement.
        self.scroll_screen()

        if self.bgm and self.bgm.get_stream_position() == 0:
            self.bgm.stop()
            self.bgm.play(0.2)

    # Click for attacking.
    def on_mouse_press(self, x, y, button, modifiers):
        # If target is locked, then send attack data
        if self.aim.target:
            player = self.aim.target
            self.io.emit('attack', [player.id, player.position, self.aim.damage])

        if self.aim.toggle:
            if self.item_cache[self.player.items[self.player.cur_item]].code == 'K':
                arcade.play_sound(self.stab_sound, 0.2)
            elif self.item_cache[self.player.items[self.player.cur_item]].code == 'G':
                arcade.play_sound(self.gun_sound, 0.05)

     # Switch between items with player.
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        # Check if player has anything in his inventory.
        if self.player.cur_item != -1:
            inventory = len(self.player.items)
            if scroll_y == 1:
                self.player.cur_item = (self.player.cur_item + 1) % inventory
            elif scroll_y == -1:
                self.player.cur_item = (self.player.cur_item - 1 + inventory) % inventory

            # Show game message of item switch.
            self.show_item_switch_msg()
            arcade.play_sound(self.item_sound)

    def on_key_press(self, symbol, modifiers):
        # Player movement
        if symbol == arcade.key.D and self.player.change_x != SPEED:
            self.io.emit('move', [self.player.id, self.player.position, 3])
        elif symbol == arcade.key.A and self.player.change_x != -SPEED:
            self.io.emit('move', [self.player.id, self.player.position, 2])
        elif symbol == arcade.key.W and self.player.change_y != SPEED:
            self.io.emit('move', [self.player.id, self.player.position, 0])
        elif symbol == arcade.key.S and self.player.change_y != -SPEED:
            self.io.emit('move', [self.player.id, self.player.position, 1])

        # Stop or pickup item
        elif symbol == arcade.key.SPACE:
            pickups = []
            inventory = len(self.player.items)
            items = arcade.check_for_collision_with_list(self.player, self.item_list)
            if items:
                items = list(filter(lambda i: not i.taken, items))
                if items:
                    for item in items:
                        if inventory < BAG_CAPACITY:
                            item_ids = list(map(lambda i: i.id, filter(lambda i: i.code == item.code, game.item_list)))
                            if not any(id in item_ids for id in self.player.items):
                                if item.code in ['C', 'PH', 'L', 'PA', 'W', 'B', 'J', 'M']:
                                    pickups.append((item.id, 1))
                                else:
                                    pickups.append((item.id, 0))
                                inventory += 1
                            else:
                                self.info = "You already have it with you. Can't pick up again."
                                arcade.play_sound(self.error_sound, 0.2)
                        else:
                            self.info = 'Your inventory is full ! [ MAX: 4 items ].'
                            arcade.play_sound(self.error_sound, 0.2)

            # if not idle or has picked up some item, send data to server.
            if (self.player.change_x + self.player.change_y) != 0 or pickups:
                self.io.emit('item', [self.player.id, pickups, 1, self.player.position])

        # drop item.
        elif symbol == arcade.key.F:
            if self.player.cur_item == -1:
                self.info = 'Your inventory is empty.'
                arcade.play_sound(self.error_sound, 0.2)
            else:
                drop_item_id = self.player.items[self.player.cur_item]
                item = self.item_cache[drop_item_id]
                if item.code in ['C', 'PH', 'L', 'PA', 'W', 'B', 'J', 'M']:
                    self.io.emit('item', [self.player.id, [(drop_item_id, 1)], 0, self.player.position])
                else:
                    self.io.emit('item', [self.player.id, [(drop_item_id, 0)], 0, self.player.position])

        # Access door, FAB and Main switch
        elif symbol == arcade.key.E:
            specials = arcade.check_for_collision_with_list(self.player, self.special_list)
            if specials:
                if specials[0].properties['id'] == 0: #Health Booster
                    if self.player.life == 1:
                        self.info = "You can't take medicine while health is max."
                        arcade.play_sound(self.error_sound, 0.2)
                    else:
                        self.info = 'Looking for medicines ...'
                        self.io.emit('meds')
                else: # Main Switch
                    self.io.emit('light', (self.has_light + 1) % 2)
            else:
                doors = arcade.check_for_collision_with_list(self.player, self.door_list)
                if doors:
                    keys = keys = list(filter(lambda i: i.code == doors[0].properties['key'], self.item_list))
                    key_ids = list(map(lambda i: i.id, keys))
                    if any(id in self.player.items for id in key_ids):
                        self.io.emit('door', [self.player.id, doors[0].properties['id']])
                    else:
                        self.info = 'You need {} to access this door.'.format(keys[0].name)
                        arcade.play_sound(self.error_sound, 0.2)

    def get_item_texture(self):
        if self.player.cur_item == -1:
            return self.item_cache.get(-1) # none when no item
        else:
            item_id = self.player.items[self.player.cur_item] # find current item's id
            return self.item_cache.get(item_id).texture # return item texture

    def toggle_item_info(self):
        # All messages except item-info ends with dot.
        # If player collides with any item, show it's info.
        # When players leaved the item, toggle back to game info.
        if self.info.endswith('.'):
            self.prevInfo = self.info
        items = arcade.check_for_collision_with_list(self.player, self.item_list)
        if items:
            items = list(filter(lambda i: not i.taken and i.id not in self.player.items, items))
            if items:
                self.info = items[0].info
            else:
                self.info = self.prevInfo
        else:
            self.info = self.prevInfo

    def update_aim(self):
        # Align aim control to the direction player is facing.
        direction = self.player.angle
        self.aim.update(direction, self.player.position)

        # Check if aim control is over any player.
        # If True and has line of sight, then set the closest player as target
        # Aim is inactive(Red) only if there is no LOS to target
        players = arcade.check_for_collision_with_list(self.aim, self.others)
        if len(players) > 0:
            if not players[0].jailed and arcade.has_line_of_sight(self.player.position, players[0].position, self.block_list):
                self.aim.target = players[0] # Lock target
                self.aim.set_texture(0) # Set aim to Green
            else:
                self.aim.set_texture(1) # Set aim to red (Blocking)
                self.aim.target = None
        else:
            self.aim.target = None
            self.aim.set_texture(0)

    # Draw all game objects.
    def draw_all_game_objects(self):
        self.jail_list.draw()
        arcade.draw_lrwh_rectangle_textured(0, 0, 1024, 832, self.bg)
        try:
            self.block_list.draw()
            self.item_list.draw()
            self.others.draw()
            if self.aim.toggle: # Draw only if player is holding any weapon
                self.aim.draw()
            self.player_list.draw()
            self.blood_list.draw()
        except Exception as e:
            print(e)

        # Display player's with life and name.
        arcade.draw_xywh_rectangle_filled(self.player.left, self.player.top + 2, self.player.width * self.player.life, 3, arcade.color.GREEN)
        arcade.draw_text(self.player.name, self.player.center_x - 12, self.player.center_y + 16, arcade.color.BLUE, 8)

        # Display others life and name based on team.
        for player in self.others:
            if player.team == self.player.team:
                arcade.draw_xywh_rectangle_filled(player.left, player.top + 2, player.width * player.life, 3, arcade.color.GREEN)
                arcade.draw_text(player.name, player.center_x - 12, player.center_y + 15, arcade.color.BLUE, 8, bold=True)
            else:
                arcade.draw_xywh_rectangle_filled(player.left, player.top + 2, player.width * player.life, 3, arcade.color.ROSE)
                arcade.draw_text(player.name, player.center_x - 12, player.center_y + 15, arcade.color.RED, 8, bold=True)

    # Drop items where player was last standing when jailed or leaves game.
    def drop_items(self, position, item_ids):
        for id in item_ids:
            item = self.item_cache.get(id)
            x, y = position
            x += randrange(0, 6)
            y += randrange(0, 6)
            item.position = (x, y)
            item.taken = False

    # Show appropriate msg when an item is switched.
    def show_item_switch_msg(self):
        item = self.item_cache[self.player.items[self.player.cur_item]]
        if item.code in ['G', 'K']: # if switched to weapon (gun/knife)
            self.aim.toggle = True # activate aim control
            self.aim.damage = item.damage # set damage of current weapon
        else:
            self.aim.toggle = False
        self.info = "You switched to {}.".format(item.name)

    # Loads swipe cards and weapons.
    def load_items(self):
        items = [(0, (400,82), 'YELLOW'), (1, (620, 82), 'RED'), (2, (110, 370), 'BLUE'), (3, (400, 495), 'BLUE'),
                (4, (95, 675), 'GREEN'), (5, (815, 690), 'GREEN'), (6, (80, 305), 'K'), (7, (205, 305), 'K'),
                (8, (820, 305), 'K'), (9, (940, 305), 'K'), (10, (910, 585), 'G'), (11, (970, 555), 'G'),
                (12, (110, 585), 'G'), (13, (60, 585), 'G')]

        for item in items:
            item_obj = Item(item[0], item[1], item[2])
            self.item_list.append(item_obj)
            self.item_cache[item[0]] = item_obj

    # Scrolling screen according to player movement.
    def scroll_screen(self):
        changed = False # Flag to identify whether player scrolled.

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


#########################################################################################################################


def findTexture(team, winner):
    if team == 0:
        if winner == 0:
            texture = 'res\CopW.png'
        else:
            texture = 'res\CopL.png'
    else:
        if winner == 1:
            texture = 'res\ThiefW.png'
        else:
            texture = 'res\ThiefL.png'
    return texture

def splash_blood(blood_list, position):
    x, y = position
    for i in range(10):
        blood_drop = Blood(4, 4, arcade.color.RED)
        while blood_drop.change_y == 0 and blood_drop.change_x == 0:
            blood_drop.change_y = randrange(-2, 3)
            blood_drop.change_x = randrange(-2, 3)
            blood_drop.center_x = x
            blood_drop.center_y = y
            blood_list.append(blood_drop)


#########################################################################################################################


def main():
    global game
    sio = socketio.Client()

    # When player has successfully connected with server, got to Lobby.
    @sio.event
    def connect():
        print('connected')
        if game:
            game.lock = True # flag set
            view = LobbyView(game.team, sio, game.light_layer)
            game.window.show_view(view)

    # When initial data is recieved, add player and other players in game.
    @sio.event
    def init(data):
        if game:
            pid, name, team, pos = data[0] # player
            game.player = Player(pid, name, team, pos)

            for player in data[1]: # others
                pid, name, team, pos = player
                game.others.append(Player(pid, name, team, pos))
            game.joined = True # flag set

    # when new player has joined, add that player in game.
    @sio.event
    def newPlr(data):
        if game:
            pid, name, team, pos = data[0]
            game.others.append(Player(pid, name, team, pos))

    # If medicine available restore health to max, else show appropriate message.
    # PARAM: player_id, status [0: no meds, else: denotes number of meds left.]
    @sio.event
    def meds(data):
        if game:
            pid, status = data
            if status == 0:
                game.info = 'Oops! No medicine left.'
                arcade.play_sound(game.error_sound, 0.5)
            else:
                if pid == game.player.id:
                    game.player.life = 1
                    game.info = 'Medicines found. Full health restored.\nMedicines left: {}/8.'.format(status)
                    arcade.play_sound(game.health_sound, 0.7)
                else:
                    player = game.player_cache[pid]
                    player.life = 1

    # On each attack, update player's life.
    # PARAMS: player_id, remaining life
    @sio.event
    def attack(data):
        if game:
            pid, life = data
            if game.player.id == pid:
                game.player.life = life
                splash_blood(game.blood_list, game.player.position)
                arcade.play_sound(game.hurt_sound, 0.2)
            else:
                player = game.player_cache[pid]
                player.life = life
                splash_blood(game.blood_list, player.position)

    # If player is knocked down, drop every item he had and send him to jail.
    # status: [0: escaped, 1: jailed]
    @sio.event
    def jail(data):
        if game:
            status, pid, pos, items = data
            if pid == game.player.id:
                if status == 1:
                    game.player.send_to_jail()
                    game.aim.toggle = False
                    game.info = "You got jailed. Hope for being rescued."
                    game.drop_items(pos, items)
                    arcade.play_sound(game.jail_sound, 0.4)
                else:
                    game.player.jailed = False
                    game.player.life = 1
                    game.info = 'You escaped from jail.'
                    arcade.play_sound(game.health_sound, 0.7)
            else:
                player = game.player_cache[pid]
                if status == 1:
                    player.send_to_jail()
                    game.info = "{} got jailed.".format(player.name)
                    game.drop_items(pos, items)
                    arcade.play_sound(game.jail_sound, 0.4)
                else:
                    player.jailed = False
                    player.life = 1
                    game.info = "{} escaped from jail.".format(player.name)

    # Whenever an item is picked up or dropped, stop player, update items and player inventory.
    # status: [0: drop, 1: pickup]
    @sio.event
    def item(data):
        if game:
            pid, item_ids, status, position, loot_count = data

            names = []
            action = None

            for i in item_ids:
                id = i[0]
                item = game.item_cache.get(id)
                item.position = position
                item.taken = status

                if pid == game.player.id:
                    if status == 0:
                        game.player.items.remove(id)
                        action = 'dropped'
                        names.append(item.name)
                        if len(game.player.items) == 0:
                            game.player.cur_item = -1
                        else:
                            game.player.cur_item = 0

                    elif status == 1:
                        game.player.items.append(id)
                        action = 'picked up'
                        names.append(item.name)
                        if len(game.player.items) == 1:
                            game.player.cur_item = 0
                        else:
                            game.player.cur_item = len(game.player.items) - 1

                    if game.player.cur_item != -1:
                        item = game.item_cache.get(game.player.items[game.player.cur_item])
                        if item.code in ['G', 'K']:
                            game.aim.toggle = True
                            game.aim.damage = item.damage
                        else:
                            game.aim.toggle = False
                    else:
                            game.aim.toggle = False

            # Update loot counts
            game.loots_collected[0] = loot_count[0]
            game.loots_collected[1] = loot_count[1]

            if pid == game.player.id:
                game.player.position = position
                game.player.change_x, game.player.change_y = 0, 0
                if names:
                    names = ', '.join(names)
                    names = wrap(names, 40)
                    game.info = 'You {} {}.'.format(action, '\n'.join(names))
                    arcade.play_sound(game.item_sound)
            else:
                player = game.player_cache[pid]
                player.position = position
                player.change_x, player.change_y = 0, 0

    # Move player according to the data recieved.
    @sio.event
    def move(data):
        if game:
            pid, position, direction = data
            speed = {0: (0, SPEED), 1: (0, -SPEED), 2: (-SPEED, 0), 3: (SPEED, 0)}
            if game.player.id == pid:
                game.position = position
                game.player.change_x, game.player.change_y = speed[direction]
            else:
                player = game.player_cache[pid]
                player.position = position
                player.change_x, player.change_y = speed[direction]

    # In case error occurs in connection, notify player.
    @sio.event
    def connect_error(err):
        if game:
            game.msg = "Can't connect with server. Try again later."

    # For turning main switch on and off, which inturn updates lightings.
    # status: [0: off, 1: on]
    @sio.event
    def light(flag):
        if game:
            status = {0:'off', 1: 'on'}
            game.has_light = flag
            game.info = "Main switch has been turned {}.".format(status[flag])
            arcade.play_sound(game.light_sound, 0.1)

    # Locking and unlocking doors.
    # status: [0: unlocked, 1: locked]
    @sio.event
    def door(data):
        if game:
            pid, door_id = data
            door = list(filter(lambda d:d.properties['id'] == door_id, game.door_list))[0]
            if door.properties['locked'] == 0:
                door.properties['locked'] = 1
                game.block_list.append(door)
                if pid == game.player.id:
                    game.info = 'You Locked the door.'
                    arcade.play_sound(game.door_sound, 0.4)
            else:
                door.properties['locked'] = 0
                game.block_list.remove(door)
                if pid == game.player.id:
                    game.info = 'You Opened the door.'
                    arcade.play_sound(game.door_sound, 0.4)

    # Status to stand or end game.
    @sio.event
    def gameState(data):
        if game:
            status = data[0] # status: [1: start game, 0: stop game]
            if status == 1:
                items = data[1]
                view = GameView(game.io, game.player, game.others, items, game.light_layer)
                game.window.show_view(view)
            else:
                winner_team = data[1]
                game.bgm.stop()
                game.bgm = None
                view = GameEndView(game.io, winner_team, game.player.team, game.light_layer)
                game.window.show_view(view)

    # Status for players
    # status: [2: ready to play, 0: left game]
    @sio.event
    def status(data):
        if game:
            while 1:
                if game.joined == True:
                    pid, stat, items = data
                    if pid == game.player.id:
                        game.player.status = stat
                        game.statusText = 'Waiting for other players ...'
                    else:
                        player = list(filter(lambda p: p.id == pid, game.others))[0]
                        player.status = stat
                        if stat == 0:
                            try:
                                game.info = '{} left the game.'.format(player.name)
                                if items:
                                    game.drop_items(player.position, items)
                                del game.player_cache[pid]
                            except Exception as e:
                                print(e)
                            finally:
                                player.remove_from_sprite_lists()
                    break

    # WHen player disconnect from game.
    @sio.event
    def disconnect():
        if game:
            print('disconnected')
            msg = "Disconnected from server. Please connect again."
            sio.disconnect()
            view = HomeView(sio, msg, game.light_layer)
            game.window.show_view(view)

    # Create game window
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)

    # create light layer (context)
    light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Show home screen.
    view = HomeView(sio, None, light_layer)
    window.show_view(view)

    # Game loop.
    arcade.run()

    # If window is closed, disconnect from server.
    sio.disconnect()


#########################################################################################################################


if __name__ == '__main__':
    main()
