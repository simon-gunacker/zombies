from abm.environment import EnvironmentOperable


class AgentExecutor(EnvironmentOperable):
    """
    an operable for executing an agent

    this is used when a topology gets traversed to
    ensure the agents of a node perform their behavior
    when visited
    """

    def __call__(self, node: int):
        """
        executes the current agents behavior
        """
        agent = self._env.getAgent(node)
        agent.do()
