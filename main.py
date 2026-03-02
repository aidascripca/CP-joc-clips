import pygame
import random
import sys

# --- SETĂRI INIȚIALE ---
pygame.init()
LATIME, INALTIME = 800, 600
ecran = pygame.display.set_mode((LATIME, INALTIME))
pygame.display.set_caption("Bean Counters - Evolutie Pinguin")
clock = pygame.time.Clock()

# --- ÎNCĂRCARE IMAGINI ---
try:
    # 1. Fundalul
    img_bg = pygame.image.load("assets/background.png").convert()
    img_bg = pygame.transform.scale(img_bg, (LATIME, INALTIME))
    
    # 2. Lista de Pinguini (Evolutie)
    pinguini_imagini = {}
    for i in range(1, 8): 
        nume_fisier = f"assets/Bean_Counters_penguin_{i}.webp"
        img = pygame.image.load(nume_fisier).convert_alpha()
        pinguini_imagini[i] = pygame.transform.scale(img, (120, 140)) 
    
    # 3. Sacul
    img_sac = pygame.image.load("assets/Java_Bag.webp").convert_alpha()
    img_sac = pygame.transform.scale(img_sac, (60, 40)) 

except FileNotFoundError as e:
    print(f"Eroare: Nu gasesc fisierele! Verifica numele in folderul assets. Detalii: {e}")
    sys.exit()

# --- VARIABILE JOC ---
pinguin_x = LATIME // 2
pinguin_y = INALTIME - 160 # Pozitie deasupra zapezii
viteza_pinguin = 8
saci_in_brate = 0
vieti = 3
scor = 0
cooldown_timer = 0
COOLDOWN_DURATA = 120 # 120 cadre = aprox 2 secunde la 60 FPS

# --- SISTEM SACI ---
lista_saci = []
viteza_sac = 5
timer_generare_sac = 0
interval_generare = 60

# Font pentru scor si mesaje
font = pygame.font.SysFont("Arial", 30, bold=True)

running = True
game_over = False

while running:
    # 1. EVENIMENTE
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            # Restart joc daca apesi R dupa moarte
            if event.key == pygame.K_r:
                saci_in_brate = 0
                vieti = 3
                scor = 0
                lista_saci = []
                game_over = False
                cooldown_timer = 0

    if not game_over:
        
        # Scădem timer-ul de cooldown
        if cooldown_timer > 0:
            cooldown_timer -= 1

        # 2. MIȘCARE PINGUIN
        taste = pygame.key.get_pressed()
        if cooldown_timer == 0: # Pinguinul se mișcă doar dacă nu e amețit
            if taste[pygame.K_LEFT] and pinguin_x > 0:
                pinguin_x -= viteza_pinguin
            if taste[pygame.K_RIGHT] and pinguin_x < LATIME - pinguini_imagini[1].get_width():
                pinguin_x += viteza_pinguin
        
        # --- LOGICA DESCARCARE (Platforma din stanga) ---
        if pinguin_x < 50 and saci_in_brate > 0 and cooldown_timer == 0:
            scor += saci_in_brate * 10
            saci_in_brate = 0
            print(f"Sacii au fost descarcati! Scor: {scor}")

        # --- LOGICA SCHIMBARE IMAGINE PINGUIN ---
        if cooldown_timer > 0:
            img_curenta = pinguini_imagini[7] # Imaginea de "lovit/amețit"
        else:
            # Logica normală de progresie a sacilor
            indice_img = saci_in_brate + 1
            if indice_img > 6: 
                indice_img = 6
            img_curenta = pinguini_imagini[indice_img]

        # Actualizare Hitbox Pinguin
        hitbox_pinguin = img_curenta.get_rect(topleft=(pinguin_x, pinguin_y))

        # 3. GENERARE SACI
        timer_generare_sac += 1
        if timer_generare_sac >= interval_generare:
            sac_x = random.randint(100, LATIME - 150)
            lista_saci.append({"x": sac_x, "y": -50})
            timer_generare_sac = 0
            interval_generare = random.randint(40, 80)

        # 4. MISCARE SI COLIZIUNI SACI
        saci_de_sters = []
        for sac in lista_saci:
            sac["y"] += viteza_sac
            hitbox_sac = pygame.Rect(sac["x"], sac["y"], 60, 40)

            # Verificăm coliziunea DOAR dacă nu suntem în cooldown
            if cooldown_timer == 0 and hitbox_pinguin.colliderect(hitbox_sac):
                saci_in_brate += 1
                saci_de_sters.append(sac)
                
                # LOGICA DE "MOARTE" / PIERDERE VIAȚĂ
                if saci_in_brate >= 6:
                    vieti -= 1
                    saci_in_brate = 0
                    cooldown_timer = COOLDOWN_DURATA 
                    print(f"Viață pierdută! Vieti ramase: {vieti}")
                    if vieti <= 0:
                        game_over = True
            
            # Stergem sacii care ies de pe ecran
            elif sac["y"] > INALTIME:
                saci_de_sters.append(sac)

        # Curatarea corecta a listei de saci
        for sac in saci_de_sters:
            if sac in lista_saci:
                lista_saci.remove(sac)

    # 5. DESENARE
    ecran.blit(img_bg, (0, 0))
    
    if not game_over:
        ecran.blit(img_curenta, (pinguin_x, pinguin_y))
        for sac in lista_saci:
            ecran.blit(img_sac, (sac["x"], sac["y"]))
        
        # Afisare Scor si Vieti
        text_scor = font.render(f"Scor: {scor}", True, (255, 255, 255))
        text_vieti = font.render(f"Vieti: {vieti}", True, (255, 50, 50))
        text_saci = font.render(f"Saci: {saci_in_brate}/6", True, (255, 255, 0))
        ecran.blit(text_scor, (20, 20))
        ecran.blit(text_vieti, (20, 60))
        ecran.blit(text_saci, (LATIME - 150, 20))
    else:
        # Mesaj Game Over
        text_msg = font.render("GAME OVER! Apasa R pentru Restart", True, (200, 0, 0))
        ecran.blit(text_msg, (LATIME//2 - 200, INALTIME//2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()