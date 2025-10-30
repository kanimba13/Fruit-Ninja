import pygame
import random

pygame.init()
pygame.mixer.init()
def menu():
    ancho,alto=600,600
    pantalla=pygame.display.set_mode((ancho,alto))
    pygame.display.set_caption("Cortar Frutas")
    fondo = pygame.image.load("Multimedia/Imagenes/menu.png").convert()
    fondo = pygame.transform.scale(fondo, (ancho, alto))
    pantalla.blit(fondo, (0, 0))
    running=True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
        if pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if 85 <= mouse_x <= 520 and 65 <= mouse_y <= 205:
                pygame.time.delay(200)
                return "juego"
            if 85 <= mouse_x <= 520 and 405 <= mouse_y <= 550:
                return "salir"
        pygame.display.flip()
        clock.tick(60)
def juego():
    screen=pygame.display.set_mode((600, 600))
    clock=pygame.time.Clock()
    running=True
    pared=pygame.image.load("Multimedia/Imagenes/Wood.jpg").convert()
    pared=pygame.transform.scale(pared, (600, 600))
    cortar_sound=pygame.mixer.Sound("Multimedia/Audio/KnifeSlice.ogg")
    exit=pygame.image.load("Multimedia/Imagenes/exitRight.png").convert_alpha()
    pos_mouse=[]
    espesor=10
    color_linea=(255,0,0)
    pl = []
    for i in range(5):
        x = random.randint(30, 570)
        y = random.randint(30, 570)
        r = 15
        pl.append(pygame.Rect(x - r, y - r, r * 2, r * 2))
    cambio_timer = 0
    timer_especial = 0
    pl_e = None
    puntos=0
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            if event.type==pygame.MOUSEMOTION:
                pos_mouse.append(event.pos)
            if event.type==pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if 550 <= mouse_x <= 590 and 10 <= mouse_y <= 50:
                    pygame.time.delay(200)
                    return "menu"
        screen.blit(pared, (0, 0))
        screen.blit(exit, (550, 10))
        cambio_timer += clock.get_time()
        timer_especial += clock.get_time()
        if cambio_timer > 2000:
            pl.clear()
            for i in range(5):
                x = random.randint(30, 570)
                y = random.randint(30, 570)
                r = 15
                pl.append(pygame.Rect(x - r, y - r, r * 2, r * 2))
            cambio_timer = 0
        if timer_especial >= 10000 and not pl_e:
            pl_e = pygame.Rect(random.randint(30, 570) - 15, random.randint(30, 570) - 15, 30, 30)
            timer_especial = 0
        for p in pl:
            pygame.draw.ellipse(screen, (0, 0, 255), p)
        if pl_e:
            pygame.draw.rect(screen, (255, 0, 0), pl_e)
        for pos in pos_mouse:
            if len(pos_mouse)>7:
                pos_mouse.pop(0)
        if pygame.mouse.get_pressed()[0]:
            if len(pos_mouse)>1:
                linea=pygame.draw.lines(screen, color_linea, False, pos_mouse, espesor)
        else:
            pos_mouse.clear()
            linea=None
        if linea:
            for p in pl[:]:
                if linea.colliderect(p):
                    pl.remove(p)
                    cortar_sound.play()
                    puntos += 1
                    break
            if pl_e and linea.colliderect(pl_e):
                pl_e=None
                cortar_sound.play()
                puntos += 5
        fuente = pygame.font.Font(None, 36)
        texto = fuente.render("Puntos: {}".format(puntos), True, (0, 0, 0))
        screen.blit(texto, (10, 10))
        pygame.display.flip()
        clock.tick(120)
    return
def main():
    pantalla_actual = "menu"
    while True:
        if pantalla_actual == "menu":
            pantalla_actual = menu()
        elif pantalla_actual == "juego":
            pantalla_actual = juego()
        elif pantalla_actual == "salir":
            break
    pygame.quit()
main()