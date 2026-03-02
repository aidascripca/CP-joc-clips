import pygame
import random
import sys

# --- SETĂRI INIȚIALE ---
pygame.init()
LATIME, INALTIME = 800, 600
ecran = pygame.display.set_mode((LATIME, INALTIME))
pygame.display.set_caption("Bean Counters - Efecte Sol si Fade")
clock = pygame.time.Clock()

# --- FUNCȚIE PENTRU TEXT CU CONTUR ---
def deseneaza_text_conturat(surface, text, font, culoare_text, culoare_contur, x, y, center=False):
    text_surface = font.render(text, True, culoare_text)
    contur_surface = font.render(text, True, culoare_contur)
    
    if center:
        rect = text_surface.get_rect(center=(x, y))
        x, y = rect.topleft

    grosime = 2
    for dx in [-grosime, 0, grosime]:
        for dy in [-grosime, 0, grosime]:
            if dx != 0 or dy != 0:
                surface.blit(contur_surface, (x + dx, y + dy))
                
    surface.blit(text_surface, (x, y))

# --- FONTURI CARTOONISH ---
nume_font = "comicsansms"
font_hud = pygame.font.SysFont(nume_font, 35, bold=True)
font_mare = pygame.font.SysFont(nume_font, 80, bold=True)
font_efecte = pygame.font.SysFont(nume_font, 50, bold=True)    

# --- ÎNCĂRCARE IMAGINI ---
try:
    img_bg = pygame.image.load("assets/background.png").convert()
    img_bg = pygame.transform.scale(img_bg, (LATIME, INALTIME))
    
    pinguini_imagini = {}
    for i in range(1, 10): 
        nume_fisier = f"assets/Bean_Counters_penguin_{i}.webp"
        img = pygame.image.load(nume_fisier).convert_alpha()
        pinguini_imagini[i] = pygame.transform.scale(img, (120, 140)) 
    
    img_sac = pygame.image.load("assets/Java_Bag.png").convert_alpha()
    img_sac = pygame.transform.scale(img_sac, (120, 100)) 
    
    img_sac_platforma = pygame.image.load("assets/Java_Bag.png").convert_alpha()
    img_sac_platforma = pygame.transform.scale(img_sac_platforma, (140, 110)) 
    
    img_nicovala = pygame.image.load("assets/Bean_Counters_anvil.webp").convert_alpha()
    img_nicovala = pygame.transform.scale(img_nicovala, (60, 50)) 
    
    img_peste = pygame.image.load("assets/Bean_Counters_fish.webp").convert_alpha()
    img_peste = pygame.transform.scale(img_peste, (50, 20))

    # --- IMAGINI NOI PENTRU EFECTE PE SOL ---
    img_sac_spart = pygame.image.load("assets/Sac_Spart.png").convert_alpha()
    img_sac_spart = pygame.transform.scale(img_sac_spart, (120, 100)) # Aceeasi dimensiune ca sacul
    
    img_nicovala_jos = pygame.image.load("assets/Nicovala_Jos.png").convert_alpha()
    img_nicovala_jos = pygame.transform.scale(img_nicovala_jos, (60, 50))

except FileNotFoundError as e:
    print(f"Eroare: Nu gasesc fisierele! Verifica numele in folderul assets. Detalii: {e}")
    sys.exit()



# --- VARIABILE JOC ---
pinguin_x = LATIME // 2
pinguin_y = INALTIME - 160 
viteza_pinguin = 10
saci_in_brate = 0
vieti = 3
scor = 0
saci_pe_platforma = 0

nivel = 1
total_saci_descarcati = 0
timer_tranzitie_nivel = 120 

cooldown_timer = 0
COOLDOWN_DURATA = 120 
tip_cooldown = 7 

lista_obiecte = []
lista_efecte_sol = [] # Lista pentru obiectele cazute pe jos
interval_generare = 60
timer_generare = 0

# Nivelul Y la care consideram ca obiectul s-a izbit de pamant
NIVEL_SOL = INALTIME - 80 

running = True
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                saci_in_brate = 0
                saci_pe_platforma = 0 
                vieti = 3
                scor = 0
                nivel = 1
                total_saci_descarcati = 0
                lista_obiecte = []
                lista_efecte_sol = []
                cooldown_timer = 0
                timer_tranzitie_nivel = 120 
                game_over = False
                img_curenta = pinguini_imagini[1] 

    if not game_over:
        if timer_tranzitie_nivel > 0:
            timer_tranzitie_nivel -= 1
            img_curenta = pinguini_imagini[1]
        else:
            if cooldown_timer > 0:
                cooldown_timer -= 1

            taste = pygame.key.get_pressed()
            if cooldown_timer == 0: 
                if taste[pygame.K_LEFT] and pinguin_x > 0:
                    pinguin_x -= viteza_pinguin
                if taste[pygame.K_RIGHT] and pinguin_x < LATIME - pinguini_imagini[1].get_width():
                    pinguin_x += viteza_pinguin
            
            # --- LOGICA DESCARCARE ---
            if pinguin_x < 50 and saci_in_brate > 0 and cooldown_timer == 0:
                saci_pe_platforma += saci_in_brate 
                scor += saci_in_brate * 10 #scor per sac
                total_saci_descarcati += saci_in_brate 
                saci_in_brate = 0
                
                nivel_anterior = nivel
                
                if total_saci_descarcati >= 150: nivel = 6 
                elif total_saci_descarcati >= 100: nivel = 5
                elif total_saci_descarcati >= 70: nivel = 4
                elif total_saci_descarcati >= 50: nivel = 3
                elif total_saci_descarcati >= 20: nivel = 2

                if nivel > nivel_anterior:
                    timer_tranzitie_nivel = 120 
                    lista_obiecte.clear()       
                    pinguin_x = LATIME // 2     
                    saci_pe_platforma = 0 

            if cooldown_timer > 0:
                img_curenta = pinguini_imagini[tip_cooldown] 
            else:
                indice_img = saci_in_brate + 1
                if indice_img > 6: indice_img = 6
                img_curenta = pinguini_imagini[indice_img]

            # --- HITBOX PINGUIN ---
            offset_x = 30  
            offset_y = 10  
            latime_hitbox = 60   
            inaltime_hitbox = 50 
            hitbox_pinguin = pygame.Rect(pinguin_x + offset_x, pinguin_y + offset_y, latime_hitbox, inaltime_hitbox)

            if nivel == 1: int_min, int_max, prob_obstacol = 50, 80, 0
            elif nivel == 2: int_min, int_max, prob_obstacol = 45, 75, 10
            elif nivel == 3: int_min, int_max, prob_obstacol = 40, 65, 20
            elif nivel == 4: int_min, int_max, prob_obstacol = 30, 55, 30
            else: int_min, int_max, prob_obstacol = 20, 45, 40 

            # 3. GENERARE OBIECTE
            timer_generare += 1
            if timer_generare >= interval_generare:
                start_x = LATIME - 250 
                start_y = 150 
                v_x = random.uniform(-7.0, -3.0) 
                v_y = random.uniform(-9.0, -4.0) 

                tip_ales = "sac"
                if random.randint(1, 100) <= prob_obstacol:
                    tip_ales = random.choice(["nicovala", "peste"])
                
                lista_obiecte.append({"x": start_x, "y": start_y, "tip": tip_ales, "vx": v_x, "vy": v_y, "unghi": 0})
                timer_generare = 0
                interval_generare = random.randint(int_min, int_max)

            # 4. MISCARE SI COLIZIUNI
            obiecte_de_sters = []
            gravitatie = 0.4 

            for obj in lista_obiecte:
                obj["vy"] += gravitatie  
                obj["x"] += obj["vx"]    
                obj["y"] += obj["vy"]    
                
                if -3 <= obj["vy"] <= 3:
                    obj["unghi"] += 5

                if obj["tip"] == "sac": h_obj = pygame.Rect(obj["x"], obj["y"], 60, 40)
                elif obj["tip"] == "nicovala": h_obj = pygame.Rect(obj["x"], obj["y"], 60, 50)
                elif obj["tip"] == "peste": h_obj = pygame.Rect(obj["x"], obj["y"], 50, 20)

                if cooldown_timer == 0 and hitbox_pinguin.colliderect(h_obj):
                    obiecte_de_sters.append(obj)
                    if obj["tip"] == "sac":
                        saci_in_brate += 1
                        if saci_in_brate >= 6:
                            vieti -= 1; saci_in_brate = 0
                            cooldown_timer = COOLDOWN_DURATA; tip_cooldown = 7
                            img_curenta = pinguini_imagini[tip_cooldown] 
                            if vieti <= 0: game_over = True
                            
                    elif obj["tip"] == "nicovala":
                        vieti -= 1; saci_in_brate = 0
                        cooldown_timer = COOLDOWN_DURATA; tip_cooldown = 8 
                        img_curenta = pinguini_imagini[tip_cooldown] 
                        if vieti <= 0: game_over = True
                        
                    elif obj["tip"] == "peste":
                        vieti -= 1; saci_in_brate = 0
                        cooldown_timer = COOLDOWN_DURATA; tip_cooldown = 9 
                        img_curenta = pinguini_imagini[tip_cooldown] 
                        if vieti <= 0: game_over = True
                
                # --- MODIFICARE AICI: OBIECTUL CADE PE PAMANT ---
                elif obj["y"] > NIVEL_SOL:
                    obiecte_de_sters.append(obj)
                    
                    # Alegem imaginea corespunzatoare pentru sol
                    if obj["tip"] == "sac": img_efect = img_sac_spart
                    elif obj["tip"] == "nicovala": img_efect = img_nicovala_jos
                    elif obj["tip"] == "peste": img_efect = img_peste # Pestele ramane la fel
                    
                    # Adaugam in lista de efecte vizuale cu timer si alpha (transparenta)
                    lista_efecte_sol.append({
                        "x": obj["x"],
                        "y": NIVEL_SOL, # Il oprim din cadere fix la nivelul pamantului
                        "img": img_efect,
                        "timer": 90, # Ramane 1.5 secunde (90 cadre)
                        "alpha": 255 # Opacitate maxima initial
                    })

            for obj in obiecte_de_sters:
                if obj in lista_obiecte:
                    lista_obiecte.remove(obj)

    # --- LOGICA FADE-OUT PENTRU EFECTE SOL ---
    # Aceasta parte ruleaza constant, chiar si la Game Over, ca sa se termine animatia
    efecte_de_sters = []
    for efect in lista_efecte_sol:
        efect["timer"] -= 1
        
        # Incepem sa estompam imaginea in ultimele 30 de cadre (0.5 secunde)
        if efect["timer"] < 30:
            efect["alpha"] -= (255 / 30)
            if efect["alpha"] < 0: efect["alpha"] = 0
            
        if efect["timer"] <= 0:
            efecte_de_sters.append(efect)
            
    for efect in efecte_de_sters:
        if efect in lista_efecte_sol:
            lista_efecte_sol.remove(efect)

    # -----------------------------------------------------------------------
    # 5. DESENARE 
    # -----------------------------------------------------------------------
    ecran.blit(img_bg, (0, 0))
    
    baza_platforma_x = 10 
    baza_platforma_y = INALTIME - 120 
    for i in range(saci_pe_platforma):
        pozitie_y = baza_platforma_y - (i * 15)
        ecran.blit(img_sac_platforma, (baza_platforma_x, pozitie_y))

    # --- DESENARE EFECTE SOL (Sub pinguin, dar peste fundal) ---
    for efect in lista_efecte_sol:
        img_temp = efect["img"].copy() # Copiem imaginea ca sa ii putem modifica transparenta
        img_temp.set_alpha(int(efect["alpha"])) # Aplicam Fade-ul
        ecran.blit(img_temp, (efect["x"], efect["y"]))

    if 'img_curenta' in locals():
        ecran.blit(img_curenta, (pinguin_x, pinguin_y))
        
    for obj in lista_obiecte:
        if obj["tip"] == "sac": img_baza = img_sac
        elif obj["tip"] == "nicovala": img_baza = img_nicovala
        elif obj["tip"] == "peste": img_baza = img_peste
        
        img_rotita = pygame.transform.rotate(img_baza, obj["unghi"])
        rect_baza = img_baza.get_rect(topleft=(obj["x"], obj["y"]))
        rect_rotit = img_rotita.get_rect(center=rect_baza.center)
        ecran.blit(img_rotita, rect_rotit.topleft)
    
    # --- HUD ---
    deseneaza_text_conturat(ecran, f"LIVES: {vieti}", font_hud, (255, 255, 255), (0, 0, 0), 30, 20)
    deseneaza_text_conturat(ecran, f"LEVEL: {nivel}", font_hud, (255, 255, 255), (0, 0, 0), LATIME // 2, 20, center=True)
    deseneaza_text_conturat(ecran, f"SCORE: {scor}", font_hud, (255, 255, 255), (0, 0, 0), LATIME - 250, 20)
    deseneaza_text_conturat(ecran, f"Saci: {saci_in_brate}/5", font_hud, (255, 255, 0), (0, 0, 0), LATIME - 250, 60)

    # --- ECRANE SUPRAPUSE ---
    if game_over:
        if tip_cooldown == 8: deseneaza_text_conturat(ecran, "ZBANG!!", font_efecte, (255, 50, 50), (0, 0, 0), pinguin_x + 60, pinguin_y - 40, center=True)
        elif tip_cooldown == 9: deseneaza_text_conturat(ecran, "PLEOSC!!", font_efecte, (100, 255, 255), (0, 0, 0), pinguin_x + 60, pinguin_y - 40, center=True)
        elif tip_cooldown == 7: deseneaza_text_conturat(ecran, "BUF!!", font_efecte, (255, 200, 50), (0, 0, 0), pinguin_x + 60, pinguin_y - 40, center=True)

        fundal_gameover = pygame.Surface((LATIME, INALTIME))
        fundal_gameover.set_alpha(150) 
        fundal_gameover.fill((0, 0, 0))
        ecran.blit(fundal_gameover, (0, 0))
        
        deseneaza_text_conturat(ecran, "GAME OVER!", font_mare, (255, 50, 50), (0, 0, 0), LATIME//2, INALTIME//2 - 30, center=True)
        deseneaza_text_conturat(ecran, "Apasa R pentru Restart", font_hud, (255, 255, 255), (0, 0, 0), LATIME//2, INALTIME//2 + 50, center=True)

    else:
        if cooldown_timer > 0:
            if tip_cooldown == 8: deseneaza_text_conturat(ecran, "ZBANG!!", font_efecte, (255, 50, 50), (0, 0, 0), pinguin_x + 60, pinguin_y - 40, center=True)
            elif tip_cooldown == 9: deseneaza_text_conturat(ecran, "PLEOSC!!", font_efecte, (100, 255, 255), (0, 0, 0), pinguin_x + 60, pinguin_y - 40, center=True)
            elif tip_cooldown == 7: deseneaza_text_conturat(ecran, "BUF!!", font_efecte, (255, 200, 50), (0, 0, 0), pinguin_x + 60, pinguin_y - 40, center=True)
            
            if cooldown_timer > 90: text_cd = "Mai incearca!"
            elif cooldown_timer > 60: text_cd = "3"
            elif cooldown_timer > 30: text_cd = "2"
            else: text_cd = "1"
            deseneaza_text_conturat(ecran, text_cd, font_mare, (255, 255, 255), (0, 0, 0), LATIME//2, INALTIME//2 - 50, center=True)

        if timer_tranzitie_nivel > 0:
            fundal_text = pygame.Surface((LATIME, 120))
            fundal_text.set_alpha(150) 
            fundal_text.fill((0, 0, 0)) 
            ecran.blit(fundal_text, (0, INALTIME//2 - 60))
            deseneaza_text_conturat(ecran, f"NIVELUL {nivel}", font_mare, (255, 215, 0), (0, 0, 0), LATIME//2, INALTIME//2, center=True)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()