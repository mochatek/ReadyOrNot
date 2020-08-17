import socketio
from _thread import start_new_thread
import arcade

from aim import Aim
from player import Player
from item import Item

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
SCALING = 0.25
TITLE = "Ready or Not ?"
SPEED = 2
ITEM_SCALE = 0.3
AIM_SCALE = 0.15
MARGIN = 160

game = None

def setupNetwork(io):
    sio = io
    global game

    @sio.event
    def connect():
        game.msg = 'success'

    @sio.event
    def message(data):
        game.msg = data

    @sio.event
    def init(data):
        id, name, life, tex, team, stat, pos = data['you']
        game.player = Player(id, name, life, tex, team, stat, pos)

        for player in data['others']:
            id, name, life, tex, team, stat, pos = player
            game.other_players_list.append(Player(id, name, life, tex, team, stat, pos))
        game.ready = True

    @sio.event
    def newPlr(data):
        id, name, life, tex, team, stat, pos = data['player']
        game.other_players_list.append(Player(id, name, life, tex, team, stat, pos))


    @sio.event
    def connect_error(err):
        game.msg = "Can't connect with server. Try again later."

    @sio.event
    def disconnect():
        game.msg = "Can't connect with server. Try again later."


    try:
        sio.connect('http://localhost:5000')
    except:
        game.msg = "Can't connect with server. Try again later."

# Initail game screen.
class ScreenView(arcade.View):
    def __init__(self, msg=None):
        super().__init__()
        self.bg = arcade.load_texture('res\screen.png')
        self.team = -1
        # Display any game messages (ERROR).
        self.msg = msg

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.bg)
        if self.msg and self.msg != 'success':
            arcade.draw_text(self.msg, 110, 380, arcade.color.ANTIQUE_WHITE, 8, font_name=('Times New Roman'))

    def on_update(self, dt):
        if self.msg == 'success':
            view = LobbyView(self.team, self.io)
            self.window.show_view(view)

    def on_mouse_press(self, x, y, button, modifiers):
        # If player pressed setting button, show info.
        if 374 <= y <= 390 and 373 <= x <= 389:
            # Show settings and other info.
            view = InfoView(self.team, self.io)
            self.window.show_view(view)

        # Find team chosen by player.
        elif 120 <= y <= 136:
            if  96 <= x <= 141:
                self.team = 0
            elif 249 <= x <= 294:
                self.team = 1

        if self.team != -1:
            self.io = socketio.Client()
            global game
            game = self
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
        self.ready = False #true once data has been updated in client
        global game
        game = self
        self.io = io
        self.bg = arcade.load_texture('res\lobby.png')

        self.other_players_list = arcade.SpriteList()
        self.item_list = arcade.SpriteList()

        # Request join.
        self.io.emit('join', ['mocha', team])

        # Message to be displayed below. (It is based on the game status)
        self.msg = "Looking for Opponents..."


    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.bg)

        # Display game message.
        arcade.draw_text(self.msg, 20, 15, arcade.color.WHITE, 10, bold=True)

        if self.ready:
            # Draw player and his name.
            file = self.player.file
            arcade.Sprite(file, 1, center_x=120, center_y=268).draw()
            arcade.draw_text(self.player.name, 200, 255, arcade.color.GREEN, 12, bold=True)

            y = 268
            # sort_order = {0:False, 1:True}
            # for p in sorted(self.data, key = lambda x:x[6], reverse = sort_order.get(self.player.team)):
            for i in range(3):
                y = y - 50
                # Not joined or left.
                if i >= len(self.other_players_list):
                    arcade.Sprite('res\Players\inactive.png', 1, center_x=120, center_y=y).draw()
                    arcade.draw_text("Searching...", 200, y-12, arcade.color.WHITE_SMOKE, 12, bold=True)
                else:
                    try:
                        file = self.other_players_list[i].file
                        arcade.Sprite(file, 1, center_x=120, center_y=y).draw()
                        arcade.draw_text(self.other_players_list[i].name, 200, y-10, arcade.color.GREEN, 12, bold=True)
                    except:
                        pass


    def on_update(self, delta_time):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
    # Go back to screen view.
        if 364 <= x <= 386 and  13 <= y <= 31:
            view = ScreenView()
            self.window.show_view(view)



def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    # Show initial game load screen.
    view = ScreenView()
    window.show_view(view)
    arcade.run()

if __name__ == '__main__':
    main()
