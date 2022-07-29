import pygame, sys
import random

import variable_arrs

#General setup
pygame.init()
clock = pygame.time.Clock()

#Game screen
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

#game variabeles
game_status = 0
battle_status = 0
running = True
player = None
enemy = None
prev_level = None
level = 'level1'
level_bg = None
map_width = 0
map_height = 0
texture_scale = pygame.math.Vector2()
texture_scale = 96
action_wait_time = 90
item = None


#sprites for animation

#sprites of fight stage
PANEL = pygame.image.load('sprites\\panel.jpg').convert()

#sounds
ERROR_SOUND = pygame.mixer.Sound('sounds\\error.wav')

#fonts
COMIC_SANS_50 = pygame.font.Font('fonts\\comicsansms.ttf', 50)
COMIC_SANS_20 = pygame.font.Font('fonts\\comicsansms.ttf', 20)

#game classes
class Tile(pygame.sprite.Sprite):
    def __init__(self,sprite,pos,group):
        super().__init__(group)
        self.image = load_sprite(sprite)
        self.rect = self.image.get_rect(topleft = (pos[0]*texture_scale, pos[1]*texture_scale))
        self.old_rect = self.rect.copy()

class Item(Tile):
    def __init__(self, sprite, pos, group, name):
        super().__init__(sprite, pos, group)
        self.name = ' '.join(variable_arrs.items[name][x] for x in range(len(variable_arrs.items[name])-1))
        self.effect = name
        self.bonus = int(variable_arrs.items[name][2][:-1])
        self.price = variable_arrs.items[name][3]

class Teleport(Tile):
    def __init__(self, sprite, pos, location, group):
        super().__init__(sprite,pos, group)
        self.location = location

class Enemy(pygame.sprite.Sprite):
    def __init__(self, sprite, pos, level, group):
        super().__init__(group)
        self.name = sprite[:-4]
        self.image = load_sprite(sprite)
        self.pos = pygame.math.Vector2(pos)*texture_scale
        self.rect = self.image.get_rect(topleft = (pos[0]*texture_scale,pos[1]*texture_scale))
        self.level = level + player.level if self.name != 'blank' else 0
        self.health = level * 2 + player.level
        self.damage = level
        self.action_cooldown = 0

    def attack(self, target):
        damage = self.level + self.damage
        target.health -= damage
    
class MenuButton():
    def __init__(self, font, option, colour, func=None, item = None):
        self.surface = font.render(option, False, colour)
        self.func = func
        self.item = item

class Menu:
    def __init__(self, font):
        self._options = []
        self._current_option_index = 0
        self._font = font


    def append(self, option, callback):
        self._options.append(MenuButton(self._font, option, 'white', callback))


    def remove(self, option):
        self._options.remove(option)


    def switch(self, direction):
        self._current_option_index = max(0, min(self._current_option_index + direction, len(self._options)-1))


    def select(self):
        if len(self._options):
            self._options[self._current_option_index].func()
    

    def draw(self, surf, x, y, padding):
        for i, option in enumerate(self._options):
            option_rect = option.surface.get_rect()
            option_rect.topleft = (x, y + i * padding)
            if i == self._current_option_index:
                pygame.draw.rect(surf, ('purple'), option_rect)
            surf.blit(option.surface, option_rect)

class Inventory(Menu):
    def __init__(self, font):
        super().__init__(font)
        self._rect = pygame.Rect(200,100,400,300)
    

    def append(self, name, item):
            self._options.append(MenuButton(self._font,name, 'white', item=item))

    
    def select(self):
        if len(self._options):
            return self._options[self._current_option_index]
    

    def draw(self, surf):
        pygame.draw.rect(surf, ('grey'), self._rect)
        for i, option in enumerate(self._options):
            option_rect = option.surface.get_rect()
            option_rect.topleft = (200,100 + i * 25)
            if i == self._current_option_index:
                pygame.draw.rect(surf, ('purple'), option_rect)
            surf.blit(option.surface, option_rect)

class Shop(Menu):
    def __init__(self, font):
        super().__init__(font)
        self._rect = pygame.Rect(200,100,500,300)
        self.fill()


    def append(self, name, item):
        self._options.append(MenuButton(self._font,name, 'white', item=item))


    def select(self):
        if len(self._options):
            return self._options[self._current_option_index]


    def draw(self, surf):
            pygame.draw.rect(surf, ('grey'), self._rect)
            for i, option in enumerate(self._options):
                option_rect = option.surface.get_rect()
                option_rect.topleft = (200,100 + i * 25)
                if i == self._current_option_index:
                    pygame.draw.rect(surf, ('purple'), option_rect)
                surf.blit(option.surface, option_rect)
                draw_text('119 p', COMIC_SANS_20, 'white', 550, 100)
                draw_text('22 p', COMIC_SANS_20, 'white', 550, 125)
                draw_text('390 p', COMIC_SANS_20, 'white', 550, 150)
                draw_text('30000000 p.', COMIC_SANS_20, 'brown', 550, 175)
                

    def fill(self):
        for i in range(4):
            name = variable_arrs.items_names[i]
            # item_name = ' '.join(variable_arrs.items[name][x] for x in range(len(variable_arrs.items[name])-1))
            sprite = name + '.png' if name != 'bread' else 'blank.png'
            item = Item(sprite, (-3,-3), collectable_gpoup, name, )
            self.append(item.name, item)

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)

        self.sprite_list = []
        self.sprite_list.append(load_sprite('player0.png'))
        self.sprite_list.append(load_sprite('player1.png'))
        self.sprite_list.append(load_sprite('player2.png'))


        self.name = 'Anon'
        self.image = self.sprite_list[0]
        self.pos = pygame.math.Vector2(pos)*texture_scale
        self.rect = self.image.get_rect(topleft = (pos[0]*texture_scale,pos[1]*texture_scale))
        self.old_rect = self.rect.copy()
        self.direction = pygame.math.Vector2()
        self.level = 1
        self.exp = 0
        self.max_exp = 10
        self.max_health = 10
        self.health = 10
        self.speed = 5
        self.damage = 2
        self.money = 3000000000
        self.inventory = Inventory(COMIC_SANS_20)
        self.shop = Shop(COMIC_SANS_20)
        self.inv_weight = 0
        self.in_inventory = False
        self.in_shop = False
        self.in_battle = False
        self.pressed = False
        self.can_attack = False
        self.target = None
        self.action_cooldown = 0
        self.self_BREAD = False


    def change_pos(self, pos):
        self.pos.x = pos[0]*texture_scale
        self.pos.y = pos[1]*texture_scale


    def level_up(self):
        self.level += 1
        self.max_health += self.level
        self.health = self.max_health
        self.max_exp *= 2


    def useButton(self, button=None):
        if button is not None and not self.in_shop:
            if button.item.effect == 'heal':
                self.health = (self.health + (self.max_health * button.item.bonus)//100)
                self.health = self.health if self.max_health >= self.health else self.max_health
                self.inventory.remove(button)
                self.inv_weight -= 1

            elif button.item.effect == 'add_damage':
                self.damage += button.item.bonus
                self.inventory.remove(button)
                self.inv_weight -= 1

            elif button.item.effect == 'add_health':
                self.max_health += button.item.bonus
                self.health += button.item.bonus
                self.inventory.remove(button)
                self.inv_weight -= 1

        elif button is not None and self.in_shop:
            print(button.item.effect)
            if self.money >= button.item.price:
                self.money -= button.item.price
                self.inventory.append(button.item.effect, button.item)
                self.inv_weight += 1
                if button.item.effect == 'bread':
                    self._BREAD = True
            else:
                ERROR_SOUND.play()

        else:
            ERROR_SOUND.play()


    def input(self):
        keys_d = pygame.key.get_pressed()
        if not self.in_inventory:
            if not self.in_battle:
                if keys_d[pygame.K_UP] and self.rect.top > 0:
                    self.direction.y = -1
                elif keys_d[pygame.K_DOWN] and self.rect.bottom < map_height*texture_scale:
                    self.direction.y = 1
                else:
                    self.direction.y = 0

                if keys_d[pygame.K_RIGHT] and self.rect.right < map_width*texture_scale:
                    self.direction.x = 1
                elif keys_d[pygame.K_LEFT] and self.rect.left > 0:
                    self.direction.x = -1
                else:
                    self.direction.x = 0

            if self.in_battle:
                if keys_d[pygame.K_z] and not self.pressed and self.can_attack:
                    self.attack()
                    self.can_attack = False
                    self.pressed = True
                    player.action_cooldown = 0
                else:
                    self.direction.x = 0
                    self.direction.y = 0    

            if keys_d[pygame.K_c] and not self.pressed:
                self.in_inventory = True
                self.pressed = True

            if level == 'level4' and not self.in_inventory:
                if not self.pressed:
                    if keys_d[pygame.K_z] and not self.in_shop:
                        self.in_shop = True
                        self.pressed = True
                    if keys_d[pygame.K_x]: 
                        self.in_shop = False
                    if keys_d[pygame.K_UP] and self.in_shop:
                        self.shop.switch(-1)
                        self.pressed = True
                    elif keys_d[pygame.K_DOWN] and self.in_shop:
                        self.shop.switch(1)
                        self.pressed = True
                    elif keys_d[pygame.K_z] and self.in_shop and not self.pressed:
                        button = self.shop.select()
                        self.useButton(button)
                        self.pressed = True
                
        elif self.in_inventory:
            if keys_d[pygame.K_c] and not self.pressed:
                self.in_inventory = False
                self.pressed = True
            if keys_d[pygame.K_UP] and not self.pressed:
                self.inventory.switch(-1)
                self.pressed = True
            elif keys_d[pygame.K_DOWN] and not self.pressed:
                self.inventory.switch(1)
                self.pressed = True
            elif keys_d[pygame.K_z] and not self.pressed:
                if not self.in_battle:
                    button = self.inventory.select()
                    self.useButton(button)
                    self.pressed = True
                elif self.can_attack:
                    button = self.inventory.select()
                    self.useButton(button)
                    self.pressed = True
                    self.can_attack = False
                    self.in_inventory = False
            else:
                self.direction.x = 0
                self.direction.y = 0
        
        if not keys_d[pygame.K_c] and not keys_d[pygame.K_z] \
            and not keys_d[pygame.K_UP] and not keys_d[pygame.K_DOWN]:
            self.pressed = False
    

    def attack(self):
        damage = self.level + self.damage
        self.target.health -= damage


    def collision(self, direction):
        collision_sprites = pygame.sprite.spritecollide(self, obstacle_group, False)
        if collision_sprites:
            if direction == 'horizontal':
                for sprite in collision_sprites:
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left
                        self.pos.x = self.rect.x
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right
                        self.pos.x = self.rect.x
            if direction =='vertical':
                for sprite in collision_sprites:
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom
                        self.pos.y = self.rect.y
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top
                        self.pos.y = self.rect.y


    def update(self):
        self.old_rect = self.rect.copy()
        self.input()

        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        if self.in_inventory:
            self.inventory.draw(screen)
        if self.in_shop:
            self.shop.draw(screen)
        
        if self.direction.y < 0:
            self.image = self.sprite_list[2]
        elif self.direction.y < 0 and self.direction.x > 0:
            self.image = self.sprite_list[0]
        elif self.direction.y < 0 and self.direction.x < 0:
            self.image = self.sprite_list[1]
        elif self.direction.x < 0:
            self.image = self.sprite_list[1]
        elif self.direction.x > 0:
            self.image = self.sprite_list[0]

        self.pos.x += self.direction.x * self.speed
        self.rect.x = round(self.pos.x)
        self.collision('horizontal')
        self.pos.y += self.direction.y * self.speed
        self.rect.y = round(self.pos.y)
        self.collision('vertical')

        if player.exp >= self.max_exp:
            player.exp = player.exp % self.max_exp
            player.level_up()

class CameraGroup(pygame.sprite.Group):
    def __init__(self, *groups):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.groups = groups
        #offset
        self.offset = pygame.math.Vector2()
        self.hallf_width = self.display_surface.get_size()[0] // 2
        self.hallf_height = self.display_surface.get_size()[1] // 2
        
        #camera box
        self.camera_borders = {'left': 200, 'right': 200, 'top': 200, 'bottom':200}
        l = self.camera_borders['left']
        t = self.camera_borders['top']
        w = self.display_surface.get_size()[0] - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.display_surface.get_size()[1] - (self.camera_borders['top'] + self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(l,t,w,h)

    def center_target(self, target):
        self.offset.x = target.rect.centerx - self.hallf_width
        self.offset.y = target.rect.centery - self.hallf_height

    def box_target(self, target):
        if target.rect.left < self.camera_rect.left:
            self.camera_rect.left = target.rect.left
        if target.rect.right > self.camera_rect.right:
            self.camera_rect.right = target.rect.right
        if target.rect.top < self.camera_rect.top:
            self.camera_rect.top = target.rect.top
        if target.rect.bottom > self.camera_rect.bottom:
            self.camera_rect.bottom = target.rect.bottom    

        self.offset.x = self.camera_rect.left - self.camera_borders['left']
        self.offset.y = self.camera_rect.top - self.camera_borders['top']
        

    def camera_draw(self, target):
        
        self.box_target(target)

        for group in self.groups:
            for sprite in group:
                sprite_offset = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image, sprite_offset)

        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

        draw_text('hp: '+str(target.health)+'/'+str(target.max_health), COMIC_SANS_20, 'red', 10, 10)
        draw_text('exp: '+str(target.exp)+'/'+str(target.max_exp), COMIC_SANS_20, 'white', 10, 40)
        draw_text('items: '+str(target.inv_weight)+'/12', COMIC_SANS_20, 'white', 10, 70)
        draw_text(str(target.money)+' p.', COMIC_SANS_20, 'white', 10, 100)



    def clear(self):
        for group in self.groups:
            group.empty()



#game functions
def start():
    global game_status
    generate_level(load_level(level))
    game_status = 1

def quit():
    global running
    running = False

def load_sprite(sprite_name):
    sprite = 'sprites\\' + sprite_name
    return pygame.image.load(sprite).convert_alpha()

def switch_level(next_level, camera):
    global prev_level, level, level_bg, enemy, item
    prev_level = level
    level = next_level[:-4]
    player.change_pos(variable_arrs.pos[int(prev_level[-1])][int(next_level[-5])])
    camera.clear()
    level_bg = Tile(next_level,(0,0),ground_group)
    if next_level == 'level2.png':
        enemy = Enemy('Gopnik.png', (1,2),2,enemy_group)
    elif next_level == 'level0.png':
        enemy = Enemy('blank.png', (4,1),0,enemy_group)
    elif next_level == 'level3.png':
        if random.randint(0,1):
            name = variable_arrs.items_names[random.randint(0,2)]
            item = Item(name+'.png',(random.randint(2,12),random.randint(3,6)), collectable_gpoup, name)
    if next_level == 'level1.png' and player._BREAD:
        quit()
    return generate_level(load_level(level))

def load_level(cur_level) -> list:
    cur_level = 'levels\\'+level+'.txt'
    with open(cur_level, 'r') as map_file:
        level_data = []
        global map_width, map_height
        map_width, map_height, data_lines = map(int, map_file.readline().split())
        for line in range(data_lines):
            level_data.append((map_file.readline().strip().split('-')))

        level_map = []
        for line in range(map_height):
            line = map_file.readline().strip()
            level_map.append(line)

    return (level_data, level_map)

def generate_level(cur_level) -> list:
    level_data, level_map = cur_level
    teleports = dict()
    for data in level_data:
        teleports[data[1]] = data[0]
    for y in range(len(level_map)):
        for x, symbol in enumerate(level_map[y]):
            if symbol == '#':
                Tile('blank.png', (x,y), obstacle_group)
            elif symbol.isdigit():
                Teleport('blank.png', (x,y), teleports[symbol], teleport_group)

            
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_panel():
    screen.blit(PANEL, (0, 400))
    draw_text(f'{player.name} HP: {player.health}', COMIC_SANS_20, 'white', 100, 510)
    draw_text(f'{enemy.name} HP: {enemy.health}', COMIC_SANS_20, 'white', 550, 510)
    


#Group setup
ground_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
teleport_group = pygame.sprite.Group()
collectable_gpoup = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()
camera_group = CameraGroup(
    ground_group, teleport_group,
    collectable_gpoup, enemy_group,obstacle_group
)


#MainMenu
menu = Menu(COMIC_SANS_50)
menu.append('Start!', lambda: start())
menu.append('Quit', lambda: quit())


level_bg = Tile('level1.png',(0,0),ground_group)


player = Player((2,1), camera_group)

while running:
    screen.fill('black')
    #main menu
    if game_status == 0:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    menu.switch(-1)
                elif event.key == pygame.K_DOWN:
                    menu.switch(1)
                elif event.key == pygame.K_z:
                    menu.select()
            elif event.type == pygame.QUIT:
                quit()
        menu.draw(screen, 300, 200, 75)
        draw_text("Get some bread!!!!!", COMIC_SANS_50, 'yellow', 200, 100)

    #location
    elif game_status == 1:
        player.in_battle = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        camera_group.camera_draw(player)
        camera_group.update()
        if pygame.sprite.spritecollide(player, teleport_group, 0):
            switch_level(pygame.sprite.spritecollideany(player, teleport_group).location, camera_group)
        if pygame.sprite.spritecollide(player, collectable_gpoup, False) and player.inv_weight < 12 :
            item = pygame.sprite.spritecollideany(player, collectable_gpoup)
            player.inventory.append(item.name, item)
            player.inv_weight += 1
            pygame.sprite.spritecollide(player, collectable_gpoup, True)
        if pygame.sprite.spritecollide(player, enemy_group, 0):
            enemy = pygame.sprite.spritecollideany(player, enemy_group)
            player.target = enemy
            player.in_battle = True
            player.action_cooldown = 0
            enemy.action_cooldown = 0
            game_status = 3
            battle_status = 0

        
    # battle
    elif game_status == 3:
        camera_group.camera_draw(player)
        player.update()
        draw_panel()
        
        if battle_status == 0:
            if player.health > 0:
                player.action_cooldown += 1
                if player.action_cooldown >= action_wait_time:
                    player.can_attack = True
                    draw_text('Do something',COMIC_SANS_50, 'green', 250, 250)
                                
            
            if enemy.health > 0:
                enemy.action_cooldown += 1
                if enemy.action_cooldown >= action_wait_time:
                    enemy.attack(player)
                    enemy.action_cooldown = 0
            else:
                battle_status = 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()


        if battle_status == 1:
            player.exp += enemy.level*2 + 1 
            player.money += (enemy.level + random.randint(1,15)*2) if enemy.name != 'blank' else 0
            enemy.kill()
            player.action_cooldown = 0
            game_status = 1
        elif player.health <= 0:
            player.action_cooldown = 0
            player.health = 1
            game_status = 1
            enemy.kill()

    
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()