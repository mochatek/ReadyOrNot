from arcade import Sprite

ITEM_SCALE = 0.3

class Item(Sprite):
    def __init__(self, ID, pos, item):
        item_dict = {
            'RED': ('cardR', 'Red Swipe Card', '[ Used to unlock Jail ]'),
            'BLUE': ('cardB', 'Blue Swipe Card', '[ Used to unlock Blue Rooms ]'),
            'GREEN': ('cardG', 'Green Swipe Card', '[ Used to unlock Green Rooms ]'),
            'YELLOW': ('cardY', 'Yellow Swipe Card', '[ Used to unlock Yellow Rooms ]'),
            'G': ('gun', '9MM Pistol', 5, 0.1),
            'K': ('knife', "Kitchen Knife", 2, 0.5),
            'C': ('cash', 'Cash Bundles', '10 Lakh rupees'),
            'PH': ('phone', 'Brand new IPhone 11', '[ Worth Rs.100K ]'),
            'L': ('lap', 'Macbook Pro', '[ Worth Rs.160K ]'),
            'PA': ('painting', 'Monalisa Painting', '[ Worth Rs.5200 Cr ]'),
            'W': ('watch', 'Patek Luxury Watch', '[ Worth Rs.30 Cr ]'),
            'B': ('key', "BMW 3.0 CSL Key", '[ Car worths Rs.12 Cr ]'),
        }

        super().__init__('res\Items\{}.png'.format(item_dict[item][0]))

        self.id = ID
        self.scale = ITEM_SCALE
        self.position = pos
        self.item = item_dict[item][1]
        self.taken = False
        if item in ['G', 'K']:
            self.range = item_dict[item][2]
            self.damage = item_dict[item][3]
            self.info = '[ Range : {} , Damage : -{}% ]'.format(self.range, self.damage * 100)
        else:
            self.info = item_dict[item][2]

    def update(self):
        if self.taken:
            self.alpha = 0
