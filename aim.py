from arcade import Sprite, load_texture

AIM_SCALE = 0.1

class Aim(Sprite):
    def __init__(self, pos):
        super().__init__('res\AimG.png', AIM_SCALE)
        self.textures.append(load_texture('res\AimR.png'))
        self.set_texture(0)
        self.position = pos
        self.toggle = False
        self.range = None
        self.damage  = None