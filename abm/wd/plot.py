import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame


class Plotter:
    """
    plots statistics collected by a DataCollector object
    """

    def plotData(self, dc):
        """
        plots statistics of data collected by a DataCollector

        :param dc: the DataCollector
        """
        rick = dc.getDataFrame('rick')
        friends = dc.getDataFrame('friends')
        enemies = dc.getDataFrame('enemies')
        zombies = dc.getDataFrame('zombies')
        humans = friends + enemies + rick

        timesteps = len(rick.iloc[0])

        ricks_death = rick.sum(1)
        ricks_death_mean = ricks_death.mean()
        # ricks_death_min = ricks_death.min()
        # ricks_death_max = ricks_death.max()

        sns.set_context('talk')
        plt.plot(zombies.mean(), color='r')
        plt.fill_between(zombies.columns, zombies.max(), zombies.min(),
                         color='r', alpha=.33)

        plt.plot(humans.mean(), color='g')
        plt.fill_between(humans.columns, humans.max(), humans.min(), color='g',
                         alpha=.33)

        ymax = self.ylim(zombies, humans)
        plt.plot((ricks_death_mean, ricks_death_mean), (0, ymax), color='b')
        # plt.fill_between([ricks_death_min, ricks_death_max], [0, 0], [ymax,
        #  ymax], color='b', alpha=.33)

        plt.title("The Walking Dead")
        plt.legend(['Zombies', 'Humans', 'Rick\'s death'], loc=7, frameon=True)
        plt.xlim(xmax=timesteps)
        plt.ylabel('Population')
        plt.xlabel('Simulation time')
        plt.show()

    @staticmethod
    def ylim(zombies: DataFrame, humans: DataFrame) -> int:
        """
        finds the limit for the y-axis of the plot, i.e. the max population
        of either zombies or humans throughout the whole simulation

        :param zombies:
        :param humans:
        :return:
        """
        max_zombies = zombies.max().max()
        max_humans = humans.max().max()
        return max(max_zombies, max_humans)
