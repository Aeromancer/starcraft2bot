
import sc2, asyncio

from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer

from sc2.constants import SUPPLYDEPOT, SCV, COMMANDCENTER, REFINERY, ENGINEERINGBAY, BARRACKS, MARINE

class basebot(sc2.BotAI):
    async def on_step(self, iteration):
        #what to do every step

        await self.distribute_workers()  # in sc2/bot_ai.py
        await self.build_worker()
        await self.build_supplydepot()
        await self.expand()
        await self.build_refinery()



    async def build_worker(self):
        for cc in self.units(COMMANDCENTER).ready.noqueue:
            if self.can_afford(SCV):
                await self.do(cc.train(SCV))
                await asyncio.sleep(0.1)

    async def build_supplydepot(self):
        if self.supply_left < 5 and not self.already_pending(SUPPLYDEPOT):
            ccs = self.units(COMMANDCENTER).ready 
            if ccs.exists:
                if self.can_afford(SUPPLYDEPOT):
                    await self.build(SUPPLYDEPOT, near = ccs.first)

    async def expand(self):
        if self.units(COMMANDCENTER).amount < 2 and self.can_afford(COMMANDCENTER):
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
                if not self.units(REFINERY).closer_than(1.0, vaspene).exists:
                    await self.do(worker.build(REFINERY, vaspene))
                    await asyncio.sleep(0.1)

    async def offensive_force_buildings(self):
        if self.units(BARRACKS).ready.exists and self.units(SCV) > 20:
            if not self.units(ENGINEERINGBAY):
                if self.can_afford(ENGINEERINGBAY) and not self.already_pending(ENGINEERINGBAY):
                    await self.build(ENGINEERINGBAY)
                    await asyncio.sleep(0.1)
        else:
            if self.can_afford(BARRACKS) and not self.already_pending(BARRACKS):
                await self.build(BARRACKS)
                await asyncio.sleep(0.1)

    async def build_offensive_force(self):
        for brk in self.units(BARRACKS).ready.noqueue:
            if self.can_afford(MARINE) and self.supply_left > 0:
                await self.do(brk.train(MARINE))
                await asyncio.sleep(0.1) 







run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Terran, basebot()),
    Computer(Race.Zerg, Difficulty.Easy)
    ], realtime = True)

#Just a quick thing at the end to make sure I'm not dumb