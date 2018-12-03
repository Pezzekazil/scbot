import pgbot
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer


run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Protoss, pgbot.PgBot()),
    Computer(Race.Terran, Difficulty.Easy)
], realtime=False)