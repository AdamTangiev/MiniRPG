import pygame
import pytmx
import pyscroll

from pygame import mixer

from new_player import NewPlayer
from enemy import Enemy, Skeleton1
from wall import Wall
from npc import NPC, Maire
from npc import NPC, Tavernier
from npc import NPC, Forgeron
from npc import NPC, Explorer

from Inventory import Inventory
from HealthBar import HealthBar

pygame.mixer.init()

# Les variables de la taille de la fenêtre du jeu
HEIGHT = 720
WIDTH = 1280

# Classe du jeu avec ses variables
class Game:
    def __init__(self):
        self.running = True
        self.map = "village"
         # Initialisation du groupe des NPCs
        self.npc_group = pygame.sprite.Group()
        # Creer la fenêtre du jeu
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("MiniRPG")

        # Initialize other game components
        self.inventory = Inventory()
        self.healthbar = HealthBar(x=10, y=10)

        self.enemies_group = pygame.sprite.Group()

        # Charger la carte (tmx)
        tmx_data = pytmx.util_pygame.load_pygame("tiled/data/tmx/village.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        # map_layer va contenir tous les calques
        map_layer = pyscroll.orthographic.BufferedRenderer(
            map_data, self.screen.get_size()
        )
        map_layer.zoom = 2
        self.wall_group = pygame.sprite.Group()

        pygame.mixer.music.load("music/The_Witcher_3 _Wild_Hunt.mp3")
        pygame.mixer.music.set_volume(0.5)  # Adjust the volume as desired (0.0 to 1.0)
        pygame.mixer.music.play(-1)  # Start playing the music (-1 loops the music indefinitely)

        # Définr une liste qui va stocker les rectangles de collision
        self.walls = []
        for obj in tmx_data.objects:
            if obj.type == "collision":
                wall = Wall(obj.x, obj.y, obj.width, obj.height)
                self.wall_group.add(wall)
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
              
       # Spawn les NPCs -------------------------------------------------------------
        for obj in tmx_data.objects:
            if obj.name == "NPC_Maire":
                npc_maire = Maire(obj.x, obj.y, self.wall_group)
                self.npc_group.add(npc_maire)
            elif obj.name == "NPC_Tavernier":
                npc_tavernier = Tavernier(obj.x, obj.y, self.wall_group)
                self.npc_group.add(npc_tavernier)
            elif obj.name == "NPC_Forgeron":
                npc_forgeron = Forgeron(obj.x, obj.y, self.wall_group)
                self.npc_group.add(npc_forgeron)
            elif obj.name == "NPC_Explorer":
                npc_explorer = Explorer(obj.x, obj.y, self.wall_group)
                self.npc_group.add(npc_explorer)
        
        player_position = tmx_data.get_object_by_name("player_spawn1")
        self.player = NewPlayer(player_position.x, player_position.y, self.wall_group)

        # Dessiner le groupe de calque
        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=8)
        self.group.add(self.player)

        # On va définir le rectangle de collision pour entrer dans la forêt
        enter_forest = tmx_data.get_object_by_name("enter_forest")
        self.enter_forest_rect = pygame.Rect(
            enter_forest.x, enter_forest.y, enter_forest.width, enter_forest.height
        )

    # Fonction qui permet de passer du village à la forêt
    def switch_level(self):
        self.map = "forest"
          # Vider le groupe de PNJ
        self.npc_group.empty()
        # Charger la carte (tmx)
        tmx_data = pytmx.util_pygame.load_pygame("tiled/data/tmx/forest.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        # map_layer va contenir tous les calques
        map_layer = pyscroll.orthographic.BufferedRenderer(
            map_data, self.screen.get_size()
        )
        map_layer.zoom = 2

        self.wall_group = pygame.sprite.Group()

        # Définr une liste qui va stocker les rectangles de collision
        self.walls = []
        for obj in tmx_data.objects:
            if obj.type == "collision":
                wall = Wall(obj.x, obj.y, obj.width, obj.height)
                self.wall_group.add(wall)
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # Spawn les monstres -------------------------------------------------------------
        for obj in tmx_data.objects:
            if obj.name == "skeleton_spawn":
                skeleton1 = Skeleton1(obj.x, obj.y, self.wall_group)
                self.enemies_group.add(skeleton1)

        # Dessiner le groupe de calque
        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=9)
        self.group.add(self.player)
        for enemy in self.enemies_group:
            self.group.add(enemy)

        # Ajouter les NPCs au groupe Pyscroll
        for npc in self.npc_group:
            self.group.add(npc)    

        # On va définir le rectangle de collision pour entrer dans la forêt
        enter_forest = tmx_data.get_object_by_name("exit_forest_to_village")
        self.enter_forest_rect = pygame.Rect(
            enter_forest.x, enter_forest.y, enter_forest.width, enter_forest.height
        )

        # Au niveau de la forêt
        spawn_village_point = tmx_data.get_object_by_name("spawn_forest")
        self.player.position[0] = spawn_village_point.x + 50
        self.player.position[1] = spawn_village_point.y
        self.player.update_walls(self.wall_group)

    # Fonction qui permet de passer de la forêt au village
    def switch_back(self):
        self.map = "village"
        # Charger la carte (tmx)
        tmx_data = pytmx.util_pygame.load_pygame("tiled/data/tmx/village.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
      
        # Creer les NPCs
        self.npc_group = pygame.sprite.Group()
        for obj in tmx_data.objects:
            if obj.name == "NPC_Maire":
                maire = Maire(obj.x, obj.y, self.wall_group)
                self.npc_group.add(maire)
            elif obj.name == "NPC_Forgeron":
                forgeron = Forgeron(obj.x, obj.y, self.wall_group)
                self.npc_group.add(forgeron)
            elif obj.name == "NPC_Tavernier":
                tavernier = Tavernier(obj.x, obj.y, self.wall_group)
                self.npc_group.add(tavernier)
            elif obj.name == "NPC_Explorer":
                explorer = Explorer(obj.x, obj.y, self.wall_group)
                self.npc_group.add(explorer)
        
        # map_layer va contenir tous les calques
        map_layer = pyscroll.orthographic.BufferedRenderer(
            map_data, self.screen.get_size()
        )
        map_layer.zoom = 2

        self.wall_group = pygame.sprite.Group()

        # Définr une liste qui va stocker les rectangles de collision
        self.walls = []
        for obj in tmx_data.objects:
            if obj.type == "collision":
                wall = Wall(obj.x, obj.y, obj.width, obj.height)
                self.wall_group.add(wall)
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # Dessiner le groupe de calque
        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=8)
        self.group.add(self.player)
        self.enemies_group.empty()

        # On va définir le rectangle de collision pour entrer dans la forêt
        enter_forest = tmx_data.get_object_by_name("enter_forest")
        self.enter_forest_rect = pygame.Rect(
            enter_forest.x, enter_forest.y, enter_forest.width, enter_forest.height
        )

        spawn_village_point = tmx_data.get_object_by_name("enter_forest_exit")
        self.player.position[0] = spawn_village_point.x - 20
        self.player.position[1] = spawn_village_point.y
        self.player.update_walls(self.wall_group)

    # Fonction qui donne les conditions pour switcher de niveau
    def update(self):
        if self.map == "village" and self.player.rect.colliderect(
            self.enter_forest_rect
        ):
            self.switch_level()
            self.map = "forest"

        if self.map == "forest" and self.player.rect.colliderect(
            self.enter_forest_rect
        ):
            self.switch_back()
            self.map = "village"
    
    def pause_music(self):
        pygame.mixer.music.pause()

    def resume_music(self):
        pygame.mixer.music.unpause()

    def stop_music(self):
        pygame.mixer.music.stop()

    def handle_keypress(self, key):
        if key == pygame.K_F3:  # Press 'F3' to pause the music
            self.pause_music()
        elif key == pygame.K_F2:  # Press 'F2' to resume the music
            self.resume_music()
        elif key == pygame.K_F1:  # Press 'F1' to stop the music
            self.stop_music()

    # Fonction qui run le jeu et dans laquelle se trouve la boucle
    def run(self):
        clock = pygame.time.Clock()
        
        # Boucle du jeu

        while self.running:
            self.update()
            if self.player.attacking:
                self.player.attack()
            self.player.move()
            for enemy in self.enemies_group:
                enemy.update_enemy(self.player)
            self.group.update()
            self.group.center(self.player.rect.center)
            #NPC
            for npc in self.npc_group:
                npc.update_NPC()
            self.group.add(self.npc_group)

            # On va dessiner les calques sur le screen
            self.group.draw(self.screen)
            self.inventory.render(self.screen)
            self.healthbar.render(self.screen)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    self.handle_keypress(event.key)
                    if event.key == pygame.K_z or event.key == pygame.K_UP:
                        self.player.jump()
                    if event.key == pygame.K_i:  # Toggle inventory visibility on "i" key press
                        self.inventory.toggleVisibility()
                    if event.key == pygame.K_SPACE:  # Assuming space key causes damage to the player
                        damage_amount = 1  # Adjust the damage amount as per your requirements
                        self.healthbar.takeDamage(damage_amount)
                    if event.key == pygame.K_h:  # Assuming "h" key triggers healing
                        healing_amount = 1  # Adjust the healing amount as per your requirements
                        self.healthbar.Heal(healing_amount)
                    if event.key == pygame.K_a or event.key == pygame.K_RETURN:
                        if not self.player.attacking:
                            self.player.attacking = True
                            self.player.attack()
                            self.player.attack_counter = 1  # Premiere attaque
                        else:
                            if self.player.attack_counter < 4:
                                self.player.attack_counter += 1

            clock.tick(60)
        pygame.quit()
