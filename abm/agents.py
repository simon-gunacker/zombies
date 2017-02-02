from abm.log import Logger
from settings import LOGGER


class Agent:
    """
    Can be placed on graph nodes. Perform actions there.

    This class is used as a general class. Concrete agent implementations are
    supposed to derive it.
    """

    def __init__(self):
        self._env = None
        self._index = None

    def setIndex(self, index: int):
        """
        used by the environment to set the node index of a node an agent
        is placed on.

        :param index: the node index
        """
        self._index = index

    def getIndex(self) -> int:
        """
        :returns the node index of the node the agent is currently placed
        on.
        """
        return self._index

    def setEnv(self, env):
        """
        sets the agents environment. Any agent needs to know its
        environment for finding neighbors and so on.

        :param env: the environment the agent is acting in
        """
        self._env = env

    def getNeighborNodes(self, *types):
        """
        :returns the agents neighbor nodes (only those of the given
        types)
        :param types: a list of types of neighbors we are interested in
        """
        g = self._env.getTopology()
        return [neighbor for neighbor in g.neighbors(self._index) if
                type(g.node[neighbor]['agent']) in types]

    def getNeighborAgents(self, *types):
        """
        :returns the agents neighbor agents (only those of the given
        types)
        :param types: a list of types of neighbors we are interested in
        """
        g = self._env.getTopology()
        return [g.node[x] for x in self.getNeighborNodes(*types)]

    def do(self):
        """
        this method should be overridden by concrete agents to implement
        their behavior
        """
        LOGGER("%s: does nothing" % self, Logger.LEVEL_DETAILS)

    def getName(self) -> str:
        """
        :returns an agents name and should be overridden
        by all child agents.
        """
        return NotImplementedError

    def __str__(self):
        return "%s (%d)" % (self.getName(), self._index)


class MovingAgent(Agent):
    """
    a moving agent can swap positions (with a neighbor)

    The moving agent can be skipped. That is, if he had already swapped
    position, he is not supposed to act a second time within the current
    traversal
    """

    def __init__(self):
        super().__init__()
        self._skip = False

    def do(self):
        """
        behavoir of the agent. Has to be overridden by child agents.

        When overriding, super().do() has to be called in the beginning to
        ensure the skipping behavior is not lost.
        """
        if self._skip:
            return

    def swapPosition(self, other):
        """
        swaps position (node) with another agent.

        This is considered to be a move on a graph. The environment makes sure
        the other agent is a neighbor, however, this method is kept general.

        :param other: the agent to swap position with
        """
        if not self._skip:
            index_before_move = other.getIndex()
            self._env.setAgent(self._index, other)
            self._env.setAgent(index_before_move, self)
        self._skip = not self._skip
