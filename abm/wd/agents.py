from random import random, choice
from abm.log import Logger
from abm.agents import MovingAgent, Agent
from settings import SCENARIO, SCENARIO_IMMORTAL_ZOMBIES, CHANCE_TO_KILL_ZOMBIE, \
    SCENARIO_KILLABLE_ZOMBIES, SCENARIO_MOVING_KILLABLE_ZOMBIES, LOGGER


class Rick(MovingAgent):
    """
    Rick - a moving agent
    """

    def do(self):
        """
        implements the behavior of rick

        whenever Rick has moved already, his behavior is skipped for the
        current timestep. Otherwise, when rick has no zombies around him,
        he is happy and does nothing. If there are zombies around, rick tries
        to find a candidate to swap position with. The candidate he looks for
        is an enemy of his neighborhood, namely the one with the least amount
        of zombies in his neighborhood. If rick doesn't find an enemy,
        he looks for a friend to swap with.
        """
        if self._skip:
            return

        if len(self.getNeighborNodes(ZombieFactory.getZombieType())) == 0:
            LOGGER("No Zombies nearby. %s feels safe and does nothing" % self,
                   Logger.LEVEL_DETAILS)
            return

        # when there are any zombies, rick tries to swap with an enemy
        candidate = self.__get_candidate_to_sacrifice(EnemyOfRick)

        # if there is no enemy around, he simply sacrifices a friends life
        if candidate is None:
            candidate = self.__get_candidate_to_sacrifice(FriendOfRick)

        # if he finds someone to swap, he swaps
        if candidate is None:
            LOGGER("%s couldn't seems to be surronded by zombies. This is "
                   "gonna be tough" % self, Logger.LEVEL_DETAILS)
        else:
            LOGGER("%s swaps position with %s" % (self, candidate),
                   Logger.LEVEL_DETAILS)
            self.swapPosition(candidate)

    def getName(self) -> str:
        """
        :returns the name of the object. Used for logging
        """
        return "Rick"

    def __get_candidate_to_sacrifice(self, agent_type):
        """
        a candidate rick can sacrifice.

        rick tries to find the least endangered neighbor. The least
        endangered neighbor is the one with the least amount of zombies in
        his neighborhood.

        :param agent_type: class of the candiate rick is looking for
        :return: the optimal candidate of None if none was found
        """
        neighbors = self.getNeighborNodes(agent_type)

        if len(neighbors) > 0:
            # find the least threatened neighbor, i.e. the one with the
            # least amount of zombies around
            endangered = lambda agent: len(
                self._env.getAgent(agent).getNeighborNodes(
                    ZombieFactory.getZombieType()))
            return self._env.getAgent(min(neighbors, key=endangered))
        else:
            return None


class FriendOfRick(MovingAgent):
    """
    a friend of rick - a moving agent
    """

    def do(self):
        """
        implements the behavior of rick's friend

        whenever the friend has moved already, his behavior is skipped for the
        current timestep. Otherwise, when he is close to rick (i.e. a direct
        neighbor of rick), he is happy and does nothing. If he is not
        directly connected to rick, he swaps with a common neighbor or does
        nothing if he doesn't find one.
        """
        if self._skip:
            return

        if self._env.isRickDead():
            LOGGER("Rick is dead. %s strews about helplessly" % self,
                   Logger.LEVEL_DETAILS)
            return

        if len(self.getNeighborNodes(Rick)) > 0:
            LOGGER("%s is close to rick - everything is ok" % self,
                   Logger.LEVEL_DETAILS)
            return

        # try to find common neighbors
        rick = self._env.getAgent(self._env.getRick())
        ricks_neighbors = rick.getNeighborNodes(FriendOfRick, EnemyOfRick,
                                                ZombieFactory.getZombieType())
        friends_neighbors = self.getNeighborNodes(FriendOfRick, EnemyOfRick,
                                                  ZombieFactory.getZombieType())
        common_neighbors = list(
            set(ricks_neighbors).union(set(friends_neighbors)))

        # if there is none, the friend resigns
        if len(common_neighbors) == 0:
            LOGGER("%s couldn't find anyone to swap with - he might be "
                   "lost ...", self, Logger.LEVEL_DETAILS)
            return

        # if there is a common neighbor, the friend gets his place
        if len(common_neighbors) > 0:
            agent = self._env.getAgent(choice(common_neighbors))
            self.swapPosition(agent)
            return

    def getName(self) -> str:
        """
        :returns the name of the object. Used for logging
        """
        return "FriendOfRick"


class EnemyOfRick(Agent):
    """
    an enemy of rick

    an enemy does nothing except for hanging around ...
    """

    def getName(self) -> str:
        """
        :returns the name of the object. Used for logging
        """
        return "EnemyOfRick"


class Zombie(Agent):
    """
    A zombie

    :param aggressiveness: the aggressiveness with which the zombie tries to
    attack it's victim
    """

    def __init__(self, aggressiveness: float):
        super().__init__()
        self.__aggressiveness = aggressiveness

    def do(self):
        """
        implements the behavior of a zombie

        a zombie tries to find humans in its neighborhood and tries to eat
        the which turns them into zombies too. Depending on its
        aggressiveness, the zombie succeeds. When there is no victim around,
        the zombie does nothing.
        """
        victims = self.getNeighborNodes(Rick, FriendOfRick, EnemyOfRick)
        for victim in victims:
            LOGGER("%s: attacks %s" % (self, self._env.getAgent(victim)),
                   Logger.LEVEL_DETAILS, end="")

            # the zombie has a certain chance of getting its victim
            if random() < self.__aggressiveness:
                LOGGER(" ... and wins", Logger.LEVEL_DETAILS)
                self._env.setAgent(victim, ZombieFactory.getInstance(
                    self.__aggressiveness))
            else:
                LOGGER(" ... but looses", Logger.LEVEL_DETAILS)
            break
        else:
            LOGGER("%s: cannot find anyone to eat" % self, Logger.LEVEL_DETAILS)

    def getName(self) -> str:
        """
        :returns the name of the object. Used for logging
        """
        return "Zombie"


class KillableZombie(Zombie):
    """
    A killable zombie

    :param aggressiveness: the aggressiveness with which the zombie tries to
    attack it's victim
    """

    def __init__(self, aggressiveness: float):
        super().__init__(aggressiveness)
        self.__alive = True

    def kill(self):
        """
        kills a zombie
        """
        self.__alive = False

    def isAlive(self) -> bool:
        """
        :returns whether the zombie is still alive
        """
        return self.__alive

    def do(self):
        """
        the zombies behavior

        a killable zombie looks for victims in its neighborhood. Any victim
        attacked by the zombie tries to kill the zombie. When the zombie
        survives all of the attacks, it tries to eat its victims (inherited
        from parent behavior)
        """
        if not self.__alive:
            return

        victims = self.getNeighborNodes(Rick, FriendOfRick, EnemyOfRick)
        for victim in victims:
            LOGGER("%s: attacks %s" % (self, self._env.getAgent(victim)),
                   Logger.LEVEL_DETAILS, end="")

            if random() <= CHANCE_TO_KILL_ZOMBIE:
                self.kill()
                return

        super().do()


class MovableKillableZombie(KillableZombie):
    """
    A movable, killable zombie
    """

    def do(self):
        """
        the zombies behavior

        moving is basically modelled by setting a random link to another node
        within the graph. After doing so, the zombie tries to fight and eat
        it's human neighbors (inherited from parents behavior)
        """
        self._env.setRandomLink(self)
        super().do()


class ZombieFactory:
    """
    produces zombies
    """

    @staticmethod
    def getInstance(aggressiveness: int):
        """
        depending on global settings, this method returns a new Zombie
        instance with an aggressiveness set. The instance can either be
        Zombie, KillableZombie or MovingKillableZombie.

        :param aggressiveness: the aggressiveness of the zombie.
        :return: a Zombie instance
        """
        if SCENARIO & SCENARIO_IMMORTAL_ZOMBIES == SCENARIO_IMMORTAL_ZOMBIES:
            return Zombie(aggressiveness)
        elif SCENARIO & SCENARIO_KILLABLE_ZOMBIES == SCENARIO_KILLABLE_ZOMBIES:
            return KillableZombie(aggressiveness)
        elif SCENARIO & SCENARIO_MOVING_KILLABLE_ZOMBIES == SCENARIO_MOVING_KILLABLE_ZOMBIES:
            return MovableKillableZombie(aggressiveness)

    @staticmethod
    def getZombieType():
        """
        :returns: the class of Zombies being produced by this factory (
        depending on global settings)
        """
        if SCENARIO & SCENARIO_IMMORTAL_ZOMBIES == SCENARIO_IMMORTAL_ZOMBIES:
            return Zombie.__class__
        elif SCENARIO & SCENARIO_KILLABLE_ZOMBIES == SCENARIO_KILLABLE_ZOMBIES:
            return KillableZombie.__class__
        elif SCENARIO & SCENARIO_MOVING_KILLABLE_ZOMBIES == SCENARIO_MOVING_KILLABLE_ZOMBIES:
            return MovableKillableZombie.__class__
