import pygame
import random
import sys

# --- SETĂRI INIȚIALE ---
pygame.init()
LATIME, INALTIME = 800, 600
ecran = pygame.display.set_mode((LATIME, INALTIME))
pygame.display.set_caption("Bean Counters - Manual Player Edition")
clock = pygame.time.Clock()


# ==========================================
# FUNCȚII GRAFICE INTERNE (Înlocuiesc modulul UI)
# ==========================================
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


def deseneaza_buton(surface, text, font, x, y, latime, inaltime, culoare_baza, culoare_hover):
    mouse_pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, latime, inaltime)

    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(surface, culoare_hover, rect)
        pygame.draw.rect(surface, (255, 255, 255), rect, 2)  # Contur alb la hover
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(surface, culoare_baza, rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 2)  # Contur negru normal

    deseneaza_text_conturat(surface, text, font, (255, 255, 255), (0, 0, 0), x + latime // 2, y + inaltime // 2,
                            center=True)
    return False


def deseneaza_buton_rotund(surface, text, font, cx, cy, raza, culoare_baza, culoare_hover):
    mouse_pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    dist = ((mouse_pos[0] - cx) ** 2 + (mouse_pos[1] - cy) ** 2) ** 0.5

    if dist <= raza:
        pygame.draw.circle(surface, culoare_hover, (cx, cy), raza)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), raza, 2)
        if click[0] == 1:
            return True
    else:
        pygame.draw.circle(surface, culoare_baza, (cx, cy), raza)
        pygame.draw.circle(surface, (0, 0, 0), (cx, cy), raza, 2)

    deseneaza_text_conturat(surface, text, font, (255, 255, 255), (0, 0, 0), cx, cy, center=True)
    return False


# --- ÎNCĂRCARE IMAGINI ---
try:
    img_bg = pygame.image.load("assets/background.png").convert()
    img_bg = pygame.transform.scale(img_bg, (LATIME, INALTIME))

    pinguini_imagini = {}
    for i in range(1, 10):
        nume_fisier = f"assets/Bean_Counters_penguin_{i}.webp"
        img = pygame.image.load(nume_fisier).convert_alpha()
        pinguini_imagini[i] = pygame.transform.scale(img, (120, 140))

    imagini_saci = {
        "sac": pygame.transform.scale(pygame.image.load("assets/Java_Bag.png").convert_alpha(), (120, 100)),
        "sac_gold": pygame.transform.scale(pygame.image.load("assets/Java_Bag_Gold.png").convert_alpha(), (120, 100)),
        "sac_diamond": pygame.transform.scale(pygame.image.load("assets/Java_Bag_Diamond.png").convert_alpha(),
                                              (120, 100))
    }

    imagini_platforma = {
        "sac": pygame.transform.scale(pygame.image.load("assets/Java_Bag.png").convert_alpha(), (140, 110)),
        "sac_gold": pygame.transform.scale(pygame.image.load("assets/Java_Bag_Gold.png").convert_alpha(), (140, 110)),
        "sac_diamond": pygame.transform.scale(pygame.image.load("assets/Java_Bag_Diamond.png").convert_alpha(),
                                              (140, 110))
    }

    imagini_sparte = {
        "sac": pygame.transform.scale(pygame.image.load("assets/Sac_Spart.png").convert_alpha(), (120, 100)),
        "sac_gold": pygame.transform.scale(pygame.image.load("assets/Sac_Spart_Gold.png").convert_alpha(), (120, 100)),
        "sac_diamond": pygame.transform.scale(pygame.image.load("assets/Sac_Spart_Diamond.png").convert_alpha(),
                                              (120, 100))
    }

    img_nicovala = pygame.transform.scale(pygame.image.load("assets/Bean_Counters_anvil.webp").convert_alpha(),
                                          (60, 50))
    img_nicovala_jos = pygame.transform.scale(pygame.image.load("assets/Nicovala_Jos.png").convert_alpha(), (60, 50))
    img_peste = pygame.transform.scale(pygame.image.load("assets/Bean_Counters_fish.webp").convert_alpha(), (50, 20))

except FileNotFoundError as e:
    print(f"Eroare critically: Nu gasesc folderul assets sau imaginile! {e}")
    sys.exit()

nume_font = "comicsansms"
font_hud = pygame.font.SysFont(nume_font, 35, bold=True)
font_mare = pygame.font.SysFont(nume_font, 50, bold=True)
font_efecte = pygame.font.SysFont(nume_font, 50, bold=True)
font_mic = pygame.font.SysFont(nume_font, 22, bold=True)

# --- VARIABILE STATICE CONFIG ---
VITEZA_DE_BAZA = 10
MAX_SACI_SCAPATI = 20
NIVEL_SOL = INALTIME - 80
COOLDOWN_DURATA = 120

# --- VARIABILE DE STARE INITIALE ---
stare_curenta = "MENIU_PRINCIPAL"
mod_infinit = False
nivel = 1
interval_generare = 60
timer_generare = 0


def resetare_joc(nivel_start=1, infinit=False):
    global pinguin_x, pinguin_y, viteza_curenta_pinguin, vieti, scor
    global lista_saci_brate, lista_saci_platforma, saci_scapati, motiv_game_over
    global stamina, stamina_epuizata, nivel, total_saci_descarcati
    global timer_tranzitie_nivel, cooldown_timer, tip_cooldown
    global lista_obiecte, lista_efecte_sol, timer_generare, mod_infinit, stare_curenta

    pinguin_x = LATIME // 2
    pinguin_y = INALTIME - 160
    viteza_curenta_pinguin = VITEZA_DE_BAZA
    vieti = 3
    scor = 0
    lista_saci_brate = []
    lista_saci_platforma = []
    saci_scapati = 0
    motiv_game_over = ""
    stamina = 100.0
    stamina_epuizata = False
    nivel = nivel_start
    total_saci_descarcati = 0
    timer_tranzitie_nivel = 120
    cooldown_timer = 0
    tip_cooldown = 7
    lista_obiecte = []
    lista_efecte_sol = []
    timer_generare = 0
    mod_infinit = infinit
    stare_curenta = "JOC"


running = True
click_debounce = 0

while running:
    ecran.blit(img_bg, (0, 0))
    if click_debounce > 0:
        click_debounce -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                if stare_curenta == "JOC":
                    stare_curenta = "PAUZA"
                elif stare_curenta == "PAUZA":
                    stare_curenta = "JOC"
            if event.key == pygame.K_r and stare_curenta == "GAME_OVER":
                resetare_joc(nivel_start=nivel, infinit=mod_infinit)

    # ==========================================
    # STATE: MENIU PRINCIPAL
    # ==========================================
    if stare_curenta == "MENIU_PRINCIPAL":
        fundal_intunecat = pygame.Surface((LATIME, INALTIME))
        fundal_intunecat.set_alpha(150)
        fundal_intunecat.fill((0, 0, 0))
        ecran.blit(fundal_intunecat, (0, 0))

        deseneaza_text_conturat(ecran, "BEAN COUNTERS", font_mare, (255, 215, 0), (0, 0, 0), LATIME // 2,
                                INALTIME // 2 - 100, center=True)
        deseneaza_text_conturat(ecran, "Manual Player Edition", font_hud, (255, 255, 255), (0, 0, 0), LATIME // 2,
                                INALTIME // 2 - 50, center=True)

        if deseneaza_buton(ecran, "Start Joc Normal", font_mic, LATIME // 2 - 125, INALTIME // 2 + 20, 250, 50,
                           (50, 150, 50), (100, 200, 100)) and click_debounce == 0:
            resetare_joc(nivel_start=1, infinit=False)
            click_debounce = 15

        if deseneaza_buton(ecran, "Selecteaza Nivel", font_mic, LATIME // 2 - 125, INALTIME // 2 + 90, 250, 50,
                           (50, 50, 150), (100, 100, 200)) and click_debounce == 0:
            stare_curenta = "SELECTIE_NIVEL"
            click_debounce = 15

    # ==========================================
    # STATE: SELECTIE NIVEL (Poti alege Nivelul 5 direct!)
    # ==========================================
    elif stare_curenta == "SELECTIE_NIVEL":
        fundal_intunecat = pygame.Surface((LATIME, INALTIME))
        fundal_intunecat.set_alpha(150)
        fundal_intunecat.fill((0, 0, 0))
        ecran.blit(fundal_intunecat, (0, 0))

        deseneaza_text_conturat(ecran, "Alege Nivelul de Start", font_mare, (255, 215, 0), (0, 0, 0), LATIME // 2, 80,
                                center=True)

        for i in range(1, 6):
            if deseneaza_buton(ecran, f"Nivelul {i}", font_mic, LATIME // 2 - 100, 140 + i * 60, 200, 40,
                               (150, 100, 50), (200, 150, 100)) and click_debounce == 0:
                resetare_joc(nivel_start=i, infinit=True)
                click_debounce = 15

        if deseneaza_buton(ecran, "Inapoi", font_mic, 20, 20, 120, 40, (150, 50, 50),
                           (200, 100, 100)) and click_debounce == 0:
            stare_curenta = "MENIU_PRINCIPAL"
            click_debounce = 15

    # ==========================================
    # STATES: JOC, PAUZA SAU GAME OVER
    # ==========================================
    elif stare_curenta in ["JOC", "PAUZA", "GAME_OVER"]:

        # Logica fizica se actualizeaza DOAR in starea activa de joc
        if stare_curenta == "JOC":
            if timer_tranzitie_nivel > 0:
                timer_tranzitie_nivel -= 1
                img_curenta = pinguini_imagini[1]
            else:
                if cooldown_timer > 0:
                    cooldown_timer -= 1

                # 1. LOGICA STAMINA & VITEZA
                numar_saci = len(lista_saci_brate)
                greutate_extra = sum(
                    0.3 if s == "sac_gold" else (0.5 if s == "sac_diamond" else 0) for s in lista_saci_brate)

                if numar_saci == 0:
                    modificator_stamina = 0.3
                elif numar_saci == 1:
                    modificator_stamina = 0.1
                elif numar_saci == 2:
                    modificator_stamina = 0.05
                elif numar_saci == 3:
                    modificator_stamina = -0.4
                elif numar_saci == 4:
                    modificator_stamina = -0.6
                else:
                    modificator_stamina = -0.8

                if modificator_stamina < 0:
                    modificator_stamina -= greutate_extra

                stamina += modificator_stamina
                if stamina > 100:
                    stamina = 100
                elif stamina <= 0:
                    stamina = 0
                    stamina_epuizata = True

                if stamina_epuizata and stamina >= 20: stamina_epuizata = False

                if stamina_epuizata:
                    viteza_curenta_pinguin = 2
                else:
                    penalizare_greutate = sum(
                        1 if s == "sac_gold" else (2.5 if s == "sac_diamond" else 0) for s in lista_saci_brate)
                    viteza_curenta_pinguin = VITEZA_DE_BAZA - penalizare_greutate
                    if viteza_curenta_pinguin < 3: viteza_curenta_pinguin = 3

                # 2. CONTROLUL MANUAL AL JUCĂTORULUI
                taste = pygame.key.get_pressed()
                if cooldown_timer == 0:
                    if taste[pygame.K_LEFT] and pinguin_x > 0:
                        pinguin_x -= viteza_curenta_pinguin
                    if taste[pygame.K_RIGHT] and pinguin_x < LATIME - pinguini_imagini[1].get_width():
                        pinguin_x += viteza_curenta_pinguin

                # 3. LOGICA DESCARCARE LA PLATFORMA
                if pinguin_x < 50 and len(lista_saci_brate) > 0 and cooldown_timer == 0:
                    for sac in lista_saci_brate:
                        if sac == "sac":
                            scor += 10
                        elif sac == "sac_gold":
                            scor += 30
                        elif sac == "sac_diamond":
                            scor += 50
                        lista_saci_platforma.append(sac)

                    total_saci_descarcati += len(lista_saci_brate)
                    lista_saci_brate.clear()

                    if not mod_infinit:
                        nivel_anterior = nivel
                        if total_saci_descarcati >= 150:
                            nivel = 6
                        elif total_saci_descarcati >= 100:
                            nivel = 5
                        elif total_saci_descarcati >= 70:
                            nivel = 4
                        elif total_saci_descarcati >= 50:
                            nivel = 3
                        elif total_saci_descarcati >= 20:
                            nivel = 2

                        if nivel > nivel_anterior:
                            timer_tranzitie_nivel = 120
                            lista_obiecte.clear()
                            pinguin_x = LATIME // 2
                            lista_saci_platforma.clear()

                if cooldown_timer > 0:
                    img_curenta = pinguini_imagini[tip_cooldown]
                else:
                    indice_img = len(lista_saci_brate) + 1
                    if indice_img > 6: indice_img = 6
                    img_curenta = pinguini_imagini[indice_img]

                offset_x, offset_y, latime_hitbox, inaltime_hitbox = 30, 10, 60, 50
                hitbox_pinguin = pygame.Rect(pinguin_x + offset_x, pinguin_y + offset_y, latime_hitbox, inaltime_hitbox)

                if nivel == 1:
                    int_min, int_max, prob_obstacol = 50, 80, 0
                elif nivel == 2:
                    int_min, int_max, prob_obstacol = 45, 75, 15
                elif nivel == 3:
                    int_min, int_max, prob_obstacol = 40, 65, 25
                elif nivel == 4:
                    int_min, int_max, prob_obstacol = 30, 55, 35
                else:
                    int_min, int_max, prob_obstacol = 20, 45, 45

                # 4. GENERARE OBIECTE PROCEDURALE
                timer_generare += 1
                if timer_generare >= interval_generare:
                    start_x, start_y = LATIME - 250, 150
                    v_x = random.uniform(-7.0, -3.0)
                    v_y = random.uniform(-9.0, -4.0)

                    if random.randint(1, 100) <= prob_obstacol:
                        tip_ales = random.choice(["nicovala", "peste"])
                        gravitatie_obiect = 0.4
                    else:
                        sans = random.randint(1, 100)
                        if sans <= 70:
                            tip_ales, gravitatie_obiect = "sac", 0.4
                        elif sans <= 90:
                            tip_ales, gravitatie_obiect = "sac_gold", 0.45
                        else:
                            tip_ales, gravitatie_obiect = "sac_diamond", 0.55

                    lista_obiecte.append({"x": start_x, "y": start_y, "tip": tip_ales, "vx": v_x, "vy": v_y, "unghi": 0,
                                          "grav": gravitatie_obiect})
                    timer_generare = 0
                    interval_generare = random.randint(int_min, int_max)

                # 5. MISCARE SI COLIZIUNI
                obiecte_de_sters = []
                for obj in lista_obiecte:
                    obj["vy"] += obj["grav"]
                    obj["x"] += obj["vx"]
                    obj["y"] += obj["vy"]

                    if -3 <= obj["vy"] <= 3: obj["unghi"] += 5

                    if "sac" in obj["tip"]:
                        h_obj = pygame.Rect(obj["x"], obj["y"], 60, 40)
                    elif obj["tip"] == "nicovala":
                        h_obj = pygame.Rect(obj["x"], obj["y"], 60, 50)
                    elif obj["tip"] == "peste":
                        h_obj = pygame.Rect(obj["x"], obj["y"], 50, 20)

                    if cooldown_timer == 0 and hitbox_pinguin.colliderect(h_obj):
                        obiecte_de_sters.append(obj)
                        if "sac" in obj["tip"]:
                            lista_saci_brate.append(obj["tip"])
                            if len(lista_saci_brate) >= 6:
                                vieti -= 1;
                                lista_saci_brate.clear();
                                cooldown_timer = COOLDOWN_DURATA;
                                tip_cooldown = 7
                                if vieti <= 0: stare_curenta, motiv_game_over = "GAME_OVER", "strivit"
                        elif obj["tip"] == "nicovala":
                            vieti -= 1;
                            lista_saci_brate.clear();
                            cooldown_timer = COOLDOWN_DURATA;
                            tip_cooldown = 8
                            if vieti <= 0: stare_curenta, motiv_game_over = "GAME_OVER", "strivit"
                        elif obj["tip"] == "peste":
                            vieti -= 1;
                            lista_saci_brate.clear();
                            cooldown_timer = COOLDOWN_DURATA;
                            tip_cooldown = 9
                            if vieti <= 0: stare_curenta, motiv_game_over = "GAME_OVER", "strivit"

                    elif obj["y"] > NIVEL_SOL:
                        obiecte_de_sters.append(obj)
                        if "sac" in obj["tip"]:
                            img_efect = imagini_sparte[obj["tip"]]
                            saci_scapati += 1
                            if saci_scapati >= MAX_SACI_SCAPATI: stare_curenta, motiv_game_over = "GAME_OVER", "concediat"
                        elif obj["tip"] == "nicovala":
                            img_efect = img_nicovala_jos
                        elif obj["tip"] == "peste":
                            img_efect = img_peste

                        lista_efecte_sol.append(
                            {"x": obj["x"], "y": NIVEL_SOL, "img": img_efect, "timer": 90, "alpha": 255})

                for obj in obiecte_de_sters:
                    if obj in lista_obiecte: lista_obiecte.remove(obj)

                efecte_de_sters = []
                for efect in lista_efecte_sol:
                    efect["timer"] -= 1
                    if efect["timer"] < 30:
                        efect["alpha"] -= (255 / 30)
                        if efect["alpha"] < 0: efect["alpha"] = 0
                    if efect["timer"] <= 0: efecte_de_sters.append(efect)
                for efect in efecte_de_sters:
                    if efect in lista_efecte_sol: lista_efecte_sol.remove(efect)

        # ==========================================
        # RANDARE FUNDAL ȘI ENTITĂȚI (Comune pentru Joc, Pauză și GameOver)
        # ==========================================
        baza_platforma_x, baza_platforma_y = 10, INALTIME - 120
        for i, tip_sac in enumerate(lista_saci_platforma):
            pozitie_y = baza_platforma_y - (i * 15)
            ecran.blit(imagini_platforma[tip_sac], (baza_platforma_x, pozitie_y))

        for efect in lista_efecte_sol:
            img_temp = efect["img"].copy()
            img_temp.set_alpha(int(efect["alpha"]))
            ecran.blit(img_temp, (efect["x"], efect["y"]))

        if 'img_curenta' in locals():
            ecran.blit(img_curenta, (pinguin_x, pinguin_y))

        for obj in lista_obiecte:
            if "sac" in obj["tip"]:
                img_baza = imagini_saci[obj["tip"]]
            elif obj["tip"] == "nicovala":
                img_baza = img_nicovala
            elif obj["tip"] == "peste":
                img_baza = img_peste
            img_rotita = pygame.transform.rotate(img_baza, obj["unghi"])
            rect_baza = img_baza.get_rect(topleft=(obj["x"], obj["y"]))
            rect_rotit = img_rotita.get_rect(center=rect_baza.center)
            ecran.blit(img_rotita, rect_rotit.topleft)

        # RENDER HUD TELEMETRIE
        deseneaza_text_conturat(ecran, f"LIVES: {vieti}", font_hud, (255, 255, 255), (0, 0, 0), 30, 20)
        deseneaza_text_conturat(ecran, f"LEVEL: {nivel}", font_hud, (255, 255, 255), (0, 0, 0), LATIME // 2, 20,
                                center=True)
        deseneaza_text_conturat(ecran, f"SCORE: {scor}", font_hud, (255, 255, 255), (0, 0, 0), 30, 100)
        deseneaza_text_conturat(ecran, f"Saci: {len(lista_saci_brate)}/5", font_hud, (255, 255, 0), (0, 0, 0),
                                LATIME - 220, 20)
        deseneaza_text_conturat(ecran, f"Scapati: {saci_scapati}/{MAX_SACI_SCAPATI}", font_hud, (255, 100, 100),
                                (0, 0, 0), LATIME - 250, 60)

        # BUTON PAUZĂ OPTIC (Micuț, Rotund în colț)
        if deseneaza_buton_rotund(ecran, "P", font_mic, LATIME - 20, 20, 20, (100, 100, 100),
                                  (150, 150, 150)) and click_debounce == 0:
            if stare_curenta == "JOC":
                stare_curenta = "PAUZA"
            elif stare_curenta == "PAUZA":
                stare_curenta = "JOC"
            click_debounce = 15

        # RANDARE BARA DE STAMINĂ
        x_bara, y_bara, latime_bara, inaltime_bara = 30, 70, 200, 20
        if stamina_epuizata:
            culoare_stamina = (100, 100, 100)
        elif stamina > 50:
            culoare_stamina = (50, 255, 50)
        elif stamina > 20:
            culoare_stamina = (255, 255, 50)
        else:
            culoare_stamina = (255, 50, 50)

        pygame.draw.rect(ecran, (0, 0, 0), (x_bara - 2, y_bara - 2, latime_bara + 4, inaltime_bara + 4))
        pygame.draw.rect(ecran, (50, 50, 50), (x_bara, y_bara, latime_bara, inaltime_bara))
        latime_curenta = (stamina / 100.0) * latime_bara
        if latime_curenta > 0: pygame.draw.rect(ecran, culoare_stamina, (x_bara, y_bara, latime_curenta, inaltime_bara))
        deseneaza_text_conturat(ecran, "ENERGY", pygame.font.SysFont("comicsansms", 18, bold=True), (255, 255, 255),
                                (0, 0, 0), x_bara + 60, y_bara - 3)

        # ANIMATIE COOLDOWN IMPACT
        if stare_curenta == "JOC" and cooldown_timer > 0:
            if tip_cooldown == 8:
                deseneaza_text_conturat(ecran, "ZBANG!!", font_efecte, (255, 50, 50), (0, 0, 0), pinguin_x + 60,
                                        pinguin_y - 40, center=True)
            elif tip_cooldown == 9:
                deseneaza_text_conturat(ecran, "PLEOSC!!", font_efecte, (100, 255, 255), (0, 0, 0), pinguin_x + 60,
                                        pinguin_y - 40, center=True)
            elif tip_cooldown == 7:
                deseneaza_text_conturat(ecran, "STUF!!", font_efecte, (255, 200, 50), (0, 0, 0), pinguin_x + 60,
                                        pinguin_y - 40, center=True)

            if cooldown_timer > 90:
                text_cd = "Mai incearca!"
            elif cooldown_timer > 60:
                text_cd = "3"
            elif cooldown_timer > 30:
                text_cd = "2"
            else:
                text_cd = "1"
            deseneaza_text_conturat(ecran, text_cd, font_mare, (255, 255, 255), (0, 0, 0), LATIME // 2,
                                    INALTIME // 2 - 50, center=True)

        # CARD TRANZIȚIE NIVEL
        if stare_curenta == "JOC" and timer_tranzitie_nivel > 0:
            fundal_text = pygame.Surface((LATIME, 120))
            fundal_text.set_alpha(150)
            fundal_text.fill((0, 0, 0))
            ecran.blit(fundal_text, (0, INALTIME // 2 - 60))
            deseneaza_text_conturat(ecran, f"NIVELUL {nivel}", font_mare, (255, 215, 0), (0, 0, 0), LATIME // 2,
                                    INALTIME // 2, center=True)

        # ==========================================
        # OVERLAY: PAUZĂ
        # ==========================================
        if stare_curenta == "PAUZA":
            fundal_pauza = pygame.Surface((LATIME, INALTIME))
            fundal_pauza.set_alpha(170)
            fundal_pauza.fill((0, 0, 0))
            ecran.blit(fundal_pauza, (0, 0))

            deseneaza_text_conturat(ecran, "PAUZA", font_mare, (255, 255, 255), (0, 0, 0), LATIME // 2,
                                    INALTIME // 2 - 60, center=True)
            deseneaza_text_conturat(ecran, "Apasa P sau ESC pentru a continua", font_hud, (200, 200, 200), (0, 0, 0),
                                    LATIME // 2, INALTIME // 2, center=True)

            if deseneaza_buton(ecran, "Meniu Principal", font_mic, LATIME // 2 - 100, INALTIME // 2 + 70, 200, 40,
                               (150, 50, 50), (200, 100, 100)) and click_debounce == 0:
                stare_curenta = "MENIU_PRINCIPAL"
                click_debounce = 15

        # ==========================================
        # OVERLAY: GAME OVER
        # ==========================================
        elif stare_curenta == "GAME_OVER":
            fundal_gameover = pygame.Surface((LATIME, INALTIME))
            fundal_gameover.set_alpha(180)
            fundal_gameover.fill((0, 0, 0))
            ecran.blit(fundal_gameover, (0, 0))

            if motiv_game_over == "concediat":
                deseneaza_text_conturat(ecran, "AI FOST CONCEDIAT!", font_mare, (255, 50, 50), (0, 0, 0), LATIME // 2,
                                        INALTIME // 2 - 60, center=True)
                deseneaza_text_conturat(ecran, "Ai lasat sa cada prea multa marfa...", font_hud, (255, 200, 50),
                                        (0, 0, 0), LATIME // 2, INALTIME // 2 + 10, center=True)
            else:
                deseneaza_text_conturat(ecran, "GAME OVER!", font_mare, (255, 50, 50), (0, 0, 0), LATIME // 2,
                                        INALTIME // 2 - 50, center=True)
                deseneaza_text_conturat(ecran, "Pinguinul a fost strivit de obstacole!", font_hud, (255, 200, 50),
                                        (0, 0, 0), LATIME // 2, INALTIME // 2 + 10, center=True)

            deseneaza_text_conturat(ecran, "Apasa R pentru Restart", font_hud, (255, 255, 255), (0, 0, 0), LATIME // 2,
                                    INALTIME // 2 + 70, center=True)

            if deseneaza_buton(ecran, "Meniu Principal", font_mic, LATIME // 2 - 100, INALTIME // 2 + 130, 200, 40,
                               (150, 50, 50), (200, 100, 100)) and click_debounce == 0:
                stare_curenta = "MENIU_PRINCIPAL"
                click_debounce = 15

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
