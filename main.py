import pygame
import random
import sys

# --- SETĂRI INIȚIALE ---
pygame.init()
LATIME, INALTIME = 800, 600
ecran = pygame.display.set_mode((LATIME, INALTIME))
pygame.display.set_caption("Bean Counters - Grafica")
clock = pygame.time.Clock()

# --- ÎNCĂRCARE IMAGINI ---
# Inlocuieste cu numele fisierelor tale
# --- ÎNCĂRCARE ȘI REDIMENSIONARE IMAGINI ---
try:
    # 1. Fundalul (800x600)
    img_bg = pygame.image.load("assets/background.png").convert() # Foloseste slash /
    img_bg = pygame.transform.scale(img_bg, (LATIME, INALTIME))
    
    # 2. Pinguinul (Redimensionat la ceva rezonabil, ex: 100x120)
    img_pinguin = pygame.image.load("assets/Bean_Counters_penguin_1.webp").convert_alpha()
    img_pinguin = pygame.transform.scale(img_pinguin, (100, 120)) 
    
    # 3. Sacul (Redimensionat la ceva mic, ex: 60x40)
    img_sac = pygame.image.load("assets/Java_Bag.webp").convert_alpha()
    img_sac = pygame.transform.scale(img_sac, (60, 40)) 

except FileNotFoundError as e:
    print(f"Eroare: Nu gasesc fisierul! Detalii: {e}")
    sys.exit()

# --- VARIABILE PINGUIN ---
pinguin_x = LATIME // 2
pinguin_y = INALTIME - img_pinguin.get_height() - 20
viteza_pinguin = 8

# --- SISTEMUL DE SACI CARE CAD ---
lista_saci = [] # Aici vom tine minte toti sacii de pe ecran
viteza_sac = 5
timer_generare_sac = 0
interval_generare = 60 # La cate frame-uri apare un sac nou (60 cadre = aprox 1 secunda)

# Variabile temporare de stare (pe care mai tarziu le va gestiona CLIPS)
scor_fals = 0
vieti_false = 3

running = True
while running:
    # 1. EVENIMENTE
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. MIȘCARE PINGUIN
    taste = pygame.key.get_pressed()
    if taste[pygame.K_LEFT] and pinguin_x > 0:
        pinguin_x -= viteza_pinguin
    if taste[pygame.K_RIGHT] and pinguin_x < LATIME - img_pinguin.get_width():
        pinguin_x += viteza_pinguin

    # Creăm HITBOX-ul pinguinului la pozitia lui curenta
    hitbox_pinguin = pygame.Rect(pinguin_x, pinguin_y, img_pinguin.get_width(), img_pinguin.get_height())

    # 3. GENERARE SACI RANDOM
    timer_generare_sac += 1
    if timer_generare_sac >= interval_generare:
        # Generam un X random pentru noul sac
        sac_x = random.randint(0, LATIME - img_sac.get_width())
        sac_y = -50 # Incepe deasupra ecranului
        
        # Adaugam sacul in lista ca un dictionar
        lista_saci.append({"x": sac_x, "y": sac_y})
        
        timer_generare_sac = 0 # Resetam timer-ul
        interval_generare = random.randint(40, 90) # Urmatorul sac apare la un interval usor diferit

    # 4. MIȘCARE ȘI COLIZIUNI SACI
    saci_de_sters = [] # Aici punem sacii care au fost prinsi sau au cazut pe jos
    
    for sac in lista_saci:
        sac["y"] += viteza_sac # Sacul cade
        
        # Creăm HITBOX-ul sacului
        hitbox_sac = pygame.Rect(sac["x"], sac["y"], img_sac.get_width(), img_sac.get_height())
        
        # VERIFICĂM COLIZIUNEA
        if hitbox_pinguin.colliderect(hitbox_sac):
            print("Python raporteaza: BANG! Coliziune cu un sac!")
            # AICI VOM TRIMITE DATELE CATRE CLIPS MAI TARZIU
            scor_fals += 10 # Temporar, ca sa vezi ca merge
            saci_de_sters.append(sac)
            
        # Daca sacul a cazut de pe ecran
        elif sac["y"] > INALTIME:
            saci_de_sters.append(sac)

    # Curatam sacii care nu mai trebuie desenati
    for sac in saci_de_sters:
        if sac in lista_saci:
            lista_saci.remove(sac)

    # 5. DESENARE GRAFICĂ
    ecran.blit(img_bg, (0, 0))
    ecran.blit(img_pinguin, (pinguin_x, pinguin_y))
    
    for sac in lista_saci:
        ecran.blit(img_sac, (sac["x"], sac["y"]))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()