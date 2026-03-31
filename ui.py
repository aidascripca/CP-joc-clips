# ui.py
import pygame
import math

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

def deseneaza_buton(surface, text, font, x, y, w, h, culoare_inactiva, culoare_activa):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    apasat = False
    
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(surface, culoare_activa, (x, y, w, h))
        if click[0] == 1:
            apasat = True
    else:
        pygame.draw.rect(surface, culoare_inactiva, (x, y, w, h))

    pygame.draw.rect(surface, (0, 0, 0), (x, y, w, h), 3)
    deseneaza_text_conturat(surface, text, font, (255, 255, 255), (0, 0, 0), x + w // 2, y + h // 2, center=True)
    return apasat

def deseneaza_buton_rotund(surface, text, font, x_centru, y_centru, raza, culoare_inactiva, culoare_activa):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    apasat = False
    
    distanta = math.hypot(mouse[0] - x_centru, mouse[1] - y_centru)
    
    if distanta <= raza:
        pygame.draw.circle(surface, culoare_activa, (x_centru, y_centru), raza)
        if click[0] == 1:
            apasat = True
    else:
        pygame.draw.circle(surface, culoare_inactiva, (x_centru, y_centru), raza)

    pygame.draw.circle(surface, (0, 0, 0), (x_centru, y_centru), raza, 3) 
    deseneaza_text_conturat(surface, text, font, (255, 255, 255), (0, 0, 0), x_centru, y_centru, center=True)
    return apasat