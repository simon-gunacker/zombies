from abm.wd.environment import WalkingDeadEnv
from settings import RICKS_CLIQUE, ENEMIES, ZOMBIES, ZOMBIE_AGGRESSIVENESS, SIMULATION_TRIALS, \
    SIMULATION_TIMESTEPS, LOGGER

if __name__ == '__main__':
    env = WalkingDeadEnv(RICKS_CLIQUE, ENEMIES, ZOMBIES, ZOMBIE_AGGRESSIVENESS)
    env.runSimulation(SIMULATION_TIMESTEPS, SIMULATION_TRIALS)

