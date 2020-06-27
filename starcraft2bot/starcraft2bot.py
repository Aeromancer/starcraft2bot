
import sc2, asyncio, random 

from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer

from sc2.constants import SUPPLYDEPOT, SCV, COMMANDCENTER, REFINERY, ENGINEERINGBAY, BARRACKS, MARINE, FACTORY, STARPORT, ARMORY, MEDIVAC

class basebot(sc2.BotAI):

    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        

    async def on_step(self, iteration):
        #what to do every step
        self.iteration = iteration 
        await self.distribute_workers()  # in sc2/bot_ai.py
        await self.build_worker()
        await self.build_supplydepot()
        await self.expand()
        await self.build_refinery()
        await self.offensive_force_buildings()
        await self.build_offensive_force()
        await self.attack()


    async def build_worker(self):
        for cc in self.units(COMMANDCENTER).ready.idle:
            if self.can_afford(SCV):
                if (self.units(COMMANDCENTER).amount * 16 + self.units(REFINERY).amount * 3 + 4) > self.units(SCV).amount:    
                    await self.do(cc.train(SCV))
                    await asyncio.sleep(0.1)

    async def build_supplydepot(self):
        if self.supply_left < 5 and not self.already_pending(SUPPLYDEPOT):
            ccs = self.units(COMMANDCENTER).ready 
            if ccs.exists:
                if self.can_afford(SUPPLYDEPOT):
                    await self.build(SUPPLYDEPOT, near = ccs.first)

    async def expand(self):
        if self.units(COMMANDCENTER).amount < 3 and self.can_afford(COMMANDCENTER):
            await self.expand_now()

    async def build_refinery(self):
        for cc in self.units(COMMANDCENTER).ready:
            vaspenes = self.state.vespene_geyser.closer_than(10.0, cc)
            for vaspene in vaspenes:
                if not self.can_afford(REFINERY):
                    break
                worker = self.select_build_worker(vaspene.position)
                if worker is None:
                    break 
                if not self.units(REFINERY).closer_than(1.0, vaspene).exists and not self.already_pending(REFINERY):
                    await asyncio.sleep(0.1)
                    if self.units(SCV).amount > 16:
                        await self.do(worker.build(REFINERY, vaspene))
                        

    async def offensive_force_buildings(self):
        if self.units(BARRACKS).ready.exists and self.units(SCV).amount > 20:
            if not self.units(ENGINEERINGBAY):
                if self.can_afford(ENGINEERINGBAY) and not self.already_pending(ENGINEERINGBAY) and self.units(ENGINEERINGBAY).amount < 1:
                    ccs = self.units(COMMANDCENTER).ready.random
                    await self.build(ENGINEERINGBAY, near = ccs)
                    await asyncio.sleep(0.1)
        if self.units(SUPPLYDEPOT).ready.exists:
            supplydepot = self.units(COMMANDCENTER).ready.random 
            if self.can_afford(BARRACKS) and (self.units(BARRACKS).amount < (self.units(COMMANDCENTER).amount * 2)) and not self.already_pending(BARRACKS):
                await self.build(BARRACKS, near = supplydepot )

        if self.units(BARRACKS).ready.exists:
            bloc = self.units(BARRACKS).ready.first
            if self.can_afford(FACTORY) and self.units(FACTORY).amount < 1:
                await self.build(FACTORY, near = bloc)

        if self.units(FACTORY).ready.exists:
            bloc = self.units(COMMANDCENTER).ready.first 
            if self.can_afford(ARMORY) and self.units(ARMORY).amount < 1:
                await self.build(ARMORY, near = bloc)

        
            
            if self.can_afford(STARPORT) and self.units(STARPORT).amount < 4 and self.units(COMMANDCENTER).amount > 1:
                await self.build(STARPORT, near = bloc)

    async def build_offensive_force(self):
        for brk in self.units(BARRACKS).ready.idle:
            if self.can_afford(MARINE) and self.supply_left > 0:
                await self.do(brk.train(MARINE))
                await asyncio.sleep(0.1) 

        for stp in self.units(STARPORT).ready.idle:
            if self.can_afford(MEDIVAC) and self.supply_left > 0 and self.units(MEDIVAC).amount < 5:
                await self.do(stp.train(MEDIVAC))
                await asyncio.sleep(0.1)

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def attack(self):
        if self.units(MARINE).amount > 40:
            for s in self.units(MARINE).idle:
                await self.do(s.attack(self.find_target(self.state)))
            
        elif self.units(MARINE).amount > 5:
            if len(self.known_enemy_units) > 0:
                for s in self.units(MARINE).idle:
                    await self.do(s.attack(random.choice(self.known_enemy_units)))






run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Terran, basebot()),
    Computer(Race.Random, Difficulty.Medium)
    ], realtime = True)

#Just a quick thing at the end to make sure I'm not dumb