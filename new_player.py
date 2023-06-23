import pygame
from pygame.math import Vector2 as vec
from fireball import FireBall

from player_animations import (
    player_run_anim_R,
    player_run_anim_L,
    player_idle_anim_R,
    player_idle_anim_L,
    player_jump_anim_R,
    player_jump_anim_L,
    player_attack_anim_R,
    player_attack_anim_L,
    player_heal
)

# Les variables pour bouger
# On ajoute de la friction pour que les mouvements soient plus agréables
ACC = 0.8
FRIC = -0.2

# Les variables de l'écran
HEIGHT = 720
WIDTH = 1280
# Commentaire test


class NewPlayer(pygame.sprite.Sprite):
    def __init__(self, game, x, y, walls):
        super().__init__()
        # Images
        self.image = pygame.image.load("img/player/test.png")
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.game = game
        # Physique et collision et mouvement
        self.vx = 0
        self.walls = walls
        self.position = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.direction = "RIGHT"
        self.jumping = False
        self.running = False
        self.attacking = False
        self.healing = False
        self.magic_attacking = False
        self.player_mana = self.game.manabar.mana # On accède à l'attribut mana de manabar via game
        self.fireballs = pygame.sprite.Group()

        # Animation
        self.attack_frame = 0
        self.frame_index = 0
        self.attack_counter = 0
        self.time_since_last_frame = 0
        self.frame_duration = 60
        # Je rajoute ceci pour pénaliser le joueur qui décide de se heal en combat
        self.healing_frame_duration = 120
        self.heal_frame_index = 0 # Pour séparer le frame index des autres animations de celle du heal, sinon c'est partagé
        self.fire_rate = 5000
        self.last_fire = pygame.time.get_ticks()
        self.state = 'idle'
        
    def move(self):
        # Constante qui va accélérer vers le bas ce qui va simuler la gravité
        self.acc = vec(0, 0.5)

        # Running = faux si on est trop slow
        if abs(self.vel.x) > 0.1:
            self.running = True
        else:
            self.running = False

        if not self.healing:
            # Cela va renvoyer les touches pressées
            pressed_keys = pygame.key.get_pressed()

            # Accélère dans une direction ou une autre suivant la touche utilisée
            if (
                pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_q]
            ):  # Q pour aller à gauche
                self.acc.x = -ACC
                self.direction = "LEFT"
            elif (
                pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]
            ):  # D pour aller à droite
                self.acc.x = ACC
                self.direction = "RIGHT"

            # Détermine la vélocité en prenant en compte la friciton
            self.acc.x += self.vel.x * FRIC
            self.vel += self.acc

            if abs(self.vel.x) < 0.01:
                self.vel.x = 0

            move_by = int(self.vel.x)
            for _ in range(abs(move_by)):
                # Increment or decrement x position by 1 pixel
                if move_by > 0:
                    self.position.x += 1
                else:
                    self.position.x -= 1
                # Update le rectangle
                self.rect.x = self.position.x
                # Check pour les collisions
                collisions = pygame.sprite.spritecollide(self, self.walls, False)
                if collisions:
                    # Si je bouge vers la droite ajuste ma position à 1 pixel à gauche du mur
                    if move_by > 0:
                        self.position.x = collisions[0].rect.left - self.rect.width - 3
                    # Si je bouge vers la gauche ajuste ma position à 1 pixel à droite du mur
                    elif move_by < 0:
                        self.position.x = collisions[0].rect.right + 3
                    # Stop any horizontal movement
                    self.vel.x = 0
                    break
            # Vertical movement
            self.position.y += self.vel.y
            self.rect.y = self.position.y
            self.gravity_check()

            # Outil de debug
            #print(f"Acceleration: {self.acc}, Velocity: {self.vel}, Position: {self.position}")

            self.rect.topleft = self.position

    # Fonction qui faire un check de la gravité pour voir si on peut sauter ou pas
    # Et gère les collisions verticales
    def gravity_check(self):
        collisions = pygame.sprite.spritecollide(self, self.walls, False)
        if collisions:
            # Détecet si le joueur bouge vers le bas
            if self.vel.y > 0:
                # Personnage bouge vers le bas
                for wall in collisions:
                    # Place le joueur sur le mur
                    self.position.y = wall.rect.top - self.rect.height
                    # Stoppe la chute verticale
                    self.vel.y = 0
                    self.jumping = False
            # Détecte si le personnage saute
            elif self.vel.y < 0:
                # Saut
                for wall in collisions:
                    # Place le joueur sous le mur
                    self.position.y = wall.rect.bottom
                    # Stop mouvement vers le haut
                    self.vel.y = 0

    # Permet de sauter
    def jump(self):
        # Check si le joueur est sur le sol et ne saute pas
        self.rect.y += 1
        collisions = pygame.sprite.spritecollide(self, self.walls, False)
        self.rect.y -= 1

        # Si on est sur le sol et qu'on ne saute pas, on saute
        if collisions and not self.jumping:
            self.jumping = True
            self.vel.y = -8
            self.frame_index = 0

    # Update la liste des murs sinon on entre en collision avec les murs du premier niveau
    def update_walls(self, new_wall_group):
        self.walls = new_wall_group

    def update(self):
        time_passed = (
            pygame.time.get_ticks() - self.time_since_last_frame
        )  # Pour que les animations soient plus smooth, elles vont charger moins vite

        if (
            self.frame_index > 7
        ):  # Comme nous avons 8 images pour les animations, ceci nous permet de revenir à l'image 0
            self.frame_index = 0
            return

        if self.healing:
            if time_passed > self.healing_frame_duration:
                self.time_since_last_frame = pygame.time.get_ticks()
                if self.player_mana > 1 and not self.jumping:
                    self.state = 'healing'
                    if self.direction == "RIGHT":
                        self.image = player_heal[self.heal_frame_index]
                    elif self.direction == "LEFT":
                        self.image = pygame.transform.flip(player_heal[self.heal_frame_index], True, False)
                    self.heal_frame_index += 1
                    if self.heal_frame_index >= len(player_heal):
                        self.healing = False
                        self.heal_frame_index = 0
                        self.state ='idle'

                else: # Si le joueur n'a pas au moins 1 de mana, pas de heal et d'animation de heal
                    self.healing = False
                    self.heal_frame_index = 0
                    self.state = 'idle'
                return
        elif time_passed > self.frame_duration:
            self.time_since_last_frame = pygame.time.get_ticks()
            if self.jumping:
                if self.direction == "RIGHT":
                    self.image = player_jump_anim_R[self.frame_index]
                elif self.direction == "LEFT":
                    self.image = player_jump_anim_L[self.frame_index]
                self.frame_index += 1

            if self.running and not self.jumping:
                if self.vel.x > 0:
                    self.image = player_run_anim_R[self.frame_index]
                    self.direction = "RIGHT"
                elif self.vel.x < 0:
                    self.image = player_run_anim_L[self.frame_index]
                    self.direction = "LEFT"
                self.frame_index += 1

            elif not self.running and not self.healing and self.vel == vec(0, 0):
                if self.direction == "RIGHT":
                    self.image = player_idle_anim_R[self.frame_index]
                elif self.direction == "LEFT":
                    self.image = player_idle_anim_L[self.frame_index]
                self.frame_index += 1

    def attack(self):
        # En fonction du nombre de fois qu'on attaque, il y aura plusieurs animations
        attack_to_end_frame = {1: 6, 2: 9, 3: 13, 4: 19}
        end_frame = attack_to_end_frame.get(self.attack_counter, 19)
        time_passed = (
            pygame.time.get_ticks() - self.time_since_last_frame
        )  # Pour que les animations soient plus smooth, elles vont charger moins vite
        if time_passed > self.frame_duration:
            self.time_since_last_frame = pygame.time.get_ticks()
            if self.attack_frame > end_frame:
                self.attack_frame = 0
                self.attacking = False

            if self.direction == "RIGHT":
                self.image = player_attack_anim_R[self.attack_frame]
            elif self.direction == "LEFT":
                self.image = player_attack_anim_L[self.attack_frame]
            self.mask = pygame.mask.from_surface(self.image)
            self.attack_frame += 1

    # Méthode qui va appeler la fonction Heal de healthbar pour redonner 1 hp pour 1 mana
    def heal(self):
        self.game.healthbar.Heal(1, 1)
        self.state = 'healing'
        
    def fireball(self, manacost, damage):
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_rate:
            if self.game.manabar.manaCost(manacost)and self.state != 'healing':
                self.state = 'casting'
                self.player_mana -= manacost
                fireball = FireBall(self.game, self.position.x, self.position.y - 30, self.direction, damage)
                fireball.damage = damage
                self.game.fireballs.add(fireball)
                self.magic_attacking = True
                self.state = 'idle'
            else:
                print("Not enough mana")
                self.state = 'idle'