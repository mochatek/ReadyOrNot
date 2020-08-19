from arcade import Sprite

AIM_SCALE = 0.15

class Aim(Sprite):
    def __init__(self, pos):
        super().__init__('res\Aim.png', AIM_SCALE)
        self.position = pos
        self.type = None
        self.range = None
        self.damage  = None