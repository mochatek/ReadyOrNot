import arcade
from arcade.experimental.lights import Light, LightLayer

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
SCREEN_TITLE = "Lighting Demo"
VIEWPORT_MARGIN = 200
MOVEMENT_SPEED = 2
SCALING = 0.25

AMBIENT_COLOR = (10, 10, 10)

class GameView(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.view_left = 0
        self.view_bottom = 0
        self.bg = arcade.load_texture('res\BG.png')

        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.light_layer.set_background_color(arcade.color.BLACK)
        self.player_light = Light(0, 0, 60, arcade.color.WHITE, 'soft')
        self.light_layer.add(self.player_light)

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

        self.player = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", 0.2, center_x=300, center_y=100)

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)


        # Physics engine for the game.
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.block_list)


    def on_draw(self):
        arcade.start_render()
        with self.light_layer:
            arcade.draw_lrwh_rectangle_textured(0, 0, 1024, 832, self.bg)
            self.block_list.draw()
            self.player_list.draw()
        self.light_layer.draw(ambient_color=AMBIENT_COLOR)

    def on_key_press(self, key, _):
            if key == arcade.key.UP:
                self.player.change_y = MOVEMENT_SPEED
            elif key == arcade.key.DOWN:
                self.player.change_y = -MOVEMENT_SPEED
            elif key == arcade.key.LEFT:
                self.player.change_x = -MOVEMENT_SPEED
            elif key == arcade.key.RIGHT:
                self.player.change_x = MOVEMENT_SPEED


    def on_key_release(self, key, _):
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.change_x = 0

    def scroll_screen(self):
        """ Manage Scrolling """

        # Scroll left
        left_boundary = self.view_left + VIEWPORT_MARGIN
        if self.player.left < left_boundary:
            self.view_left -= left_boundary - self.player.left

        # Scroll right
        right_boundary = self.view_left + self.width - VIEWPORT_MARGIN
        if self.player.right > right_boundary:
            self.view_left += self.player.right - right_boundary

        # Scroll up
        top_boundary = self.view_bottom + self.height - VIEWPORT_MARGIN
        if self.player.top > top_boundary:
            self.view_bottom += self.player.top - top_boundary

        # Scroll down
        bottom_boundary = self.view_bottom + VIEWPORT_MARGIN
        if self.player.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player.bottom

        self.view_left = int(self.view_left)
        self.view_bottom = int(self.view_bottom)

        arcade.set_viewport(self.view_left,
                            self.width + self.view_left,
                            self.view_bottom,
                            self.height + self.view_bottom)

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.player_light.position = self.player.position
        self.scroll_screen()

if __name__ == "__main__":
    window = GameView()
    arcade.run()