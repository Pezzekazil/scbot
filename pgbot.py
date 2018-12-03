import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import UnitTypeId as units
from sc2.units import Units
sc2.constants


class PgBot(sc2.BotAI):
    async def on_step(self, iteration):
        # what to do every step
        await self.distribute_workers()  # in sc2/bot_ai.py
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilator()
        await self.expand()
        await self.offensive_force_buildings()
        await self.build_offensive_force()
        await self.attack()

    async def build_workers(self):
        for nexus in self.units(units.NEXUS).ready.noqueue:
            can_afford = self.can_afford(units.PROBE)
            too_many = self.units(units.PROBE).amount // self.units(units.NEXUS).amount >= 19
            if can_afford and not too_many:
                await self.do(nexus.train(units.PROBE))
    
    async def build_pylons(self):
        short_on_supply = self.supply_left < 5 * self.get_production_facilities()
        pylon_already_building = self.already_pending(units.PYLON)
        if short_on_supply and not pylon_already_building:
            # The nexus needs to be ready to be able to build a pylon
             nexuses = self.units(units.NEXUS).ready
             if nexuses.exists:
                 if self.can_afford(units.PYLON):
                     await self.build(units.PYLON, near=nexuses.first)

    async def build_assimilator(self):
        """
        For each nexus, picks the two closest vespenes. 
        If any of the two is free, then build an assimilator.
        """
        for nexus in self.units(units.NEXUS).ready:
            vespenes = self.state.vespene_geyser.sorted_by_distance_to(nexus)[:2]
            for vespene in vespenes:
                if not self.can_afford(units.ASSIMILATOR):
                    break
                if not self.units(units.ASSIMILATOR).closer_than(1.0, vespene).exists:
                    worker = self.select_build_worker(vespene.position)
                    if worker is None:
                        break
                    # TODO: the worker stays there instead of keep going with its activity
                    await self.do(worker.build(units.ASSIMILATOR, vespene))

    async def expand(self):
        # TODO: Not working because I do not know how to count probes on nexus
        # workers_more_than = lambda x : self.units(units.NEXUS).gathering.count() > x
        can_afford = self.can_afford(units.NEXUS)
        getting_worker_capped = lambda x : self.units(units.PROBE).amount // self.units(units.NEXUS).amount > x
        if can_afford and getting_worker_capped(14):
            await self.expand_now()

    async def offensive_force_buildings(self):
        if self.units(units.PYLON).ready.exists:
            # TODO: this should not be random
            pylon = self.units(units.PYLON).ready.random
            if self.units(units.GATEWAY).ready.exists:
                if not self.units(units.CYBERNETICSCORE):
                    if (
                        self.can_afford(units.CYBERNETICSCORE) 
                        and not self.already_pending(units.CYBERNETICSCORE)
                        ):
                        await self.build(units.CYBERNETICSCORE, near=pylon)
                elif (
                    self.units(units.GATEWAY).amount / self.units(units.NEXUS).amount < 2
                    and self.can_afford(units.GATEWAY)
                    and not self.already_pending(units.GATEWAY)
                ):
                    await self.build(units.GATEWAY, near=pylon)
            else:
                if self.can_afford(units.GATEWAY) and not self.already_pending(units.GATEWAY):
                    await self.build(units.GATEWAY, near=pylon)

    async def build_offensive_force(self):
        for gw in self.units(units.GATEWAY).ready.noqueue:
            if self.can_afford(units.STALKER) and self.supply_left > 0:
                await self.do(gw.train(units.STALKER))

    async def attack(self):
        if self.units(units.STALKER).amount > 15:
            for s in self.units(units.STALKER).idle:
                await self.do(s.attack(self.find_target(s)))
        if self.units(units.STALKER).amount > 5:
            for s in self.units(units.STALKER).idle:
                if self.known_enemy_units.exists:
                    await self.do(s.attack(self.known_enemy_units.random))

    def get_production_facilities(self):
        production_facilities = []
        if self.units(units.NEXUS).exists:
            production_facilities.append(self.units(units.NEXUS).amount)
        if self.units(units.GATEWAY).exists:
            production_facilities.append(self.units(units.GATEWAY).amount)
        if production_facilities:
            return sum(production_facilities)
        else:
            0

    def find_target(self, unit):
        if self.known_enemy_units.exists:
            return self.known_enemy_units.closest_to(unit)
        elif self.known_enemy_structures.exists:
            return self.known_enemy_structures.closest_to(unit)
        else:
            return self.enemy_start_locations[0]


            
            