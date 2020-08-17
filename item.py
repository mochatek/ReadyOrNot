from arcade import Sprite

class Item(Sprite):
    def __init__(self, ID, pos, item):
        if item == 'G':
            super().__init__('res\Items\gun.png')
            self.name = '9MM Pistol'
            self.range = 5
            self.damage = 0.1
            self.info = '[ Range : {} , Damage : -{}% ]'.format(self.range, self.damage * 100)
        elif item == 'K':
            super().__init__('res\Items\knife.png')
            self.name = "Kitchen Knife"
            self.range = 2
            self.damage = 0.5
            self.info = '[ Range : {} , Damage : -{}% ]'.format(self.range, self.damage * 100)
        elif item == 'RED':
            super().__init__('res\Items\cardR.png')
            self.name = 'Red Swipe Card'
            self.info = '[ Used to unlock Jail ]'
        elif item == 'BLUE':
            super().__init__('res\Items\cardB.png')
            self.name = 'Blue Swipe Card'
            self.info = '[ Used to unlock Blue Rooms ]'
        elif item == 'GREEN':
            super().__init__('res\Items\cardG.png')
            self.name = 'Green Swipe Card'
            self.info = '[ Used to unlock Green Rooms ]'
        elif item == 'YELLOW':
            super().__init__('res\Items\cardY.png')
            self.name = 'Yellow Swipe Card'
            self.info = '[ Used to unlock Yellow Rooms ]'
        elif item == 'C':
            super().__init__('res\Items\cash.png')
            self.name = 'Cash Bundles'
            self.info = ''
        elif item == 'J':
            super().__init__('res\Items\jewel.png')
            self.name = 'Precious Jewels'
            self.info = '[ Worth Lakhs ]'
        elif item == 'PH':
            super().__init__('res\Items\phone.png')
            self.name = 'Brand new IPhone 11'
            self.info = '[ Worth Rs.100K ]'
        elif item == 'L':
            super().__init__('res\Items\lap.png')
            self.name = 'Macbook Pro'
            self.info = '[ Worth Rs.160K ]'
        elif item == 'PA':
            super().__init__('res\Items\painting.png')
            self.name = 'Monalisa Painting'
            self.info = '[ Worth Rs.5200 Cr ]'
        elif item == 'W':
            super().__init__('res\Items\watch.png')
            self.name = 'Patek Luxury Watch'
            self.info = '[ Worth Rs.30 Cr ]'
        elif item == 'B':
            super().__init__('res\Items\key.png')
            self.name = "BMW 3.0 CSL Key"
            self.info = '[ Car worths Rs.12 Cr ]'

        self.id = ID
        self.scale = ITEM_SCALE
        self.position = pos
        self.item = item
        self.taken = -1