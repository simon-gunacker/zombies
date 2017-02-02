from abm.log import Logger
from settings import LOGGER


class EnvironmentOperable:
    """
    An operation that can be performed on a node.

    This is basically what the visitor pattern calls a visitor. I did not
    name it this way though since the node itself has no accept method.
    Anyway, this method is supposed to be overridden by any operation that
    should be performed on a node during graph traversal. For an example,
    see operations.py.

    :param env: in most cases, the operable needs to know the env it is
    acting in. Currently, the env is set by
    `Environment().traverseTopology()` in any case.
    """

    def __init__(self, env=None):
        self._env = env

    def __call__(self, node: int):
        """
        override by child operable.

        This is where the actual operation happens. Operable is implemented as a
        callable and calld by traverseTopology using __call__(). Parameters
        cannot be passed here since it would violate generality. To get
        parameters in here, make them attributes of the child class.

        :param node: the index of the node on which the operation is performed
        """
        raise NotImplementedError

    def setEnvironment(self, env):
        """
        used by traverseTopology() to make sure every Operable knows the
        env it is operating in.

        :param env: the environment of the operable
        """
        self._env = env

    def preProcess(self):
        """
        used before traversing the topology. Override in children.
        """
        pass

    def postProcess(self):
        """
        used after traversing the topology is done. Override in children.
        """
        pass


class Environment:
    """
    The environment agents are operating within. Is supposed to be
    derived for concrete usage.

    :param graph: a networkx.Graph which is used as the environments topology
    """

    def __init__(self, graph):
        self._graph = graph
        self.__initial_graph = None

    def saveCurrentGraph(self):
        """
        saves a graph

        saving means storing the current graph in memory. This can be used when
        agents modify the graph and the original state of the graph has to be
        restored at some point in time. I use this for running different trials
        on a scenario.
        """
        self.__initial_graph = self._graph.copy()

    def loadSavedGraph(self):
        """
        loads a previously saved graph back into the internal topology
        reference
        """
        self._graph = self.__initial_graph.copy()

    def getAgent(self, index: int):
        """
        :returns the agent placed on a node
        :param index: the index of the node we want to retrieve the agent from
        """
        return self._graph.node[index]['agent']

    def setAgent(self, index: int, agent):
        """
        places an agent on a node

        whenever an agent is placed on a node, it holds the information which
        node it is placed on and a reference to the environment it is living in

        :param index: the index of the node the agent should be placed on
        :param agent: the agent to place on the node
        """
        agent.setIndex(index)
        agent.setEnv(self)
        self._graph.node[index]['agent'] = agent

    def getTopology(self):
        """
        :returns the networkx.Graph the environment is working on
        """
        return self._graph

    def traverseTopologyUntil(self, time: int, *ops):
        """
        traverses the environments topology multiple times

        :param time: the amount of steps the topology should be traversed
        :param *ops: a list of operations that should be executed on each node
        during traversal
        """
        for i in range(time):
            LOGGER("Running Timestep %d" % i, Logger.LEVEL_ITERATIONS)
            self.traverseTopology(*ops)

    def traverseTopology(self, *ops):
        """
        traverses the environments topology once

        :param *ops: a list of operations that should be executed on each node
        during traversal. Note that the ops might have some preProcess and
        postProcess steps. these are executed before and after a full traversal.
        """
        for op in ops:
            op.setEnvironment(self)
            op.preProcess()
            for x in self._graph.nodes():
                op(x)
            op.postProcess()
