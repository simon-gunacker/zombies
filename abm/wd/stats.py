import pandas as pd

from abm.environment import EnvironmentOperable
from abm.wd.agents import *


class DataCollector(EnvironmentOperable):
    """
    collects data throughout the simulation. This data is used for statistics
    to be plotted.
    """

    def __init__(self):
        super().__init__()
        self.__trial = 0
        self.__time = 0
        self.__data = {'rick': [], 'friends': [], 'enemies': [], 'zombies': []}

    def setTrial(self, trial: int):
        """
        sets the current trial. For each trial, a new line i appended to the
        collected data.

        :param trial: the trial to set the collector to
        """
        self.__data['rick'].append([])
        self.__data['friends'].append([])
        self.__data['enemies'].append([])
        self.__data['zombies'].append([])
        self.__trial = trial

    def resetTime(self):
        """
        resets the time
        """
        self.__time = 0

    def __call__(self, node: int):
        """
        overrides EnvironmentOperable.__call__(). Whenever the DataCollector
        is called, it checks the type of agent placed on the current node and
        increments the respective counter within a trial and timestep

        :param node: the index of the node the DataCollector should evaluate
        """
        agent = self._env.getAgent(node)
        if type(agent) == Rick:
            self.__data['rick'][self.__trial][self.__time] = 1
        elif type(agent) == FriendOfRick:
            self.__data['friends'][self.__trial][self.__time] += 1
        elif type(agent) == EnemyOfRick:
            self.__data['enemies'][self.__trial][self.__time] += 1
        elif issubclass(agent.__class__, Zombie):
            if type(agent) == Zombie or \
                    (type(agent) == KillableZombie and agent.isAlive()) or \
                    (type(agent) == MovableKillableZombie and agent.isAlive()):
                self.__data['zombies'][self.__trial][self.__time] += 1
        else:
            raise Exception("Unknown agent")

    def preProcess(self):
        """
        appends a new timestep to the datastructure
        initially, all counters of the new timestep are set to 0
        """
        self.__data['rick'][self.__trial].append(0)
        self.__data['friends'][self.__trial].append(0)
        self.__data['enemies'][self.__trial].append(0)
        self.__data['zombies'][self.__trial].append(0)

    def postProcess(self):
        """
        increases the timestep by one
        """
        self.__time += 1

    def dump(self):
        """
        prints the collected data
        """
        for key in self.__data.keys():
            print()
            print("----- %s -----" % key)
            print(self.getDataFrame(key))

    def getDataFrame(self, entity: str) -> pd.DataFrame:
        """
        converts the collected data of an enitiy into a pandas.DataFrame
        :param entity: the entity whose data should be converted
        :return: a pandas.DataFrame containing the collected data
        """
        index = ["Trial %03d" % (i + 1) for i in range(
            len(self.__data[entity]))]
        return pd.DataFrame(self.__data[entity], index=index)
