# assets_loader.py
import pygame
import sys
from config import LATIME, INALTIME

def incarca_imagini():
    resurse = {}
    try:
        img_bg = pygame.image.load("assets/background.png").convert()
        resurse['bg'] = pygame.transform.scale(img_bg, (LATIME, INALTIME))

        resurse['pinguini'] = {}
        for i in range(1, 10):
            nume_fisier = f"assets/Bean_Counters_penguin_{i}.webp"
            img = pygame.image.load(nume_fisier).convert_alpha()
            resurse['pinguini'][i] = pygame.transform.scale(img, (120, 140))

        resurse['saci'] = {
            "sac": pygame.transform.scale(pygame.image.load("assets/Java_Bag.png").convert_alpha(), (120, 100)),
            "sac_gold": pygame.transform.scale(pygame.image.load("assets/Java_Bag_Gold.png").convert_alpha(), (120, 100)),
            "sac_diamond": pygame.transform.scale(pygame.image.load("assets/Java_Bag_Diamond.png").convert_alpha(), (120, 100))
        }

        resurse['platforma'] = {
            "sac": pygame.transform.scale(pygame.image.load("assets/Java_Bag.png").convert_alpha(), (140, 110)),
            "sac_gold": pygame.transform.scale(pygame.image.load("assets/Java_Bag_Gold.png").convert_alpha(), (140, 110)),
            "sac_diamond": pygame.transform.scale(pygame.image.load("assets/Java_Bag_Diamond.png").convert_alpha(), (140, 110))
        }

        resurse['sparte'] = {
            "sac": pygame.transform.scale(pygame.image.load("assets/Sac_Spart.png").convert_alpha(), (120, 100)),
            "sac_gold": pygame.transform.scale(pygame.image.load("assets/Sac_Spart_Gold.png").convert_alpha(), (120, 100)),
            "sac_diamond": pygame.transform.scale(pygame.image.load("assets/Sac_Spart_Diamond.png").convert_alpha(), (120, 100))
        }

        resurse['nicovala'] = pygame.transform.scale(pygame.image.load("assets/Bean_Counters_anvil.webp").convert_alpha(), (60, 50))
        resurse['nicovala_jos'] = pygame.transform.scale(pygame.image.load("assets/Nicovala_Jos.png").convert_alpha(), (60, 50))
        resurse['peste'] = pygame.transform.scale(pygame.image.load("assets/Bean_Counters_fish.webp").convert_alpha(), (50, 20))

    except FileNotFoundError as e:
        print(f"Eroare: Nu gasesc fisierele! {e}")
        sys.exit()

    return resurse

def incarca_fonturi():
    nume_font = "comicsansms"
    return {
        "hud": pygame.font.SysFont(nume_font, 35, bold=True),
        "mare": pygame.font.SysFont(nume_font, 50, bold=True),
        "efecte": pygame.font.SysFont(nume_font, 50, bold=True),
        "mic": pygame.font.SysFont(nume_font, 25, bold=True)
    }