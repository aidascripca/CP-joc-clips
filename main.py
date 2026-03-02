import pygame
import random
import sys

# --- SETĂRI INIȚIALE ---
pygame.init()
LATIME, INALTIME = 800, 600
ecran = pygame.display.set_mode((LATIME, INALTIME))
pygame.display.set_caption("Bean Counters - Nivele si Obstacole")
clock = pygame.time.Clock()

# --- ÎNCĂRCARE IMAGINI ---
try:
    # 1. Fundalul
    img_bg = pygame.image.load("assets/background.png").convert()
    img_bg = pygame.transform.scale(img_bg, (LATIME, INALTIME))
    
    # 2. Lista de Pinguini (1-9)
    pinguini_imagini = {}
    for i in range(1, 10): # Acum incarcam de la 1 la 9
        nume_fisier = f"assets/Bean_Counters_penguin_{i}.webp"
        img = pygame.image.load(nume_fisier).convert_alpha()
        pinguini_imagini[i] = pygame.transform.scale(img, (120, 140)) 
    
    # 3. Obiectele care cad
    img_sac = pygame.image.load("assets/Java_Bag.webp").convert_alpha()
    img_sac = pygame.transform.scale(img_sac, (60, 40)) 
    
    img_nicovala = pygame.image.load("assets/Bean_Counters_anvil.webp").convert_alpha()
    img_nicovala = pygame.transform.scale(img_nicovala, (60, 50)) 
    
    img_peste = pygame.image.load("assets/Bean_Counters_fish.webp").convert_alpha()
    img_peste = pygame.transform.scale(img_peste, (50, 20))

except FileNotFoundError as e:
    print(f"Eroare: Nu gasesc fisierele! Verifica numele in folderul assets. Detalii: {e}")
    sys.exit()

# --- VARIABILE JOC ---
pinguin_x = LATIME // 2
pinguin_y = INALTIME - 160 
viteza_pinguin = 8
saci_in_brate = 0
vieti = 3
scor = 0

# --- VARIABILE NIVELE ---
nivel = 1
total_saci_descarcati = 0

# --- VARIABILE COOLDOWN ---
cooldown_timer = 0
COOLDOWN_DURATA = 120 
tip_cooldown = 7 # 7 = saci, 8 = nicovala, 9 = peste

# --- SISTEM OBIECTE ---
lista_obiecte = []
viteza_cadere = 5
timer_generare = 0
interval_generare = 60

font = pygame.font.SysFont("Arial", 30, bold=True)

running = True
game_over = False

while running:
    # 1. EVENIMENTE
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                # Reset complet la Restart
                saci_in_brate = 0
                vieti = 3
                scor = 0
                nivel = 1
                total_saci_descarcati = 0
                lista_obiecte = []
                cooldown_timer = 0
                game_over = False

    if not game_over:
        
        # Scădem timer-ul de cooldown
        if cooldown_timer > 0:
            cooldown_timer -= 1

        # 2. MIȘCARE PINGUIN
        taste = pygame.key.get_pressed()
        if cooldown_timer == 0: 
            if taste[pygame.K_LEFT] and pinguin_x > 0:
                pinguin_x -= viteza_pinguin
            if taste[pygame.K_RIGHT] and pinguin_x < LATIME - pinguini_imagini[1].get_width():
                pinguin_x += viteza_pinguin
        
        # --- LOGICA DESCARCARE (Platforma din stanga) ---
        if pinguin_x < 50 and saci_in_brate > 0 and cooldown_timer == 0:
            scor += saci_in_brate * 10
            total_saci_descarcati += saci_in_brate # Adaugam la total pentru nivel
            saci_in_brate = 0
            
            # Verificam daca trecem la un nivel nou
            if total_saci_descarcati >= 80: nivel = 5
            elif total_saci_descarcati >= 50: nivel = 4
            elif total_saci_descarcati >= 35: nivel = 3
            elif total_saci_descarcati >= 20: nivel = 2

        # --- LOGICA SCHIMBARE IMAGINE PINGUIN ---
        if cooldown_timer > 0:
            # Afisam imaginea corecta in functie de ce l-a lovit
            img_curenta = pinguini_imagini[tip_cooldown] 
        else:
            indice_img = saci_in_brate + 1
            if indice_img > 6: indice_img = 6
            img_curenta = pinguini_imagini[indice_img]

        hitbox_pinguin = img_curenta.get_rect(topleft=(pinguin_x, pinguin_y))

        # --- SETARI DIFICULTATE IN FUNCTIE DE NIVEL ---
        if nivel == 1:
            int_min, int_max, prob_obstacol = 50, 80, 0   # 0% obstacole
        elif nivel == 2:
            int_min, int_max, prob_obstacol = 45, 75, 10  # 10% obstacole
        elif nivel == 3:
            int_min, int_max, prob_obstacol = 40, 65, 20  # 20% obstacole
        elif nivel == 4:
            int_min, int_max, prob_obstacol = 30, 55, 30  # 30% obstacole, pica mai repede
        else: # Nivel 5
            int_min, int_max, prob_obstacol = 20, 45, 40  # 40% obstacole, ploaie de obiecte

        # 3. GENERARE OBIECTE
        timer_generare += 1
        if timer_generare >= interval_generare:
            obiect_x = random.randint(100, LATIME - 150)
            
            # Alegem tipul obiectului bazat pe probabilitatea nivelului
            tip_ales = "sac"
            if random.randint(1, 100) <= prob_obstacol:
                tip_ales = random.choice(["nicovala", "peste"])
                
            lista_obiecte.append({"x": obiect_x, "y": -50, "tip": tip_ales})
            timer_generare = 0
            interval_generare = random.randint(int_min, int_max)

        # 4. MISCARE SI COLIZIUNI
        obiecte_de_sters = []
        for obj in lista_obiecte:
            obj["y"] += viteza_cadere
            
            # Hitbox in functie de tip
            if obj["tip"] == "sac": h_obj = pygame.Rect(obj["x"], obj["y"], 60, 40)
            elif obj["tip"] == "nicovala": h_obj = pygame.Rect(obj["x"], obj["y"], 60, 50)
            elif obj["tip"] == "peste": h_obj = pygame.Rect(obj["x"], obj["y"], 50, 20)

            # Coliziunea
            if cooldown_timer == 0 and hitbox_pinguin.colliderect(h_obj):
                obiecte_de_sters.append(obj)
                
                if obj["tip"] == "sac":
                    saci_in_brate += 1
                    if saci_in_brate >= 7:
                        vieti -= 1; saci_in_brate = 0
                        cooldown_timer = COOLDOWN_DURATA; tip_cooldown = 7
                        if vieti <= 0: game_over = True
                        
                elif obj["tip"] == "nicovala":
                    vieti -= 1; saci_in_brate = 0
                    cooldown_timer = COOLDOWN_DURATA; tip_cooldown = 8 # Imaginea 8
                    if vieti <= 0: game_over = True
                    
                elif obj["tip"] == "peste":
                    vieti -= 1; saci_in_brate = 0
                    cooldown_timer = COOLDOWN_DURATA; tip_cooldown = 9 # Imaginea 9
                    if vieti <= 0: game_over = True
            
            elif obj["y"] > INALTIME:
                obiecte_de_sters.append(obj)

        for obj in obiecte_de_sters:
            if obj in lista_obiecte:
                lista_obiecte.remove(obj)

    # 5. DESENARE
    ecran.blit(img_bg, (0, 0))
    
    if not game_over:
        ecran.blit(img_curenta, (pinguin_x, pinguin_y))
        
        # Desenam obiectele in functie de tipul lor
        for obj in lista_obiecte:
            if obj["tip"] == "sac": ecran.blit(img_sac, (obj["x"], obj["y"]))
            elif obj["tip"] == "nicovala": ecran.blit(img_nicovala, (obj["x"], obj["y"]))
            elif obj["tip"] == "peste": ecran.blit(img_peste, (obj["x"], obj["y"]))
        
        # Interfata Grafica (HUD)
        text_scor = font.render(f"Scor: {scor}", True, (255, 255, 255))
        text_vieti = font.render(f"Vieti: {vieti}", True, (255, 50, 50))
        text_nivel = font.render(f"Nivel: {nivel}", True, (50, 255, 50))
        text_saci = font.render(f"Saci: {saci_in_brate}/6", True, (255, 255, 0))
        
        ecran.blit(text_scor, (20, 20))
        ecran.blit(text_vieti, (20, 60))
        ecran.blit(text_nivel, (20, 100))
        ecran.blit(text_saci, (LATIME - 150, 20))
    else:
        text_msg = font.render("GAME OVER! Apasa R pentru Restart", True, (200, 0, 0))
        ecran.blit(text_msg, (LATIME//2 - 200, INALTIME//2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()