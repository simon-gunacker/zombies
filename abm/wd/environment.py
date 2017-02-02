from random import choice, randint

import networkx as nx

from abm.environment import Environment
from abm.log import Logger
from abm.operations import AgentExecutor
from abm.wd.agents import Rick, FriendOfRick, EnemyOfRick, ZombieFactory
from abm.wd.plot import Plotter
from abm.wd.stats import DataCollector
from settings import LOGGER, ENEMY_OFFSET, RICK_OFFSET, ZOMBIE_OFFSET


class WalkingDeadEnv(Environment):
    """
    an environment for handling the walking dead scenario

    :param ricks_clique: the size of ricks clique
    :param enemies: the size of the enemies clique
    :param zombies: the size of the zombies graph
    :param zombie_aggressiveness: the likelihood a zombie eats a human
    """

    def __init__(self, ricks_clique: int, enemies: int, zombies: int,
                 zombie_aggressiveness: float):
        super().__init__(nx.Graph())
        self.__rick = -1
        self.__zombie_aggresiveness = zombie_aggressiveness
        self.setup(ricks_clique, enemies, zombies, zombie_aggressiveness)

    def setRick(self, index: int):
        """
        sets rick on a node and holds a reference to that node

        :param index: the index of the node rick is placed on
        """
        self.__rick = index
        self.setAgent(index, Rick())

    def getRick(self) -> int:
        """
        :returns the index of the node rick is currently placed on
        """
        return self.__rick

    def killedRick(self):
        """
        kills rick

        the node index is set to -1 internally
        """
        self.__rick = -1

    def isRickDead(self) -> bool:
        """
        :returns whether rick is still alive
        """
        return self.__rick == -1

    def setRandomLink(self, from_agent):
        """
        links an agent to another, random agent

        :param from_agent: the agent to link from
        """
        self._graph.add_edge(from_agent.getIndex(), choice(self._graph.nodes()))

    def runSimulation(self, time: int, trials: int):
        """
        runs a simulation

        it traverses the topology for a given time (multiple trials). In each
        traversal all agents are executed and data is collected. Finally,
        the collected data is plotted.

        :param time: the time the simulation should run
        :param trials: the trials of the simulation
        """
        ae = AgentExecutor()
        dc = DataCollector()

        for i in range(trials):
            LOGGER("Running Trial %d" % i, Logger.LEVEL_ITERATIONS)
            dc.setTrial(i)
            # get initial state (t=0) before agents act
            self.traverseTopology(dc)
            # for timestep: let agents act and get state
            self.traverseTopologyUntil(time, ae, dc)
            dc.resetTime()
        # dc.dump()
        Plotter().plotData(dc)

    def traverseTopologyUntil(self, time: int, *ops):
        """
        traverses the topology multiple times. The topology is saved before and
        restored after traversal.

        :param time: number of traversal iterations
        :param ops: operations that should be executed on each node in each
        traversal step
        """
        self.saveCurrentGraph()
        super().traverseTopologyUntil(time, *ops)
        self.loadSavedGraph()

    def setup(self, ricks_clique: int, enemies_clique: int, zombies_clique: int,
              zombie_aggressiveness: float):
        """
        sets up the initial scenario with the given parameters.

        Rick's clique and the enemies are modeled as a connected graph. The
        zombies are modeled as a random graph. Then, all these graphs are
        merged together by connecting a fraction of nodes from each graph
        with nodes from the other graphs.

        :param ricks_clique: the size of ricks clique
        :param enemies_clique: the size of the enemies clique
        :param zombies_clique: the size of the zombies graph
        :param zombie_aggressiveness: the likelihood a zombie eats a human
        """
        # rick and friends are a clique
        rick_and_friends = nx.complete_graph(ricks_clique).to_undirected()

        # enemies are a clique
        enemies = nx.complete_graph(enemies_clique).to_undirected()

        # zombies are power law distributed
        zombies = nx.scale_free_graph(zombies_clique).to_undirected()

        # lets merge them all together in one world
        self.__copy_graph(rick_and_friends, RICK_OFFSET)
        self.__copy_graph(enemies, ENEMY_OFFSET)
        self.__copy_graph(zombies, ZOMBIE_OFFSET)

        # and place some links between them
        links_rick_enemies = randint(1, max(int(ricks_clique * 0.2), 2))
        links_rick_zombies = randint(1, max(int(ricks_clique * 0.4), 2))
        links_enemies_zombies = randint(1, max(int(enemies_clique * 0.4), 2))
        range_rick = range(RICK_OFFSET, ricks_clique)
        range_enemies = range(ENEMY_OFFSET, ENEMY_OFFSET + enemies_clique)
        range_zombies = range(ZOMBIE_OFFSET, ZOMBIE_OFFSET + zombies_clique)
        self.__add_random_links(range_rick, range_enemies, links_rick_enemies)
        self.__add_random_links(range_rick, range_zombies, links_rick_zombies)
        self.__add_random_links(range_enemies, range_zombies,
                                links_enemies_zombies)

        # set agents
        for i in range(ricks_clique):
            self.setAgent(i, FriendOfRick())
        for i in range(ENEMY_OFFSET, ENEMY_OFFSET + enemies_clique):
            self.setAgent(i, EnemyOfRick())
        for i in range(ZOMBIE_OFFSET, ZOMBIE_OFFSET + zombies_clique):
            self.setAgent(i, ZombieFactory.getInstance(zombie_aggressiveness))

        self.setRick(0)

    def __copy_graph(self, source, offset: int):
        """
        copies the given graph into the internal topology

        :param source: the graph to copy
        :param offset: the offset is added to a nodes index to make sure the
        index is not used multiple times within the internal topology
        """
        for node in source.nodes():
            self._graph.add_node(node + offset)
        for u, v in source.edges():
            self._graph.add_edge(u + offset, v + offset)

    def __add_random_links(self, noderange1: range, noderange2: range,
                           number_of_links: int):
        """
        adds random links to the internal topology.
        :param noderange1: range of nodes of the first community
        :param noderange2: range of nodes of the second community
        :param number_of_links: the number of links that should be set between
        the two communities
        """
        for i in range(number_of_links):
            u, v = choice(noderange1), choice(noderange2)
            self._graph.add_edge(u, v)
