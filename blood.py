from arcade import SpriteSolidColor

class Blood(SpriteSolidColor):
    def update(self):
        # Move
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Fade
        self.alpha -= 17
        if self.alpha <= 0:
            self.remove_from_sprite_lists()