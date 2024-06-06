import pygame
import random
from sys import exit
import json
from tkinter import DoubleVar, Tk, Label, Frame, IntVar, simpledialog, messagebox
from tkinter.ttk import Entry, Button, Radiobutton, Scale
import operator
from pathlib import Path

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.stand = pygame.image.load(str(Path(__file__).parent / "graphics/nami_stand.png")).convert_alpha()
        layer_walk_1 = pygame.image.load(str(Path(__file__).parent / "graphics/nami_passo1.png")).convert_alpha()
        layer_walk_2 = pygame.image.load(str(Path(__file__).parent / "graphics/nami_passo2.png")).convert_alpha()
        self.walk = [layer_walk_1, layer_walk_2]
        self.index = 0
        
        self.image = self.walk[self.index]
        self.rect = self.image.get_rect(midbottom = (400,300))

        self.gravity = 0
        self.jump = pygame.image.load(str(Path(__file__).parent / "graphics/nami_pulo.png")).convert_alpha()

        self.jump_sound = pygame.mixer.Sound(str(Path(__file__).parent / 'audio/jump.mp3'))
        self.jump_sound.set_volume(0.1)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w] or (joysticks and (joysticks[0].get_button(0) or joysticks[0].get_hat(0)[1] > 0)))and self.rect.bottom >= 300:
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
            snail_1 = pygame.image.load(str(Path(__file__).parent / "graphics/bombie.png")).convert_alpha()
            snail_2 = pygame.image.load(str(Path(__file__).parent / "graphics/bombie2.png")).convert_alpha()
            self.frames = [snail_1, snail_2]
            self.y_pos_baseline = 300
            y_pos = self.y_pos_baseline
            self.special = [not bool(random.randint(0,6))] #0: vermelho >=1: normal
            if self.special[0]: self.special.append(random.randint(450, 650))
        else:
            fly_1 = pygame.image.load(str(Path(__file__).parent / 'graphics/miney.png')).convert_alpha()
            fly_2 = pygame.image.load(str(Path(__file__).parent / 'graphics/miney2.png')).convert_alpha()
            fly_3 = pygame.image.load(str(Path(__file__).parent / 'graphics/miney3.png')).convert_alpha()
            fly_4 = pygame.image.load(str(Path(__file__).parent / 'graphics/miney4.png')).convert_alpha()
            self.frames = [fly_1, fly_2, fly_3, fly_4]
            self.y_pos_baseline = 201
            self.special = [random.randint(0,6)] #0: black 1: fast >=2: normal
            if self.special[0] <= 2: 
                self.special.append(random.randint(550, 700))
                if self.special[0] == 0:
                    self.release_time = 100
            y_pos = self.y_pos_baseline - random.randint(-15, 50)
            self.up_down = random.choice([1, -1])
        
        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(bottomright=(random.randint(800, 1500), y_pos))
        # self.rect = self.image.get_rect(bottomright=(random.randint(900, 1300), y_pos))

    def animation_state(self):
        if self.type:
            if self.special[0]:
                self.image=self.frames[1]
            return
        if self.special[0] == 1:
            self.image=self.frames[2]
            return
        if self.special[0] == 0:
            if self.rect.x < self.special[1] and self.release_time > 0:
                self.release_time -=1
                self.animation_index += 0.1
            if self.release_time <= 0:
                self.image = self.frames[3]
                return
        if int(self.animation_index) >= 2: 
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        current_vel = obstacle_vel if obstacle_vel < obstacle_max_vel else obstacle_max_vel
        if self.type and self.special[0] and self.rect.x < self.special[1]:
            current_vel *= 2.1
        
        if not self.type and self.special[0] == 1:
            current_vel *= 1.4

        if not self.type: 
            if self.special[0] == 0: 
                if self.rect.x < self.special[1]:
                    current_vel = 0
                if self.release_time <= 0:
                    current_vel = obstacle_vel if obstacle_vel < obstacle_max_vel else obstacle_max_vel
                    self.up_down = 0
                    current_vel *= 2

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

    difficulty_surf = count_font.render(f'{difficulty.upper()}', True, third_color)
    difficulty_rect = difficulty_surf.get_rect(midleft = (50, 50))
    screen.blit(difficulty_surf, difficulty_rect)

def count_jump():
    global jumps
    jumps += 1

def collision_sprites():
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False, pygame.sprite.collide_mask):
        return True
    return False
    
def show_highscore_list(diff):
    return[f'{score[0]/1000:0.1f} {score[1].lower()[:10]}'for score in gamedata["highscore"][diff] if score[0]][:5]

def settings():  
    def update_entries():
        entry_obstacle_start_vel.delete(0, 'end')
        entry_obstacle_acel.delete(0, 'end')
        entry_obstacle_max_vel.delete(0, 'end')
        entry_nome.delete(0, 'end')

        entry_obstacle_start_vel.insert(0, obstacle_start_vel)
        entry_obstacle_acel.insert(0, obstacle_acel)
        entry_obstacle_max_vel.insert(0, obstacle_max_vel)
        entry_nome.insert(0, player_name)

    def update_difficulty():
        var_difficulty.set(difficulty_name.index(difficulty))

    def set_settings():
        global obstacle_start_vel, obstacle_acel, obstacle_max_vel
        try:
            obstacle_start_vel = int(entry_obstacle_start_vel.get())
            obstacle_acel = float(entry_obstacle_acel.get())
            obstacle_max_vel = int(entry_obstacle_max_vel.get())
        except ValueError:
            messagebox.showerror(title='Parâmetros Inválidos', message='Parâmetros Inválidos! Os Parâmetros não foram atualizados.')
            update_entries()
            return
        
        gamedata['datasettings']['obstacle_start_vel'] = obstacle_start_vel
        gamedata['datasettings']['obstacle_acel'] = obstacle_acel
        gamedata['datasettings']['obstacle_max_vel'] = obstacle_max_vel

        update_entries()

        messagebox.showinfo(title='Parâmetros', message='Os Parâmetros foram atualizados!')


    def reset():
        global obstacle_start_vel, obstacle_acel, obstacle_max_vel, difficulty
        obstacle_acel = 0.002
        obstacle_start_vel = 4
        obstacle_max_vel = 16
        difficulty = "normal"

        gamedata['datasettings']['obstacle_start_vel'] = obstacle_start_vel
        gamedata['datasettings']['obstacle_acel'] = obstacle_acel
        gamedata['datasettings']['obstacle_max_vel'] = obstacle_max_vel

        gamedata['difficulty'] = difficulty

        update_entries()
        update_difficulty()

        messagebox.showinfo(title='Parâmetros', message='Os Parâmetros foram resetados!')
    
    def reset_highscore():
        global gamedata
        gamedata['highscore'] = {'easy': [[0, '']],
                                 'normal': [[0, '']],
                                 'hard': [[0, '']]}
        messagebox.showinfo(title='Highscore', message='Highscores resetados!')

    def selectsong():
   
        global current_song, bgMusic
        
        if var.get() >= len(bgMusic):
            pygame.mixer.stop()
            gamedata['music'] = len(bgMusic)
        else:
            pygame.mixer.stop()
            current_song
            current_song=pygame.mixer.Sound(bgMusic[var.get()])
            current_song.play(-1)
            current_song.set_volume(slider_value.get())
            gamedata['music'] = var.get()

    def change_volume(volume):
        if var.get() >= len(bgMusic): return 0
        current_song.set_volume(float(volume))
        gamedata["volume"] = volume

    def change_difficulty():
        global difficulty
        difficulty = difficulty_name[int(var_difficulty.get())]
        gamedata["difficulty"] = difficulty

    def change_name():
        global player_name, gamedata
        player_name = entry_nome.get()
        gamedata["name"] = player_name
        update_entries()
        messagebox.showinfo(title='Nome', message=f'Nome alterado para {player_name}!')

    janela = Tk()
    janela.title('Settings')
    janela.iconbitmap(str(Path(__file__).parent / "graphics/setts_icon.ico"))
    
    frame_nome = Frame(janela, bd=15)
    label_nome = Label(frame_nome, text=" Alterar Nome:")
    entry_nome = Entry(frame_nome)
    button_nome = Button(frame_nome, text="Inserir Nome", command=change_name)

    frame_nome.pack()
    label_nome.pack(padx=5, pady=5)
    entry_nome.pack(padx=5, pady=5)
    button_nome.pack(padx=5, pady=5)
    
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

    
    button_confirm.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
    
    update_entries()

    frame_difficulty = Frame(janela)
    frame_difficulty.pack()
    
    label_difficulty = Label(frame_difficulty, text='Dificuldade: ')
    var_difficulty = IntVar()
    difficulty_button1 = Radiobutton(frame_difficulty, text='Easy', variable=var_difficulty, value=0, command=change_difficulty)
    difficulty_button2 = Radiobutton(frame_difficulty, text='Normal', variable=var_difficulty, value=1, command=change_difficulty)
    difficulty_button3 = Radiobutton(frame_difficulty, text='Hard', variable=var_difficulty, value=2, command=change_difficulty)
    var_difficulty.set(difficulty_name.index(difficulty))
    
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
    songbutton2 = Radiobutton(framesongs, text='Dew Gathering', variable=var, value=1, command=selectsong)
    songbutton3 = Radiobutton(framesongs, text='Cryptic Puzzle', variable=var, value=2, command=selectsong)
    songbutton4 = Radiobutton(framesongs, text="None", variable=var, value=3, command=selectsong)

    var.set(gamedata['music'])

    songbutton1.pack(anchor='w')
    songbutton2.pack(anchor='w')
    songbutton3.pack(anchor='w')
    songbutton4.pack(anchor='w')

    slider_value = DoubleVar()
    slider_value.set(gamedata["volume"])
    
    volumelabel = Label(framesongs, text='Volume', pady=10)
    volume = Scale(framesongs, from_=0, to=1, orient='horizontal', variable=slider_value, command=change_volume)
    volumelabel.pack()
    volume.pack()

    janela.mainloop()

pygame.init()
pygame.joystick.init()
joysticks = []

screen = pygame.display.set_mode((800,400))
pygame.display.set_caption('Nami Runner')
icon_path = random.choice(['miney.png', 'bombie.png'])
icon = pygame.image.load(str(Path(__file__).parent / 'graphics' / icon_path))
pygame.display.set_icon(icon)
clock = pygame.time.Clock()
fonte1 = str(Path(__file__).parent / 'font/Poppins-SemiBold.ttf')
fonte2 = str(Path(__file__).parent / 'font/Poppins-Light.ttf')
main_font = pygame.font.Font(fonte1, 60)
second_font = pygame.font.Font(fonte2, 50)
third_font = pygame.font.Font(fonte1, 45)
count_font = pygame.font.Font(fonte2, 35)
main_color = (230, 126, 163)
second_color = (254, 254, 254)
third_color = (200, 254, 254)
highscore_title_font = pygame.font.Font(fonte1, 50)
highscore_diff_titles_font = pygame.font.Font(fonte2, 40)
highscore_results_font = pygame.font.Font(fonte2, 30)
player_name_font = highscore_results_font = pygame.font.Font(fonte2, 20)

setts = pygame.image.load(str(Path(__file__).parent / 'graphics/setts.png')).convert_alpha()
setts_rect = setts.get_rect(topleft=(715, 320))

arrow = pygame.image.load(str(Path(__file__).parent / 'graphics/arrow.png')).convert_alpha()
arrow_rect = arrow.get_rect(bottomright=(85, 80))


highscore_icon = pygame.image.load(str(Path(__file__).parent / 'graphics/highscore.png')).convert_alpha()
highscore_icon_rect = highscore_icon.get_rect(topright=(85, 320))

game_active = False
start_time = 0
restart = False

gamedata = {'highscore':{'easy': [[0, '']],
                         'normal': [[0, '']],
                         'hard': [[0, '']]},
            'datasettings':{
                'obstacle_start_vel': 4,
                'obstacle_acel': 0.002,
                'obstacle_max_vel': 16},
            'music': 1,
            'volume': 0.3,
            'difficulty': "normal",
            'name': ''
            }
songslist = [str(Path(__file__).parent / 'audio/Street Race at Dawn.mp3'),
            str(Path(__file__).parent / 'audio/Dew Gathering.mp3'),
            str(Path(__file__).parent / 'audio/Cryptic Puzzle.mp3')]

#Groups
player = pygame.sprite.GroupSingle()
obstacle_group = pygame.sprite.Group()

sky_surf = pygame.image.load(str(Path(__file__).parent / 'graphics/Sky.png')).convert()
ground_surf = pygame.image.load(str(Path(__file__).parent / 'graphics/ground_move.png')).convert()
ground_surf2 = pygame.image.load(str(Path(__file__).parent / 'graphics/ground_move.png')).convert()
ground_cord = 0

jumps = 0
just_start = True
in_highscore = False
odd_enemy = 2


if not Path(Path(__file__).parent / 'gamedata.json').exists():
    with open('gamedata.json', 'w') as hs_file:
                    json.dump(gamedata, hs_file, indent=4)

with open(Path(Path(__file__).parent / 'gamedata.json'), 'r') as hs_file:
    gamedata = json.load(hs_file)

player_name = gamedata["name"]
if not player_name:
    player_name = simpledialog.askstring('Nome', '\tDigite o seu nome (Até 10 caracteres)\t')
    if not player_name: player_name = ''
    gamedata["name"] = player_name


obstacle_start_vel = gamedata['datasettings']['obstacle_start_vel']
obstacle_acel = gamedata['datasettings']['obstacle_acel']
obstacle_max_vel = gamedata['datasettings']['obstacle_max_vel']
difficulty = gamedata['difficulty']
difficulty_name = ['easy', 'normal', 'hard']

bgMusic = [path for path in songslist if path]

if gamedata['music'] < len(bgMusic):
    current_song=pygame.mixer.Sound(bgMusic[gamedata['music']])
    current_song.play(-1)
    current_song.set_volume(float(gamedata['volume']))
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

        if not in_highscore and not game_active and  ((event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (joysticks and joysticks[0].get_button(7))):
            start_time = pygame.time.get_ticks()
            game_active = True

        # if (event.type == pygame.KEYDOWN and event.key == pygame.K_x):
        #     restart = True

        if game_active and event.type == obstacle_timer and pygame.time.get_ticks() - 1000 > start_time:
            # Type == True: Snail
            # Type == False: Fly
            obstacle_group.add(Obstacle(enemy_value:= random.randint(0, odd_enemy)))
            if difficulty_name.index(difficulty) > 0: 
                if enemy_value: obstacle_group.add(Obstacle(enemy_value:= random.randint(0,odd_enemy)))
                else: obstacle_group.add(Obstacle(1))
            if difficulty_name.index(difficulty) > 1:
                obstacle_group.add(Obstacle(enemy_value:= random.randint(0,odd_enemy)))
            if obstacle_vel < 24: pygame.time.set_timer(obstacle_timer, start_tick - int(obstacle_vel) * 70)
            else: pygame.time.set_timer(obstacle_timer, start_tick - 24 * 70)
        
    if game_active and not in_highscore:

        speed_up()

        if ground_cord < -800: ground_cord=0
        screen.blit(sky_surf, (0,0))
        screen.blit(ground_surf, (ground_cord, 300))
        screen.blit(ground_surf2, (ground_cord + 800, 300))
        ground_cord -= obstacle_vel * 0.8
        
        display_score()
        display_jumps()
        
        player.draw(screen)
        player.update()
        
        obstacle_group.draw(screen)
        obstacle_group.update()

        if collision_sprites():
            restart = False
            ground_cord=0
            game_active = False
            current_score = pygame.time.get_ticks() - start_time
            current_difficulty = difficulty
            gamedata['highscore'][difficulty].append([current_score, player_name])
            gamedata['highscore'][difficulty] = sorted(gamedata['highscore'][difficulty], key=operator.itemgetter(0), reverse=True)
            jumps = 0
            obstacle_group.empty()
            player.empty()
            obstacle_vel = obstacle_start_vel
            just_start = False


    else:
        
        if in_highscore:
            screen.fill(main_color)
            highscore_title_surf = highscore_title_font.render('HIGHSCORES', True, second_color)
            highscore_title_rect = highscore_title_surf.get_rect(center = (400, 50))
            
            easy_surf = highscore_diff_titles_font.render('EASY', True, second_color)
            easy_rect = easy_surf.get_rect(center = (150, 120))
            
            normal_surf = highscore_diff_titles_font.render('NORMAL', True, second_color)
            normal_rect = normal_surf.get_rect(center = (400, 120))
            
            hard_surf = highscore_diff_titles_font.render('HARD', True, second_color)
            hard_rect = hard_surf.get_rect(center = (650, 120))
            
            cord = 190
            for result in show_highscore_list("easy"):
                easy_result_surf = highscore_results_font.render(result, True, second_color)
                easy_result_rect = easy_result_surf.get_rect(center = (150, cord))
                screen.blit(easy_result_surf, easy_result_rect)
                cord += 40
                
            cord = 190
            for result in show_highscore_list("normal"):
                normal_result_surf = highscore_results_font.render(result, True, second_color)
                normal_result_rect = normal_result_surf.get_rect(center = (400, cord))
                screen.blit(normal_result_surf, normal_result_rect)
                cord += 40
            
            cord = 190
            for result in show_highscore_list("hard"):
                hard_result_surf = highscore_results_font.render(result, True, second_color)
                hard_result_rect = hard_result_surf.get_rect(center = (650, cord))
                screen.blit(hard_result_surf, hard_result_rect)
                cord += 40

            screen.blit(arrow, arrow_rect)
            screen.blit(highscore_title_surf, highscore_title_rect)
            screen.blit(easy_surf, easy_rect)
            screen.blit(normal_surf, normal_rect)
            screen.blit(hard_surf, hard_rect)

            if arrow_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                in_highscore = False
        else:
            player.add(Player())
            if just_start:
                screen.fill(main_color)
                screen.blit(pygame.image.load(str(Path(__file__).parent / "graphics/nami_stand.png")).convert_alpha(), (381,217))
                
                player_name_surf = player_name_font.render(f'{player_name[:10].lower()}', True, second_color)
                player_name_rect = player_name_surf.get_rect(midright = (785, 27))
                screen.blit(player_name_surf, player_name_rect)
                
                start_surf = main_font.render('PRESS ENTER TO START', True, second_color)
                start_rect = start_surf.get_rect(center = (400, 150))
                screen.blit(start_surf, start_rect)

                screen.blit(setts, setts_rect)
                if setts_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    settings()
                screen.blit(highscore_icon, highscore_icon_rect)
                if highscore_icon_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    in_highscore = True
            else:
                screen.fill(main_color)
                if gamedata["highscore"][current_difficulty][0][0] == current_score: newrecord = '!!!'
                else: newrecord = ''
                
                player_name_surf = player_name_font.render(f'{player_name[:10].lower()}', True, second_color)
                player_name_rect = player_name_surf.get_rect(midright = (785, 27))
                screen.blit(player_name_surf, player_name_rect)
                
                yourscore_surf = main_font.render(f'YOUR SCORE: {current_score/1000:0.1f} {newrecord}', True, second_color)
                yourscore_rect = yourscore_surf.get_rect(center = (400, 125))

                highscore_surf1 = third_font.render('HIGHSCORE:', True, second_color)
                highscore_surf2 = third_font.render(
                    f'{current_difficulty.upper()} {gamedata["highscore"][current_difficulty][0][0]/1000:0.1f} {gamedata['highscore'][current_difficulty][0][1].upper()[:10]}' if gamedata['highscore'][current_difficulty][0][0] else '',
                    True, second_color)
                highscore_rect1 = highscore_surf1.get_rect(center = (400, 225))
                highscore_rect2 = highscore_surf2.get_rect(center = (400, 275))
                screen.blit(highscore_surf1, highscore_rect1)
                screen.blit(highscore_surf2, highscore_rect2)
                screen.blit(yourscore_surf, yourscore_rect)

                screen.blit(setts, setts_rect)
                if setts_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    settings()
                screen.blit(highscore_icon, highscore_icon_rect)
                if highscore_icon_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    in_highscore = True
                
            
        obstacle_vel = obstacle_start_vel
    
    pygame.display.update()
    clock.tick(60)
