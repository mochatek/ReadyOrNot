from arcade import Sprite
from arcade import load_texture

PLAYER_SCALE  = 0.45

class Player(Sprite):
    def __init__(self, ID, name, life, tex, team, stat, pos):
        if team == 0:
            file = 'res\Players\Cop'
        else:
            file = 'res\Players\Theif'
        super().__init__(file + "U.png")
        self.file =  file + "D.png"
        self.textures.append(load_texture(file + "D.png"))
        self.textures.append(load_texture(file + "L.png"))
        self.textures.append(load_texture(file + "R.png"))
        self.scale = PLAYER_SCALE
        self.cur_texture_index = 0

        self.id = ID
        self.name = name
        self.position  = pos
        self.status = stat
        self.life = life
        self.team = team
        self.items = []
        self.cur_item = -1
        self.in_jail = False

    def update(self):
        self.set_texture(self.cur_texture_index)
        self.center_x += self.change_x
        self.center_y += self.change_y