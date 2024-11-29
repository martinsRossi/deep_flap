import pygame
from pygame.locals import *
import random
import math
import time

pygame.init()

clock = pygame.time.Clock()
fps = 60

# Tamanho original
original_width = 864
original_height = 936

# Tamanho da tela desejado
screen_width = 576  # Largura desejada
screen_height = 624  # Altura desejada

# Cria uma superfície de tamanho original
virtual_screen = pygame.Surface((original_width, original_height))
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Deep Flappy')

# Define font
font = pygame.font.SysFont('Bauhaus 93', 60)

# Define cores
white = (255, 255, 255)

# Variáveis do jogo
difficulty = 1
ground_scroll = 0
scroll_speed = 4 * difficulty
swimming = False
game_over = False
pipe_gap = 180
pipe_frequency = 1500 / difficulty  
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
tempo_inicial = 5000
tempo_final = 10000
tempo_tubarao_tela = 3000

# Carrega imagens (mantendo os tamanhos originais)
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')
shark_img = pygame.image.load('img/tubarao.png').convert_alpha()

# Variáveis para controlar a exibição e movimento do tubarão
shark_visible = False
shark_x = -shark_img.get_width()  # Começa fora da tela à esquerda
shark_y = screen_height // 2  # Posiciona no meio da tela
shark_speed = 3  # Velocidade de movimento do tubarão
shark_start_time = 0
shark_direction = 1  # 1 para mover para a direita, -1 para mover para a esquerda
shark_time_at_100 = 0  # Para controlar os 3 segundos no x = 100
next_shark_appearance = pygame.time.get_ticks() + random.randint(tempo_inicial, tempo_final)  # random.randint(5000, 15000) Próxima aparição aleatória em 5-15 segundos
shark_appeared_time = None
score_increment_delay = 1000  # Tempo de espera para aumentar o score (em milissegundos)

#Pipes
# Configurações de oscilação ajustadas
pipe_oscillation_speed = 0.001  # Velocidade de oscilação mais lenta
pipe_amplitude = 45 # Amplitude da oscilação

score_movement_pipes = 0

# Função para desenhar texto na tela
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    virtual_screen.blit(img, (x, y))

def reset_game():
    global next_shark_appearance, shark_x, shark_visible, difficulty  # Adiciona a variável global para o tubarão e a dificuldade
    pipe_group.empty()
    flappy.rect.x = 300
    flappy.rect.y = 400
    score = 0

    # Reset do tubarão e dificuldade
    shark_visible = False  # Define o tubarão como invisível
    shark_x = -shark_img.get_width()  # Coloca o tubarão fora da tela
    next_shark_appearance = pygame.time.get_ticks() + random.randint(tempo_inicial, tempo_final)  # Define próximo aparecimento aleatório
    difficulty = 1  # Reseta a dificuldade para o nível inicial
    
    return score
    

# Função de controle do tubarão
def move_shark():
    global shark_visible, shark_x, shark_direction, shark_speed, next_shark_appearance, shark_time_at_100, shark_y
    global score_incremented, score, shark_appeared_time  # Adiciona as variáveis de controle do score e o momento de aparição

    # Verifica se o tubarão deve aparecer
    if not shark_visible and pygame.time.get_ticks() >= next_shark_appearance:
        shark_visible = True
        score_incremented = False  # Reseta para permitir o incremento do score
        shark_x = -shark_img.get_width()  # Começa fora da tela à esquerda
        shark_direction = 1  # Começa a mover para a direita
        shark_time_at_100 = 0  # Reseta o tempo quando ele começa a se mover para a direita
        shark_appeared_time = pygame.time.get_ticks()  # Define o momento de aparição
        next_shark_appearance = pygame.time.get_ticks() + random.randint(tempo_inicial, tempo_final)  # Próximo aparecimento aleatório

    # Se o tubarão estiver visível, ele pode oscilar no eixo Y enquanto se move
    if shark_visible:
        # Simula o movimento de natação com oscilação no eixo Y
        oscillation_speed = 0.02  # Velocidade da oscilação (mais suave)
        amplitude = 10  # Amplitude da oscilação
        shark_y = screen_height // 2 + amplitude * math.sin(pygame.time.get_ticks() * oscillation_speed)

        # Movimenta o tubarão para a direita até x = 50
        if shark_direction == 1:
            shark_x += shark_speed
            if shark_x >= 50:  # Se atingir x = 50, para por 3 segundos
                shark_direction = 0  # Fica parado por 3 segundos
                shark_time_at_100 = pygame.time.get_ticks()  # Marca o tempo

                # Incrementa o score apenas uma vez por aparição
                if not score_incremented:
                    score += 1  # Incrementa o score
                    score_incremented = True  # Marca como incrementado para não repetir

        # Fica parado por 3 segundos em x = 50
        elif shark_direction == 0:
            if pygame.time.get_ticks() - shark_time_at_100 > tempo_tubarao_tela:  # Fica parado por 3 segundos
                shark_direction = -1  # Começa a mover para a esquerda

        # Após o tempo parado, o tubarão começa a sair da tela
        elif shark_direction == -1:
            shark_x -= shark_speed
            if shark_x <= -shark_img.get_width():  # Quando sair da tela à esquerda
                shark_visible = False  # Marca como invisível até a próxima aparição

    return shark_visible, shark_x, shark_y

class Fish(pygame.sprite.Sprite):
    def __init__(self, x, y):  # Corrigido o nome do método para __init__
        pygame.sprite.Sprite.__init__(self)  # Corrigido para chamar o inicializador da classe Sprite
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f"img/bird{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        if swimming:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < original_height - 168:
                self.rect.y += int(self.vel)
        if not game_over:
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
            flap_cooldown = 5
            self.counter += 1
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)  # Initialize the Sprite class
        self.image = pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()
        self.initial_y = y  # Store the initial y position for oscillation
        
        if position == 1:  # Top pipe
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2) - 20]
        elif position == -1:  # Bottom pipe
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

        self.position = position  # Store the position of the pipe (1 for top, -1 for bottom)

    def update(self):
        # Movimento horizontal
        self.rect.x -= scroll_speed

        # Movimento de oscilação vertical quando o score é maior ou igual a 10
        if score >= score_movement_pipes:
            # Calcula o deslocamento vertical com uma velocidade maior para aumentar o movimento
            oscillation = pipe_amplitude * math.sin(pygame.time.get_ticks() * pipe_oscillation_speed)
            if self.position == 1:
                # Para o cano superior, aplica o deslocamento para cima
                self.rect.bottom = self.initial_y - int(pipe_gap / 2) + oscillation - 20
            elif self.position == -1:
                # Para o cano inferior, aplica o deslocamento para baixo
                self.rect.top = self.initial_y + int(pipe_gap / 2) + oscillation

        # Remove o cano quando ele sair da tela
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):  # Correct constructor name
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        scaled_pos = (int(pos[0] * (original_width / screen_width)), int(pos[1] * (original_height / screen_height)))
        if self.rect.collidepoint(scaled_pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        virtual_screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

class Shark(pygame.sprite.Sprite):
    def _init_(self):
        pygame.sprite.Sprite._init_(self)
        self.image = shark_img
        self.rect = self.image.get_rect()
        # Random vertical position
        self.rect.y = random.randint(0, screen_height - self.rect.height)
        self.rect.x = -self.rect.width  # Start off-screen left
        self.spawn_time = pygame.time.get_ticks()  # Time of appearance

    def update(self):
        self.rect.x += 5  # Adjust speed as needed
        if pygame.time.get_ticks() - self.spawn_time > 3000:  # 3 seconds
            self.kill()  # Remove after 3 seconds

pipe_group = pygame.sprite.Group()
fish_group = pygame.sprite.Group()
shark_group = pygame.sprite.Group()

flappy = Fish(350, 400)
fish_group.add(flappy)  # Adiciona a instância 'flappy' ao grupo
button = Button(original_width // 2 - 50, original_height // 2 - 100, button_img)

# Loop principal
difficulty = 1  # Inicializa a dificuldade
run = True
game_over = True
while run:
    clock.tick(fps)
    virtual_screen.blit(bg, (0, 0))

    # Atualize a rolagem e frequência dos canos conforme a dificuldade
    scroll_speed = 4 * difficulty  # Aumenta a velocidade da rolagem com a dificuldade
    pipe_frequency = 1500 / difficulty  # Aumenta a frequência dos canos com a dificuldade

    # Desenho e atualização dos elementos principais
    pipe_group.draw(virtual_screen)
    fish_group.draw(virtual_screen)
    fish_group.update()

    # Desenho do solo
    virtual_screen.blit(ground_img, (ground_scroll, original_height - 168))

    # Atualização da pontuação, dps olhamos aqui
    if len(pipe_group) > 0:
        fish = fish_group.sprites()[0]
        pipe = pipe_group.sprites()[0]

        # Checa se o pássaro está dentro do cano e ainda não passou por ele
        if fish.rect.left > pipe.rect.left and fish.rect.right < pipe.rect.right and not pass_pipe:
            pass_pipe = True
            print("Pássaro entrou no cano. Aguardando saída para contar score.")

        # Incrementa o score ao passar pelo cano
        if pass_pipe and fish.rect.left > pipe.rect.right:
            score += 1
            pass_pipe = False  # Reseta para o próximo cano
            print(f"Score incrementado: {score}")

    # Atualiza o texto do score na tela
    draw_text(str(score), font, white, original_width // 2, 20)

    # Look for collision
    if pygame.sprite.groupcollide(fish_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
    # Once the fish has hit the ground it's game over and no longer swimming
    if flappy.rect.bottom >= 768:
        game_over = True
        swimming = False

    # Controle do estado do jogo e movimento dos canos
    if swimming and not game_over:
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-screen_height // 3, screen_height // 3)
            btm_pipe = Pipe(original_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(original_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now
        pipe_group.update()
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        # Movimenta o tubarão
        shark_visible, shark_x, shark_y = move_shark()

        # Se o tubarão aparecer, altere a dificuldade
        if shark_visible and difficulty == 1:
            difficulty = 2
        # Checa se já passou 1 segundo desde que o tubarão apareceu
            if pygame.time.get_ticks() - shark_appeared_time >= 3000:
                score += 1  # Aumenta o score depois de 1 segundo do aparecimento do tubarão
                print("Dificuldade aumentada para:", difficulty)  # Apenas para debug

        # Exibe o tubarão na tela se ele estiver visível
        if shark_visible:
            virtual_screen.blit(shark_img, (shark_x, shark_y))

        # Se o tubarão desaparecer, reseta a dificuldade
        if not shark_visible and difficulty == 2:
            difficulty = 1
            print("Dificuldade resetada para:", difficulty)  # Apenas para debug

    # Condição de Game Over e botão de reiniciar
    if game_over:
        # Reseta o tubarão quando o jogo termina
        shark_x = -shark_img.get_width()
        next_shark_appearance = pygame.time.get_ticks() + random.randint(tempo_inicial, tempo_final)

        # Desenha o botão de reiniciar
        if button.draw():
            game_over = False
            score = reset_game()

    # Eventos do mouse e teclado
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not swimming and not game_over:
            swimming = True

    # Escala a tela e atualiza a exibição
    scaled_surface = pygame.transform.scale(virtual_screen, (screen_width, screen_height))
    screen.blit(scaled_surface, (0, 0))
    pygame.display.update()

pygame.quit()
