import pygame, random, os

# classes
class Player(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()

        if type == 'dad':
            image = pygame.image.load('images/dad.png').convert_alpha()
        elif type == 'mom':
            image = pygame.image.load('images/mom.png').convert_alpha()

        image = pygame.transform.smoothscale(image, (96, 96))

        self.image = image
        self.rect = self.image.get_rect(midleft = (0, WINDOW_HEIGHT // 2))
        self.velocity = 10

    def move(self):
        keys = pygame.key.get_pressed()

        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.rect.top > 0:
            self.rect.y -= self.velocity
        elif (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.rect.bottom < WINDOW_HEIGHT:
            self.rect.y += self.velocity

    def update(self):
        self.move()

class FoodItem(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()

        self.type = type

        if self.type == 'healthy':
            food_item = pygame.image.load('images/healthy/food.png')
        elif self.type == 'junk':
            food_item = pygame.image.load('images/junk/' + random.choice(junk_food))

        self.image = food_item
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(WINDOW_WIDTH, WINDOW_WIDTH + 200)
        self.rect.y = random.randint(0, WINDOW_HEIGHT - 64)
        self.velocity = random.randint(3, 13)

    def update(self):
        self.rect.x -= self.velocity

    def destroy(self):
        if self.rect.x <= 0:
            self.kill()

class Game():
    def __init__(self):
        self.player = None
        self.player_group = pygame.sprite.GroupSingle()

        self.food_items_group = pygame.sprite.Group()

        self.lives = 5
        self.score = 0

        self.state = 'start'

        # load music
        pygame.mixer.music.load('sounds/bg-music.mp3')
        pygame.mixer.music.set_volume(0.1)
        self.eat_sound = pygame.mixer.Sound('sounds/eat.wav')

    def show_init_screen(self):
        title_text = font_title.render('Eat Chikuwa', True, BLUE)
        title_rect = title_text.get_rect(center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 200))

        info_text = font_content.render('Catch the Chikuwa and avoid the other food', True, PURPLE)
        info_rect = info_text.get_rect(center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))

        choose_text = font_content.render('Choose your player', True, WHITE)
        choose_rect = choose_text.get_rect(center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        self.dad_img = pygame.image.load('images/dad.png').convert_alpha()
        self.dad_rect = self.dad_img.get_rect(midleft = (300, WINDOW_HEIGHT // 2 + 100))

        self.mom_img = pygame.image.load('images/mom.png').convert_alpha()
        self.mom_rect = self.mom_img.get_rect(midright = (WINDOW_WIDTH - 300, WINDOW_HEIGHT // 2 + 100))

        screen.fill(BLACK)
        screen.blit(bg, bg_rect)

        screen.blit(title_text, title_rect)
        screen.blit(info_text, info_rect)
        screen.blit(choose_text, choose_rect)

        screen.blit(self.dad_img, self.dad_rect)
        if self.dad_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, BLUE, self.dad_rect, 1)
        else:
            pygame.draw.rect(screen, WHITE, self.dad_rect, 1)

        screen.blit(self.mom_img, self.mom_rect)
        if self.mom_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, BLUE, self.mom_rect, 1)
        else:
            pygame.draw.rect(screen, WHITE, self.mom_rect, 1)

    def add_food_item(self, food_item):
        self.food_items_group.add(food_item)

    def update(self):
        self.user_input()

        if self.state == 'start':
            self.show_init_screen()
        elif self.state == 'play':
            self.play_game()
            self.check_collisions()
            self.check_missed_food()
            self.update_state()
        elif self.state == 'end':
            self.show_end_screen()

    def show_end_screen(self):
        screen.fill(BLACK)
        screen.blit(bg, bg_rect)

        score_text = font_content.render(' Your Score: ' + str(self.score) + ' ', True, PURPLE, WHITE)
        score_rect = score_text.get_rect(center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        play_text = font_content.render(' Press Space to play again ', True, BLUE, WHITE)
        play_rect = play_text.get_rect(center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))

        screen.blit(score_text, score_rect)
        screen.blit(play_text, play_rect)

    def update_state(self):
        score_text = font_content.render(' Score: ' + str(self.score) + ' ', True, PURPLE, WHITE)
        score_rect = score_text.get_rect(center = (WINDOW_WIDTH // 2, 20))

        lives_text = font_content.render(' Lives: ' + str(self.lives) + ' ', True, PURPLE, WHITE)
        lives_rect = lives_text.get_rect(center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))

        screen.blit(score_text, score_rect)
        screen.blit(lives_text, lives_rect)

    def check_missed_food(self):
        for food_item in self.food_items_group:
            if food_item.rect.right < 0 and food_item.type == 'healthy':
                self.lives -= 1
                food_item.destroy()

                if self.lives <= 0:
                    self.state = 'end'

    def check_collisions(self):
        collided_food_item = pygame.sprite.spritecollideany(self.player, self.food_items_group)

        if collided_food_item:
            self.eat_sound.play()
            if collided_food_item.type == 'healthy':
                self.score += 1
            else:
                if self.score >= 0.5:
                    self.score -= 0.5

            # remove collided item
            collided_food_item.remove(self.food_items_group)

    def play_game(self):
        screen.fill(BLACK)
        screen.blit(bg, bg_rect)

        self.player_group.draw(screen)
        self.player_group.update()

        self.food_items_group.draw(screen)
        self.food_items_group.update()

    def user_input(self):
        if self.state == 'start':
            player_type = None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # dad is clicked
                if self.dad_rect.collidepoint(pygame.mouse.get_pos()):
                    player_type = 'dad'
                # mom is clicked
                elif self.mom_rect.collidepoint(pygame.mouse.get_pos()):
                    player_type = 'mom'

                if player_type:
                    player = Player(player_type)
                    self.player_group.add(player)
                    self.player = player
                    self.state = 'play'
                    pygame.mixer.music.play(-1)
        if self.state == 'end':
            pygame.mixer.music.stop()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = 'start'
                self.lives = 5
                self.score = 0
                self.food_items_group.empty()

pygame.init()

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 596
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Eat Chikuwa')

FPS = 60
clock = pygame.time.Clock()

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 128, 255)
PURPLE = (178, 102, 255)

# background image
bg = pygame.image.load('images/table.jpg').convert_alpha()
bg_rect = bg.get_rect(topleft = (0, 0))

# fonts
font_title = pygame.font.Font('fonts/Pumpkin Soup.ttf', 84)
font_content = pygame.font.Font('fonts/Pumpkin Soup.ttf', 32)

# get food names
healthy_food = [f for f in os.listdir('images/healthy') if os.path.join('images/healthy', f)]
junk_food = [f for f in os.listdir('images/junk') if os.path.join('images/junk', f)]

# timer
food_item_timer = pygame.USEREVENT + 1
pygame.time.set_timer(food_item_timer, 1500)

# initialize game
my_game = Game()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if my_game.state == 'play':
            if event.type == food_item_timer:
                my_game.add_food_item(FoodItem(random.choice(['healthy','junk'])))

    my_game.update()

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
