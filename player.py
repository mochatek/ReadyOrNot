from arcade import Sprite
from arcade import load_texture

PLAYER_SCALE  = 0.45

class Player(Sprite):
    def __init__(self, ID, name, team, pos):
        if team == 0:
            file = 'res\Players\Cop'
        else:
            file = 'res\Players\Theif'
        super().__init__(file + "U.png")
        self.file =  file + "D.png"

        self.scale = PLAYER_SCALE

        self.id = ID
        self.name = name
        self.team = team
        self.position  = pos
        self.angle = 0
        self.status = 1
        self.life = 1
        self.items = []
        self.cur_item = -1
        self.in_jail = False

    def update(self):
        if self.change_y > 0:
            self.angle = 0
        elif self.change_y < 0:
            self.angle = 180
        elif self.change_x > 0:
            self.angle = 270
        elif self.change_x < 0:
            self.angle = 90

        self.center_x += self.change_x
        self.center_y += self.change_y