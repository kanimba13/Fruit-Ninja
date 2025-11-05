import pygame
import random
import cv2
import mediapipe as mp
import numpy as np
import json
import os

pygame.init()
pygame.mixer.init()
gravedad =2000.0
rozamiento = 0.5
pl = []
pl_e = None  # Bola especial
pl_b = []  # Bomba
dificultad=0
puntajes = []
def cargar_datos():
    if os.path.exists("datos.json"):
        with open("datos.json", "r") as archivo:
            return json.load(archivo)
    else:
        datos = {
            "Nombre": [],
            "Puntaje": [],
        }
        with open("datos.json", "w") as archivo:
            json.dump(datos, archivo, indent=4)
        return datos
def menu():
    ancho,alto=800,600
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
            if 85 <= mouse_x <= 695 and 65 <= mouse_y <= 205:
                pygame.time.delay(200)
                return "menu_dificultad"
            if 495 <= mouse_x <= 695 and 230 <= mouse_y <= 380:
                pygame.time.delay(200)
                return "menu_puntajes"
            if 85 <= mouse_x <= 695 and 405 <= mouse_y <= 550:
                return "salir"
        pygame.display.flip()
        clock.tick(60)
def menu_puntajes():
    ancho,alto=800,600
    pantalla=pygame.display.set_mode((ancho,alto))
    pygame.display.set_caption("Cortar Frutas")
    fondo = pygame.image.load("Multimedia/Imagenes/Menu_P.png").convert()
    exit=pygame.image.load("Multimedia/Imagenes/exitRight.png").convert_alpha()
    fondo = pygame.transform.scale(fondo, (ancho, alto))
    pantalla.blit(fondo, (0, 0))
    pantalla.blit(exit, (750, 10))
    running=True
    clock = pygame.time.Clock()
    datos = cargar_datos()
    fuente = pygame.font.Font(None, 36)
    for i, (nombre, puntaje) in enumerate(zip(datos["Nombre"], datos["Puntaje"])):
        texto = fuente.render("{}. {} - {}".format(i+1, nombre, puntaje), True, (0, 0, 0))
        pantalla.blit(texto, (200, 100 + i * 40))
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
        if pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if 750 <= mouse_x <= 790 and 20 <= mouse_y <= 50:
                pygame.time.delay(200)
                return "menu"
        pygame.display.flip()
        clock.tick(60)
def menu_dificultad():
    global dificultad
    ancho,alto=800,600
    pantalla=pygame.display.set_mode((ancho,alto))
    pygame.display.set_caption("Cortar Frutas")
    fondo = pygame.image.load("Multimedia/Imagenes/Menu_D.png").convert()
    exit=pygame.image.load("Multimedia/Imagenes/exitRight.png").convert_alpha()
    fondo = pygame.transform.scale(fondo, (ancho, alto))
    pantalla.blit(fondo, (0, 0))
    pantalla.blit(exit, (750, 10))
    running=True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
        if pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if 85 <= mouse_x <= 690 and 65 <= mouse_y <= 205:
                pygame.time.delay(200)
                dificultad=0
                return "juego"
            if 85 <= mouse_x <= 690 and 235 <= mouse_y <= 375:
                pygame.time.delay(200)
                dificultad=1
                return "juego"
            if 85 <= mouse_x <= 690 and 405 <= mouse_y <= 550:
                pygame.time.delay(200)
                dificultad=2
                return "juego"
            if 750 <= mouse_x <= 790 and 10 <= mouse_y <= 50:
                pygame.time.delay(200)
                return "menu"
        pygame.display.flip()
        clock.tick(60)
def crear_bola(x, y, vx, vy, r=14):
    color = (random.randint(1,255), random.randint(1,255), random.randint(1,255))
    pl.append({
        "x": float(x), "y": float(y),   # posición en float para precisión
        "vx": float(vx), "vy": float(vy),  # velocidad
        "r": r, "color": color
    })
def crear_bola_especial(x, y, vx, vy, r=30):
    global pl_e
    color = (255, 0, 0)  # Color rojo para la bola especial
    pl_e = {
        "x": float(x), "y": float(y),   # posición en float para precisión
        "vx": float(vx), "vy": float(vy),  # velocidad
        "r": r, "color": color
    }
def crear_bomba(x, y, vx, vy, r=20):
    global pl_b
    color = (0, 0, 0)  # Color negro
    pl_b.append({
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
def actualizar_bolas_especial(dt):
    """Integra la física de la bola especial en dt segundos."""
    # Rozamiento aplicado como decaimiento exponencial por segundo
    drag = rozamiento ** dt
    E = pl_e
    # 1) fuerzas -> aceleraciones: solo gravedad en Y
    E["vy"] += gravedad * dt        # [m/s] = [m/s^2]*[s]            v = v_0 +a*t

    # 2) rozamiento (reduce gradualmente la velocidad)
    E["vx"] *= drag
    E["vy"] *= drag

    # 3) integración de posición
    E["x"]  += E["vx"] * dt        #[m] = [m/s]*[s]            x = x_0 + vt
    E["y"]  += E["vy"] * dt

    r = E["r"]
def actualizar_bombas(dt):
    """Integra la física de todas las bombas en dt segundos."""
    drag = rozamiento ** dt
    for B in pl_b:
        # gravedad
        B["vy"] += gravedad * dt

        # rozamiento
        B["vx"] *= drag
        B["vy"] *= drag

        # posición
        B["x"] += B["vx"] * dt
        B["y"] += B["vy"] * dt

        r = B["r"]
def guardar_puntaje(pantalla, puntaje):
    fuente = pygame.font.Font(None, 36)
    nombre = ""
    clock = pygame.time.Clock()
    ingresar = True

    # Dimensiones del modal
    modal_width, modal_height = 400, 150
    modal_x = (pantalla.get_width() - modal_width) // 2
    modal_y = (pantalla.get_height() - modal_height) // 2
    modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)

    while ingresar:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ingresar = False
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and nombre != "":
                    ingresar = False
                    break
                elif event.key == pygame.K_BACKSPACE:
                    nombre = nombre[:-1]
                else:
                    if len(nombre) < 5 and event.unicode.isprintable():
                        nombre += event.unicode

        # --- Dibujar el modal ---
        pantalla.fill((255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)  # Opcional: oscurece fondo
        pygame.draw.rect(pantalla, (200, 200, 200), modal_rect)  # fondo del modal
        pygame.draw.rect(pantalla, (0, 0, 0), modal_rect, 2)  # borde

        # Texto guía
        texto_guia = fuente.render("Ingresa tu nombre (máx 5):", True, (0, 0, 0))
        pantalla.blit(texto_guia, (modal_x + 20, modal_y + 20))

        # Texto ingresado
        texto_nombre = fuente.render(nombre, True, (0, 0, 0))
        pantalla.blit(texto_nombre, (modal_x + 20, modal_y + 70))

        pygame.display.flip()
        clock.tick(30)

    # --- Guardar en JSON ---
    if not os.path.exists("datos.json"):
        datos = {"Nombre": [], "Puntaje": []}
    else:
        with open("datos.json", "r") as f:
            datos = json.load(f)
    datos["Nombre"].append(nombre)
    datos["Puntaje"].append(puntaje)
    # Ordenar los puntajes de mayor a menor
    combined = list(zip(datos["Nombre"], datos["Puntaje"]))
    combined.sort(key=lambda x: x[1], reverse=True)
    datos["Nombre"], datos["Puntaje"] = zip(*combined)
    datos["Nombre"] = list(datos["Nombre"])
    datos["Puntaje"] = list(datos["Puntaje"])
    if len(datos["Nombre"]) > 10:
        datos["Nombre"] = datos["Nombre"][:10]
        datos["Puntaje"] = datos["Puntaje"][:10]
    with open("datos.json", "w") as f:
        json.dump(datos, f, indent=4)
def juego():
    global pl_e
    global pl
    global dificultad
    global gravedad
    if dificultad==0:
        gravedad=2000.0
    elif dificultad==1:
        gravedad=4500.0
    else:
        gravedad=6500.0
    hay_pelotas= False
    screen=pygame.display.set_mode((800, 600))
    clock=pygame.time.Clock()
    running=True
    pared=pygame.image.load("Multimedia/Imagenes/Wood.jpg").convert()
    pared=pygame.transform.scale(pared, (800, 600))
    cortar_sound=pygame.mixer.Sound("Multimedia/Audio/KnifeSlice.ogg")
    exit=pygame.image.load("Multimedia/Imagenes/exitRight.png").convert_alpha()
    corazon=pygame.image.load("Multimedia/Imagenes/Corazon.png").convert_alpha()
    corazon = pygame.transform.smoothscale(corazon, (50, 50))
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
    timer_bomba = 0
    puntos=0
    duracion=60000
    vidas=3
    is_pinching = False
    while running:
        dt = clock.tick(120) / 1000.0
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                cap.release()
                running=False
            if event.type==pygame.MOUSEMOTION:
                #pos_mouse.append(event.pos)
                pass
            if event.type==pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if 750 <= mouse_x <= 790 and 10 <= mouse_y <= 50:
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
                if distance < 0.1:  # Ajusta el valor
                    is_pinching = True
                    pos_mouse.append((int(index_tip.x * 800), int(index_tip.y * 600)))
                else:
                    is_pinching = False
                mp_draw.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=3),
                    mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2)
                )
        actualizar_bolas(dt)
        if pl_e:
            actualizar_bolas_especial(dt)
        if pl_b:
            actualizar_bombas(dt)
        screen.blit(pared, (0, 0))
        screen.blit(exit, (750, 10))
        for v in range(vidas):
            screen.blit(corazon, (200 + v * 40, 5))
        cambio_timer += clock.get_time()
        timer_especial += clock.get_time()
        timer_bomba += clock.get_time()
        if dificultad==0:
            limite=2000
        elif dificultad==1:
            limite=1500
        else:
            limite=1000
        if dificultad==0:
            cantidad_pelotas=10
        elif dificultad==1:
            cantidad_pelotas=15
        else:
            cantidad_pelotas=20
        if cambio_timer > limite:
            pl.clear()
            for i in range(cantidad_pelotas):
                x = random.randint(30, 770)
                y = 610
                vx = 0
                if dificultad==0:
                    vy = random.uniform(-1500, -1800)
                elif dificultad==1:
                    vy = random.uniform(-1800, -2600)
                else:
                    vy = random.uniform(-2000, -3000)
                crear_bola(x, y, vx, vy)
            cambio_timer = 0
            if not hay_pelotas:
                tiempo_inicio=pygame.time.get_ticks()
                hay_pelotas = True
        if timer_especial >= limite*3 and not pl_e:
            if dificultad==0:
                vy = random.uniform(-1500, -1800)
            elif dificultad==1:
                vy = random.uniform(-1800, -2600)
            else:
                vy = random.uniform(-2000, -3000)
            crear_bola_especial(random.randint(30, 770), 610, 0, vy)
            timer_especial = 0
        if timer_bomba > limite*2:
            pl_b.clear()
            for i in range(cantidad_bombas:=dificultad+2):
                x = random.randint(30, 770)
                y = 610
                vx = 0
                if dificultad==0:
                    vy = random.uniform(-1500, -1800)
                elif dificultad==1:
                    vy = random.uniform(-1800, -2600)
                else:
                    vy = random.uniform(-2000, -3000)
                crear_bomba(x, y, vx, vy)
            timer_bomba = 0
        for p in pl:
            pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), p["r"])
        if pl_e:
            pygame.draw.circle(screen, pl_e["color"], (int(pl_e["x"]), int(pl_e["y"])), pl_e["r"])
        for pb in pl_b:
            pygame.draw.circle(screen, pb["color"], (int(pb["x"]), int(pb["y"])), pb["r"])
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
            rect_b_e = pygame.Rect(pl_e["x"]-pl_e["r"], pl_e["y"]-pl_e["r"], pl_e["r"]*2, pl_e["r"]*2) if pl_e else None
            if pl_e and linea.colliderect(rect_b_e):
                pl_e=None
                cortar_sound.play()
                puntos += 5
            for bb in pl_b[:]:
                rect_bb = pygame.Rect(bb["x"]-bb["r"], bb["y"]-bb["r"], bb["r"]*2, bb["r"]*2)
                if linea.colliderect(rect_bb):
                    pl_b.remove(bb)
                    cortar_sound.play()
                    vidas -= 1
                    if vidas <= 0:
                        texto_final = pygame.font.Font(None, 72).render("Juego Terminado! Puntos finales: {}".format(puntos), True, (255, 0, 0))
                        screen.blit(texto_final, (100, 300))
                        pygame.display.flip()
                        pl.clear()
                        pos_mouse.clear()
                        cap.release()
                        guardar_puntaje(screen, puntos)
                        return "menu"
                    break
        fuente = pygame.font.Font(None, 36)
        puntos_texto = fuente.render("Puntos: {}".format(puntos), True, (0, 0, 0))
        tiempo_actual = pygame.time.get_ticks()
        tiempo_restante = duracion / 1000
        if hay_pelotas:
            tiempo_restante = (duracion - (tiempo_actual - tiempo_inicio)) / 1000
        if tiempo_restante <= 0:
            tiempo_restante = 0
            texto_final = fuente.render("Tiempo agotado! Puntos finales: {}".format(puntos), True, (0, 0, 0))
            screen.blit(texto_final, (150, 300))
            pygame.display.flip()
            pl.clear()
            pos_mouse.clear()
            cap.release()
            guardar_puntaje(screen, puntos)
            return "menu"
        minutos = int(tiempo_restante // 60)
        segundos = int(tiempo_restante % 60)
        texto_timer = fuente.render("Tiempo: {}:{:02d}".format(minutos, segundos), True, (0, 0, 0))
        screen.blit(texto_timer, (600, 10))
        screen.blit(puntos_texto, (10, 10))
        small_frame = cv2.resize(frame, (200, 150))
        # Convertir a formato adecuado para Pygame
        small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        small_surface = pygame.surfarray.make_surface(np.rot90(small_frame))
        # Dibujar la cámara en la esquina inferior derecha
        screen.blit(small_surface, (800 - 210, 600 - 160))
        pygame.display.flip()
        clock.tick(120)
    return
def main():
    pantalla_actual = "menu"
    while True:
        if pantalla_actual == "menu":
            pantalla_actual = menu()
        elif pantalla_actual == "menu_dificultad":
            pantalla_actual = menu_dificultad()
        elif pantalla_actual == "menu_puntajes":
            pantalla_actual = menu_puntajes()
        elif pantalla_actual == "juego":
            pantalla_actual = juego()
        elif pantalla_actual == "salir":
            break
    cv2.destroyAllWindows()
    pygame.quit()
main()