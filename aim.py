from arcade import Sprite

AIM_SCALE = 0.1

class Aim(Sprite):
    def __init__(self, pos):
        super().__init__('res\AimG.png', AIM_SCALE)
        self.position = pos
        self.toggle = False
        self.range = None
        self.damage  = None