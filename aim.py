from arcade import Sprite, load_texture

AIM_SCALE = 1

class Aim(Sprite):
    def __init__(self, pos):
        super().__init__('res\AimG.png', AIM_SCALE)
        self.textures.append(load_texture('res\AimR.png'))
        self.position = pos
        self.toggle = False
        self.damage  = None
        self.target = None

    def update(self, direction, position):
        self.angle = direction
        x, y = position
        if direction == 0:
            self.position = x, y + self.height // 2
        elif direction == 180:
            self.position = x, y - self.height // 2
        elif direction == 90:
            self.position = x - self.height // 2, y
        elif direction == 270:
            self.position = x  + self.height // 2, y

        if self.damage == 0.1:
            self.scale = 2
        else:
            self.scale = 1
