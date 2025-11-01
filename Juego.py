import pygame
import random
import cv2
import mediapipe as mp
import numpy as np

pygame.init()
pygame.mixer.init()
gravedad =2000.0
rozamiento = 0.5
pl = []
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
def crear_bola(x, y, vx, vy, r=14):
    color = (random.randint(1,255), random.randint(1,255), random.randint(1,255))
    pl.append({
        "x": float(x), "y": float(y),   # posición en float para precisión
        "vx": float(vx), "vy": float(vy),  # velocidad
        "r": r, "color": color
    })
def actualizar_bolas(dt):
    """Integra la física de todas las bolas en dt segundos."""
    # Rozamiento aplicado como decaimiento exponencial por segundo
    drag = rozamiento ** dt
    for b in pl:
        # 1) fuerzas -> aceleraciones: solo gravedad en Y
        b["vy"] += gravedad * dt        # [m/s] = [m/s^2]*[s]            v = v_0 +a*t

        # 2) rozamiento (reduce gradualmente la velocidad)
        b["vx"] *= drag
        b["vy"] *= drag

        # 3) integración de posición
        b["x"]  += b["vx"] * dt        #[m] = [m/s]*[s]            x = x_0 + vt
        b["y"]  += b["vy"] * dt

        r = b["r"]
def juego():
    hay_pelotas= False
    screen=pygame.display.set_mode((600, 600))
    clock=pygame.time.Clock()
    running=True
    pared=pygame.image.load("Multimedia/Imagenes/Wood.jpg").convert()
    pared=pygame.transform.scale(pared, (600, 600))
    cortar_sound=pygame.mixer.Sound("Multimedia/Audio/KnifeSlice.ogg")
    exit=pygame.image.load("Multimedia/Imagenes/exitRight.png").convert_alpha()
    pos_mouse=[]
    # Inicializar MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    # Inicializar la cámara
    cap = cv2.VideoCapture(0)
    espesor=10
    color_linea=(255,0,0)
    cambio_timer = 0
    timer_especial = 0
    pl_e = None
    puntos=0
    duracion=60000
    is_pinching = False
    while running:
        dt = clock.tick(120) / 1000.0
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            if event.type==pygame.MOUSEMOTION:
                #pos_mouse.append(event.pos)
                pass
            if event.type==pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if 550 <= mouse_x <= 590 and 10 <= mouse_y <= 50:
                    pygame.time.delay(200)
                    return "menu"
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
    
        # Convertir la imagen a RGB (MediaPipe requiere RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Procesar el frame para detectar manos
        results = hands.process(rgb_frame)


        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Obtener las coordenadas de los dedos pulgar e índice
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]

                # Calcular la distancia entre los dedos
                distance = np.sqrt(
                    (thumb_tip.x - index_tip.x)**2 + 
                    (thumb_tip.y - index_tip.y)**2
                )

                # Si los dedos están cerca (pinching)
                if distance < 0.2:  # Ajusta el valor
                    is_pinching = True
                    # Mover el cubo según la posición del dedo índice
                    pos_mouse.append((int(index_tip.x * 600), int(index_tip.y * 600)))
                else:
                    is_pinching = False
        actualizar_bolas(dt)
        screen.blit(pared, (0, 0))
        screen.blit(exit, (550, 10))
        cambio_timer += clock.get_time()
        timer_especial += clock.get_time()
        if cambio_timer > 2000:
            pl.clear()
            for i in range(10):
                x = random.randint(30, 570)
                y = 610
                vx = 0
                vy = random.uniform(-1000, -1800)
                crear_bola(x, y, vx, vy)
            cambio_timer = 0
            if not hay_pelotas:
                tiempo_inicio=pygame.time.get_ticks()
                hay_pelotas = True
        if timer_especial >= 10000 and not pl_e:
            pl_e = pygame.Rect(random.randint(30, 570) - 15, random.randint(30, 570) - 15, 30, 30)
            timer_especial = 0
        for p in pl:
            pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), p["r"])
        if pl_e:
            pygame.draw.rect(screen, (255, 0, 0), pl_e)
        for pos in pos_mouse:
            if len(pos_mouse)>7:
                pos_mouse.pop(0)
        if is_pinching:
            if len(pos_mouse)>1:
                linea=pygame.draw.lines(screen, color_linea, False, pos_mouse, espesor)
        else:
            pos_mouse.clear()
            linea=None
        if linea:
            for b in pl[:]:
                rect_b = pygame.Rect(b["x"]-b["r"], b["y"]-b["r"], b["r"]*2, b["r"]*2)
                if linea.colliderect(rect_b):
                    pl.remove(b)
                    cortar_sound.play()
                    puntos += 1
                    break
            if pl_e and linea.colliderect(pl_e):
                pl_e=None
                cortar_sound.play()
                puntos += 5
        fuente = pygame.font.Font(None, 36)
        texto = fuente.render("Puntos: {}".format(puntos), True, (0, 0, 0))
        tiempo_actual = pygame.time.get_ticks()
        tiempo_restante = duracion / 1000
        if hay_pelotas:
            tiempo_restante = (duracion - (tiempo_actual - tiempo_inicio)) / 1000
        if tiempo_restante <= 0:
            tiempo_restante = 0
            texto_final = fuente.render("Tiempo agotado! Puntos finales: {}".format(puntos), True, (0, 0, 0))
            screen.blit(texto_final, (100, 300))
            pygame.display.flip()
            pygame.time.delay(2000)
            pos_mouse.clear()
            cap.release()
            return "menu"
        minutos = int(tiempo_restante // 60)
        segundos = int(tiempo_restante % 60)
        texto_timer = fuente.render("Tiempo: {}:{:02d}".format(minutos, segundos), True, (0, 0, 0))
        screen.blit(texto_timer, (400, 10))
        screen.blit(texto, (10, 10))
        small_frame = cv2.resize(frame, (200, 150))
        # Convertir a formato adecuado para Pygame
        small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        small_surface = pygame.surfarray.make_surface(np.rot90(small_frame))
        # Dibujar la cámara en la esquina inferior derecha
        screen.blit(small_surface, (600 - 210, 600 - 160))
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
    cv2.destroyAllWindows()
    pygame.quit()
main()