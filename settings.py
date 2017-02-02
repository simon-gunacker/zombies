from abm.log import Logger

LOGGER = Logger.getInstance(Logger.LEVEL_NONE)

# simulation relevant parameters
SIMULATION_TRIALS = 5
SIMULATION_TIMESTEPS = 64
ZOMBIE_AGGRESSIVENESS = 0.8
CHANCE_TO_KILL_ZOMBIE = 0.8

# when changing these values, do
# not forget to change the offsets
# accordingly
# (see abm.wd.environment, in setup method)
RICKS_CLIQUE = 20
ENEMIES = 50
ZOMBIES = 200

# used to identify nodes by id
# consider changing the offsets when network sizes
# (see main file)
RICK_OFFSET = 0
ENEMY_OFFSET = 100
ZOMBIE_OFFSET = 1000

SCENARIO_IMMORTAL_ZOMBIES = 1
SCENARIO_KILLABLE_ZOMBIES = 2
SCENARIO_MOVING_KILLABLE_ZOMBIES = 4

SCENARIO = SCENARIO_MOVING_KILLABLE_ZOMBIES
