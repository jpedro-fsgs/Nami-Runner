import pygame
import random
from sys import exit
import json
from tkinter import Tk, Label, Frame, IntVar, simpledialog, messagebox
from tkinter.ttk import Entry, Button, Radiobutton, Scale
import operator
from pathlib import Path

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        layer_walk_1 = pygame.image.load(str(Path("graphics/passo1.png"))).convert_alpha()
        layer_walk_2 = pygame.image.load(str(Path("graphics/passo2.png"))).convert_alpha()
        self.walk = [layer_walk_1, layer_walk_2]
        self.index = 0
        
        self.image = self.walk[self.index]
        self.rect = self.image.get_rect(midbottom = (50,300))

        self.gravity = 0
        self.jump = pygame.image.load(str(Path("graphics/pulo.png"))).convert_alpha()

        self.jump_sound = pygame.mixer.Sound(str(Path('audio/jump.mp3')))
        self.jump_sound.set_volume(0.1)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w] or (joysticks and (joysticks[0].get_button(0) or joysticks[0].get_hat(0)[1] > 0))) and self.rect.bottom >= 300:
            self.gravity = -20
            self.jump_sound.play()

        if (keys[pygame.K_LEFT] or keys[pygame.K_a] or (joysticks and joysticks[0].get_axis(0) < -0.2) or (joysticks and joysticks[0].get_hat(0)[0] < 0)) and self.rect.left > 0:
            self.rect.x += -7
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d] or (joysticks and joysticks[0].get_axis(0) > 0.2) or (joysticks and joysticks[0].get_hat(0)[0] > 0)) and self.rect.right < 800:
            self.rect.x += 7

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom > 300:
            self.rect.bottom = 300

    def animation_state(self):
        if self.rect.bottom < 300:
            self.image = self.jump
        else:
            self.index += 0.1
            if self.index > len(self.walk): self.index = 0
            self.image = self.walk[int(self.index)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()



class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        # Type == True: Snail
        # Type == False: Fly
        super().__init__()

        self.type = type
        if type:
            snail_1 = pygame.image.load(str(Path("graphics/bombie.png"))).convert_alpha()
            snail_2 = pygame.image.load(str(Path("graphics/bombie2.png"))).convert_alpha()
            self.frames = [snail_1, snail_2]
            self.y_pos_baseline = 300
            self.special = not bool(random.randint(0,5))
        else:
            fly_1 = pygame.image.load(str(Path('graphics/miney.png'))).convert_alpha()
            fly_2 = pygame.image.load(str(Path('graphics/miney2.png'))).convert_alpha()
            fly_3 = pygame.image.load(str(Path('graphics/miney3.png'))).convert_alpha()
            fly_4 = pygame.image.load(str(Path('graphics/miney4.png'))).convert_alpha()
            self.frames = [fly_1, fly_2, fly_3, fly_4]
            self.y_pos_baseline = 201
            self.up_down = random.choice([1, -1])
        y_pos = self.y_pos_baseline
        
        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(bottomright=(random.randint(900, 1300), y_pos))

    def animation_state(self):
        if self.type:
            if self.special:
                self.image=self.frames[1]
            return
        else:
            self.animation_index += 0.05
        if int(self.animation_index) >= len(self.frames): 
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        current_vel = obstacle_vel if obstacle_vel < obstacle_max_vel else obstacle_max_vel
        if self.type and self.special and self.rect.x < 550 + random.randint(-100, 100):
            current_vel *= 2.5
        self.rect.x -= current_vel
        if self.type:
            pass
        else:
            if self.rect.y > self.y_pos_baseline + 30 or self.rect.y < self.y_pos_baseline - 100:
                self.up_down *= -1
            self.rect.y += (self.up_down * (current_vel/4))

        self.destroy()

    def destroy(self):
        if self.rect.right < 0:
            count_jump()
            self.kill()
    
def speed_up():
        global obstacle_vel
        obstacle_vel += obstacle_acel

def display_score():
    current_time = pygame.time.get_ticks() - start_time
    score_surf = second_font.render(f'{current_time/1000:0.1f}', True, third_color)
    score_rect = score_surf.get_rect(center = (400, 50))
    screen.blit(score_surf, score_rect)

def display_jumps():
    jumps_surf = count_font.render(f'{jumps}', True, third_color)
    jumps_rect = jumps_surf.get_rect(midright = (725, 50))
    screen.blit(jumps_surf, jumps_rect)

    difficulty_surf = count_font.render(f'{difficulty_name[difficulty]}', True, third_color)
    difficulty_rect = difficulty_surf.get_rect(midleft = (50, 50))
    screen.blit(difficulty_surf, difficulty_rect)

def count_jump():
    global jumps
    jumps += 1

def collision_sprites():
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        return True
    else:
        return False
    
def settings():  
    def update_entries():
        entry_obstacle_start_vel.delete(0, 'end')
        entry_obstacle_acel.delete(0, 'end')
        entry_obstacle_max_vel.delete(0, 'end')

        entry_obstacle_start_vel.insert(0, obstacle_start_vel)
        entry_obstacle_acel.insert(0, obstacle_acel)
        entry_obstacle_max_vel.insert(0, obstacle_max_vel)

    def update_difficulty():
        var_difficulty.set(difficulty)

    def set_settings():
        global obstacle_start_vel, obstacle_acel, obstacle_max_vel
        obstacle_start_vel = int(entry_obstacle_start_vel.get())
        obstacle_acel = float(entry_obstacle_acel.get())
        obstacle_max_vel = int(entry_obstacle_max_vel.get())
        
        gamedata['datasettings']['obstacle_start_vel'] = obstacle_start_vel
        gamedata['datasettings']['obstacle_acel'] = obstacle_acel
        gamedata['datasettings']['obstacle_max_vel'] = obstacle_max_vel

        update_entries()

        messagebox.showinfo(title='Parâmetros', message='Os Parâmetros foram atualizados!')


    def reset():
        global obstacle_start_vel, obstacle_acel, obstacle_max_vel, difficulty
        obstacle_acel = 0.003
        obstacle_start_vel = 4
        obstacle_max_vel = 16
        difficulty = 1

        gamedata['datasettings']['obstacle_start_vel'] = obstacle_start_vel
        gamedata['datasettings']['obstacle_acel'] = obstacle_acel
        gamedata['datasettings']['obstacle_max_vel'] = obstacle_max_vel

        gamedata['difficulty'] = difficulty

        update_entries()
        update_difficulty()

        messagebox.showinfo(title='Parâmetros', message='Os Parâmetros foram resetados!')
    
    def reset_highscore():
        global gamedata
        gamedata['highscore'] = [[0, '', 1]]
        messagebox.showinfo(title='Highscore', message='Highscores resetados!')

    def selectsong():
   
        global current_song, bgMusic
        if var.get() > len(bgMusic):
            pygame.mixer.stop()
            gamedata['music'] = len(bgMusic)
        else:
            pygame.mixer.stop()
            current_song
            current_song=pygame.mixer.Sound(bgMusic[var.get()])
            current_song.play(-1)
            current_song.set_volume(slider_value.get()/10)
            gamedata['music'] = var.get()

    def change_volume(self):
        if var.get() > len(bgMusic): return 0
        current_song.set_volume(slider_value.get()/10)
        gamedata["volume"] = slider_value.get()

    def change_difficulty():
        global difficulty
        difficulty = int(var_difficulty.get())
        gamedata["difficulty"] = difficulty


    janela = Tk()
    janela.title('Settings')
    janela.iconbitmap(str(Path("graphics/setts_icon.ico")))
    
    framevel = Frame(janela, bd=15)
    framevel.pack()
    label_vel_title = Label(framevel, text='Velocidade dos Obstáculos:')
    label_obstacle_start_vel = Label(framevel, text='Velocidade Inicial:')
    entry_obstacle_start_vel = Entry(framevel)
    label_obstacle_acel = Label(framevel, text='Aceleração:')
    entry_obstacle_acel = Entry(framevel)
    label_obstacle_max_vel = Label(framevel, text='Velocidade Máxima:')
    entry_obstacle_max_vel = Entry(framevel)

    button_confirm = Button(framevel, text='Inserir valores', command= set_settings)
    

    label_vel_title.grid(row=0,column=0, columnspan=2, padx=5, pady=5)
    label_obstacle_start_vel.grid(row=1,column=0, padx=5, pady=5)
    entry_obstacle_start_vel.grid(row=1,column=1, padx=5, pady=5)
    label_obstacle_acel.grid(row=2,column=0, padx=5, pady=5)
    entry_obstacle_acel.grid(row=2,column=1, padx=5, pady=5)
    label_obstacle_max_vel.grid(row=3,column=0, padx=5, pady=5)
    entry_obstacle_max_vel.grid(row=3,column=1, padx=5, pady=5)

    
    button_confirm.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
    
    update_entries()

    frame_difficulty = Frame(janela)
    frame_difficulty.pack()
    
    label_difficulty = Label(frame_difficulty, text='Dificuldade: ')
    var_difficulty = IntVar()
    difficulty_button1 = Radiobutton(frame_difficulty, text='Easy', variable=var_difficulty, value=0, command=change_difficulty)
    difficulty_button2 = Radiobutton(frame_difficulty, text='Normal', variable=var_difficulty, value=1, command=change_difficulty)
    difficulty_button3 = Radiobutton(frame_difficulty, text='Hard', variable=var_difficulty, value=2, command=change_difficulty)
    var_difficulty.set(difficulty)
    
    label_difficulty.pack(side='left')
    difficulty_button1.pack(side='left')
    difficulty_button2.pack(side='left')
    difficulty_button3.pack(side='left')
    

    frameoptions = Frame(janela, bd=15)
    frameoptions.pack()

    button_reset = Button(frameoptions, text='Resetar opções aos padrões', command= reset)
    button_reset_highscore = Button(frameoptions, text='Resetar Highscore', command= reset_highscore)
    
    button_reset.grid(row=0, column=0, padx=5, pady=5)
    button_reset_highscore.grid(row=1, column=0, padx=5, pady=5)
    

    framesongs = Frame(janela, bd=15)
    framesongs.pack()

    songstitle = Label(framesongs, text='Selecione a música')
    songstitle.pack()

    var = IntVar()

    songbutton1 = Radiobutton(framesongs, text='Street Race at Dawn', variable=var, value=0, command=selectsong)
    songbutton2 = Radiobutton(framesongs, text='Gathering the Dew', variable=var, value=1, command=selectsong)
    songbutton3 = Radiobutton(framesongs, text='Cryptic Puzzle', variable=var, value=2, command=selectsong)
    songbutton4 = Radiobutton(framesongs, text="None", variable=var, value=6, command=selectsong)

    var.set(gamedata['music'])

    songbutton1.pack(anchor='w')
    songbutton2.pack(anchor='w')
    songbutton3.pack(anchor='w')
    songbutton4.pack(anchor='w')

    slider_value = IntVar()
    slider_value.set(gamedata["volume"])
    
    volumelabel = Label(framesongs, text='Volume', pady=10)
    volume = Scale(framesongs, from_=0, to=10, orient='horizontal', variable=slider_value, command=change_volume)
    volumelabel.pack()
    volume.pack()

    janela.mainloop()



pygame.init()
pygame.joystick.init()
joysticks = []

screen = pygame.display.set_mode((800,400))
pygame.display.set_caption('Teudongi Runner')
icon = random.choice(['graphics/miney.png', 'graphics/bombie.png'])
pygame.display.set_icon(pygame.image.load(str(Path(icon))))
clock = pygame.time.Clock()
fonte1 = str(Path('font/Poppins-SemiBold.ttf'))
fonte2 = str(Path('font/Poppins-Light.ttf'))
main_font = pygame.font.Font(fonte1, 60)
second_font = pygame.font.Font(fonte2, 50)
third_font = pygame.font.Font(fonte1, 45)
count_font = pygame.font.Font(fonte2, 35)
main_color = (230, 126, 163)
second_color = (254, 254, 254)
third_color = (200, 254, 254)

setts = pygame.image.load(str(Path('graphics/setts.png'))).convert_alpha()
setts_rect = setts.get_rect(topleft=(715, 320))

game_active = False
start_time = 0

gamedata = {'highscore':[],
            'datasettings':{
                'obstacle_start_vel': 4,
                'obstacle_acel': 0.003,
                'obstacle_max_vel': 16},
            'music': 0,
            'difficulty': 1
            }

songslist = [str(Path('audio/Street Race at Dawn.mp3')),
            str(Path('audio/Gathering the Dew.mp3')),
            str(Path('audio/Cryptic Puzzle.mp3'))]

#Groups
player = pygame.sprite.GroupSingle()
obstacle_group = pygame.sprite.Group()

sky_surf = pygame.image.load(str(Path('graphics/Sky.png'))).convert()
ground_surf = pygame.image.load(str(Path('graphics/ground_move.png'))).convert()
ground_surf2 = pygame.image.load(str(Path('graphics/ground_move.png'))).convert()
ground_cord = 0
difficulty_name = ['EASY', 'NORMAL', 'HARD']

jumps = 0
just_start = True
odd_enemy = 2

with open('gamedata.json', 'r') as hs_file:
    gamedata = json.load(hs_file)

obstacle_start_vel = gamedata['datasettings']['obstacle_start_vel']
obstacle_acel = gamedata['datasettings']['obstacle_acel']
obstacle_max_vel = gamedata['datasettings']['obstacle_max_vel']
difficulty = gamedata['difficulty']

bgMusic = [path for path in songslist if path]

if gamedata['music'] < len(bgMusic):
    current_song=pygame.mixer.Sound(bgMusic[gamedata['music']])
    current_song.play(-1)
    current_song.set_volume(gamedata['volume']/10)
else:
    current_song = None

#Timer
start_tick = 2000
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, start_tick)

pygame.key.set_repeat(2)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            with open('gamedata.json', 'w') as hs_file:
                json.dump(gamedata, hs_file, indent=4)
            pygame.quit()
            exit()

        if event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            joysticks.clear()
            joysticks.append(joy)

        if not game_active and  ((event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (joysticks and joysticks[0].get_button(7))):
            start_time = pygame.time.get_ticks()
            game_active = True

        if game_active and event.type == obstacle_timer and pygame.time.get_ticks() - 1000 > start_time:
            # Type == True: Snail
            # Type == False: Fly
            obstacle_group.add(Obstacle(enemy_value:= random.randint(0, odd_enemy)))
            if difficulty > 0: 
                if enemy_value: obstacle_group.add(Obstacle(enemy_value:= random.randint(0,odd_enemy)))
                else: obstacle_group.add(Obstacle(1))
            if difficulty > 1:
                obstacle_group.add(Obstacle(enemy_value:= random.randint(0,odd_enemy)))
            if obstacle_vel < 24: pygame.time.set_timer(obstacle_timer, start_tick - int(obstacle_vel) * 70)
            else: pygame.time.set_timer(obstacle_timer, start_tick - 24 * 70)
        
    if game_active:

        speed_up()

        if ground_cord < -800: ground_cord=0
        screen.blit(sky_surf, (0,0))
        screen.blit(ground_surf, (ground_cord, 300))
        screen.blit(ground_surf2, (ground_cord + 800, 300))
        ground_cord -= obstacle_vel * 0.8
        
        display_score()
        display_jumps()
        
        if collision_sprites():
            ground_cord=0
            game_active = False
            current_score = pygame.time.get_ticks() - start_time
            if current_score > gamedata['highscore'][0][0]:
                player_name = simpledialog.askstring('HIGHSCORE', '\tDigite o seu nome (Até 10 caracteres)\t')
            else:
                player_name = ''
            gamedata['highscore'].append([current_score, player_name, difficulty])
            gamedata['highscore'] = sorted(gamedata['highscore'], key=operator.itemgetter(0), reverse=True)
            jumps = 0
            obstacle_group.empty()
            player.empty()
            obstacle_vel = obstacle_start_vel
            just_start = False

        player.draw(screen)
        player.update()

        obstacle_group.draw(screen)
        obstacle_group.update()

    else:
        
        player.add(Player())
        if just_start:
            screen.fill(main_color)
            
            screen.blit(pygame.image.load(str(Path("graphics/stand.png"))).convert_alpha(), (31,217))
            start_surf = main_font.render('PRESS ENTER TO START', True, second_color)
            start_rect = start_surf.get_rect(center = (400, 200))
            screen.blit(start_surf, start_rect)

            screen.blit(setts, setts_rect)
            if setts_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                settings()
        else:
            screen.fill(main_color)
            if gamedata["highscore"][0][0] == current_score: newrecord = '!!!'
            else: newrecord = ''
            yourscore_surf = main_font.render(f'YOUR SCORE: {current_score/1000:0.1f} {newrecord}', True, second_color)
            yourscore_rect = yourscore_surf.get_rect(center = (400, 150))
            highscore_surf = third_font.render(
                f'HIGHSCORE: {difficulty_name[gamedata["highscore"][0][2]]} {gamedata["highscore"][0][0]/1000:0.1f} {gamedata["highscore"][0][1].upper()[:10]}' if gamedata["highscore"][0][0] else '',
                True, second_color)
            highscore_rect = highscore_surf.get_rect(center = (400, 250))
            screen.blit(highscore_surf, highscore_rect)
            screen.blit(yourscore_surf, yourscore_rect)

            screen.blit(setts, setts_rect)
            if setts_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                settings()
        obstacle_vel = obstacle_start_vel
    
    pygame.display.update()
    clock.tick(60)