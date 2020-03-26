import numpy as np 
import pandas as pd


from lib.enhance._utils import GEAR_TYPE
from lib.enhance._utils import ENHANCEMENT_LEVEL
from lib.enhance._utils import ENHANCE_TABLES_PATH
from lib.enhance._utils import BLACK_STONE_ARMOR_PRICE
from lib.enhance._utils import REBLATH_FAILSTACK_COSTS_TABLE_KEY

CLEANSING_COST = 1e5

class Strategy(object):
    """An abstract base class for a strategy class.
    
    """
    def __init__(self):
        pass
    
    def fs_cost(self, failstack_goal: int) -> float:
        raise NotImplementedError(
        "{} needs to be overloaded"
        "in the child classes.".format("fs_cost()")
    )

    def _cost_of_failstack(self, failstack_goal: int) -> float:
        raise NotImplementedError(
            "{} needs to be overloaded"
            "in the child classes.".format("_cost_of_failstack()"))

    def _all_failstack_price(self) -> pd.DataFrame:
        raise NotImplementedError(
            "{} needs to be overloaded"
            "in the child classes.".format("_all_failstack_price()"))



class Reblath14(Strategy):
    """Strategy class for Reblath failstack building.

    Calculations are based on the assumption that the failstack is built
    only using +14 Reblath armor piece. Each failstack is gained by enhancing
    a +14 Reblath armor piece with Black Stone (Armor).

    """
    def __init__(self):
        """
        Attributes:
            enhance_table: pd.DataFrame containing ehancement chances for green color armor
                depending on number of failstacks
        """
        self.reblath_enhancement = pd.read_hdf(ENHANCE_TABLES_PATH, GEAR_TYPE["green-armor"])
        self.reblath_fs_costs = None
        with pd.HDFStore(ENHANCE_TABLES_PATH, "r") as hdf:
            if "/" + REBLATH_FAILSTACK_COSTS_TABLE_KEY in hdf.keys():
                self.reblath_fs_costs = hdf.get(REBLATH_FAILSTACK_COSTS_TABLE_KEY)
    
    def fs_cost(self, failstack_goal : int) -> float:
        if self.reblath_fs_costs is not None:
            return self.reblath_fs_costs.loc[failstack_goal, "Cost"]
        else:
            self.reblath_fs_costs = self._recalculate_failstack_costs()
            return self.reblath_fs_costs.loc[failstack_goal, "Cost"]


    def _cost_of_failstack(self, failstack_goal: int) -> float:
        """Calculates cost of failstack building.

        Calculates the cost of building a failstack of *failstack_goal*
        stacks using only Reblath +14 armor. Does not include cost of repairs. 
        Includes only costs of Black Stone (Armor) and cleansing.

        Args:
            failstack_goal: Number of failstacks to gain by failstacking.

        Returns:
            Number of silver coins needed to build the failstack.

        Raises:
            ValueError: When the number of failstacks to obtain is lower than 0
        """
        # Raise ValueError, when the argument is not appropriate
        if (failstack_goal < 0):
            raise ValueError("_cost_of_failstack accepts only non-negative integers. Passed {}.".format(failstack_goal))
            
        # Calculate the cost of stack
        # First component is cost of black stones, second is cost of cleansing
        cost = (failstack_goal * BLACK_STONE_ARMOR_PRICE / self._failstack_proba(failstack_goal) + 
                    CLEANSING_COST * (1 / self._failstack_proba(failstack_goal) - 1))
        return cost


    def _failstack_proba(self, failstack_goal: int) -> float:
        """Calculates the probability of getting given failstack.

        Calculates the probability of getting 'failstack_goal'
        failures using only +14 Reblath strategy. 

        Usage:
            strat = Reblath14()
            print(strat._failstack_proba(5))

        Args:
            failstack_goal: number of failstack to achieve

        Returns:
            Probability of getting that failstack. Value between 0 and 1.
        """
        probability = np.product(1 - self.reblath_enhancement.loc[:failstack_goal - 1, ENHANCEMENT_LEVEL["15"]])
        return probability
        
    def _recalculate_failstack_costs(self) -> pd.DataFrame:
        """Recalculates costs of failstacking

        Recalculates the cost of failstacking and returns a data-frame
        with costs. 

        Returns:
            DataFrame of size (121, 2) with two columns: FS and Cost.
        """
        fs_costs = [self._cost_of_failstack(fs) for fs in range(self.reblath_enhancement.shape[0])]
        return pd.DataFrame({"FS" : range(self.reblath_enhancement.shape[0]), "Cost" : fs_costs})

    def _all_failstack_price(self) -> pd.DataFrame:
        """Returns cost of failstack building for all failstack value

        Returns:
            A column of pd.DataFrame object.

        """
        if self.reblath_fs_costs is not None:
            return self.reblath_fs_costs.loc[:, "Cost"]
        else:
            self.reblath_fs_costs = self._recalculate_failstack_costs()
            return self.reblath_fs_costs.loc[:, "Cost"]
        