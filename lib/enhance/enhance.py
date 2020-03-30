import pandas as pd
import numpy as np

import lib.enhance.strategy
from lib.enhance._utils import ENHANCE_TABLES_PATH
from lib.enhance._utils import GEAR_TYPE
from lib.enhance._utils import ENHANCEMENT_LEVEL
from lib.enhance._utils import BLACK_STONE_ARMOR_PRICE
from lib.enhance._utils import BLACK_GEM_PRICE
from lib.enhance._utils import CONCENT_ARMOR_PRICE
from lib.enhance._utils import CONCENT_WEAPON_PRICE
from lib.enhance._utils import BLACK_STONE_WEAPON_PRICE
from lib.enhance._utils import MEMORY_FRAGMENT_PRICE


STRATEGIES = {
    "reblath" : lib.enhance.strategy.Reblath14()
}


class ItemEnhancer(object):
    def __init__(self,
                 strategy : str) -> None:
        self._strategy = STRATEGIES[strategy]

    # Cost functions
    def enhance_cost(self, gear_type : str, gear_goal_level : str, base_cost : int, failstack : int = 0) -> float:
        raise NotImplementedError("enhance_cost needs to be implemented in child classes")

    def _enhance_cost_all_failstacks(self, gear_type : str, gear_goal_level : str, base_cost : int, failstack : int = 0) -> pd.DataFrame:
        raise NotImplementedError("enhance_cost needs to be implemented in child classes")

    def single_enhancement_cost(self, gear_type : str, gear_goal_level : str, base_cost : int,
                                current_level_cost : int, failstack : int = 0, verbose : bool = False) -> float:
        raise NotImplementedError("single_enhancement_cost needs to be implemented in child classes")

    # Probability functions
    def enhance_chance(self, gear_type : str, gear_goal_level : str, failstack : int = 0) -> float:
        """ Returns chance of enhancing item to given level.
        ItemEnhancer should not be used by a user. Enhancer is preferred instead.

        Args:
            gear_type: type of gear to enhance
            gear_goal_level: to which particular gear level is item enhanced.
                Should be one higher than the current enhancement level
            failstack: current failstack number
        
        Returns:
            Probability of enhancement to 'gear_goal_level'

        """
        gear_type = GEAR_TYPE[gear_type]
        gear_goal_level = ENHANCEMENT_LEVEL[gear_goal_level]

        enhancement_table = pd.read_hdf(ENHANCE_TABLES_PATH, gear_type)
        return enhancement_table.loc[failstack, gear_goal_level]

    def _enhance_chance_all_failstacks(self, gear_type : str, gear_goal_level : str, failstack : int = 0) -> pd.DataFrame:
        """Returns enhance chance for all possible failstacks for a given goal enhancement level

        Args:
            gear_type: type of the gear
            gear_goal_level: target enhancement level
            failstack: number of current failstacks

        Returns:
            A slice of pd.DataFrame table with enhancement chances
        """
        gear_type = GEAR_TYPE[gear_type]
        gear_goal_level = ENHANCEMENT_LEVEL[gear_goal_level]

        enhancement_table = pd.read_hdf(ENHANCE_TABLES_PATH, gear_type)

        return enhancement_table.loc[:, gear_goal_level]


class AccEnhancer(ItemEnhancer):
    def __init__(self, strategy : str) -> None:
        """Deal with enhancing chance and cost calculations of accessories
        
        Attributes:
            self._enhancement_levels: list with possible accessory enhancement levels
            self._enhancement_cost_dict: dictionary with minimum average cost required to enhance to particular level
            self._enhancement_cost_df: pandas.DataFrame with average cost of enhancing item

        """
        super(AccEnhancer, self).__init__(strategy)
        self._enhancement_levels = [0, "PRI", "DUO", "TRI", "TET", "PEN"]
        self._enhancement_cost_dict = {
            0 : 0,
            "PRI" : 0,
            "DUO" : 0,
            "TRI" : 0,
            "TET" : 0,
            "PEN" : 0,
        }
        self._enhancement_min_index_dict = {
            0 : 0,
            "PRI" : 0,
            "DUO" : 0,
            "TRI" : 0,
            "TET" : 0,
            "PEN" : 0,         
        }
        self._enhancement_cost_df = pd.DataFrame()
    
    def enhance_cost(self, gear_type : str, gear_goal_level : str, base_cost : int, failstack : int = 0) -> tuple:
        """Returns cost of self-enhancing an accessory to 'gear_goal_level' of enhancement.

        Assumes self-enhancing according to the provided strategy from the base enhancement level
        up to the enhancement level provided in 'gear_goal_level'.

        Args:
            gear_type: type of the gear
            gear_goal_level: level of enhancement desired
            base_cost: price of accessory at +0 enhancement level
            failstack: number of current failstacks [default: 0]

        Returns:
            Tuple
            [0]: number of failstacks at which enhancement is least expensive
            [1]: number of silvers needed to enhance

        """
        # Argument check
        if (gear_goal_level not in "PRI DUO TRI TET PEN".split()):
            raise ValueError("Gear goal level should be PRI | DUO | TRI | TET | PEN for accessories.")

        failstack = int(failstack)
        if (failstack < 0):
            raise ValueError("Failstack number must be non-negative.")
        
        # Base cost assignment
        self._enhancement_cost_dict[0] = base_cost

        # Calculations loop
        # Each iteration it calculates the cost of enhancing in the range of possible failstack number
        # Each iteration represents a single enhancement level
        # Each iteration it finds the lowest price, considering failstack building cost, base cost
        #   and cost of the already enhanced accessory
        
        failstack_cost = self._strategy._all_failstack_price()

        for _index, _level in enumerate(self._enhancement_levels[1:]):
            # enhancement_chance_slice contains a column of enhancement probabilities for the accessory
            enhancement_chance_slice = self._enhance_chance_all_failstacks(gear_type=gear_type, gear_goal_level=_level)

            # total cost = (failstack building cost + cost of enhancing gear to preceding level + price of base accessory
            #   needed for enchanting) / number of times needed to average one success
            total_cost = (failstack_cost + + self._enhancement_cost_dict[self._enhancement_levels[_index]]
                             + self._enhancement_cost_dict[0]) / enhancement_chance_slice
            self._enhancement_cost_df[_level] = total_cost

            # Finding out the minimal price for a _level enhancement level
            self._enhancement_cost_dict[_level] = min(total_cost)
            self._enhancement_min_index_dict[_level] = np.argmin(total_cost)

            # Early stopping - there is no need to fill the whole _enhancement_cost_dict, just up to the point
            # required by function arguments
            if(_level == gear_goal_level):
                return self._enhancement_cost_dict[_level] # TO-DO (konrad.pagacz@gmail.com) make this a tuple according to the docstring

    def _enhance_cost_all_failstacks(self, gear_type : str, gear_goal_level : str, base_cost : int, failstack : int = 0) -> pd.DataFrame:
        """Returns cost of enhancing for all failstacks number and all enhancement levels 

        Args:
            gear_type: type of gear
            gear_goal_level: target enhancement level of the equipment
            base_cost: price of the +0 item
            failstack: number of failstack

        Returns:
            pandas.DataFrame with enhancement costs. Rows contain failstack numbers and columns are enhancement levels.
            Each cell contains cost of enhancing the equipment to the next enhancement level at a given failstack number.
        """
        self.enhance_cost(gear_type=gear_type, gear_goal_level=gear_goal_level, base_cost=base_cost)
        return self._enhancement_cost_df[gear_goal_level]

    def single_enhancement_cost(self, gear_type : str, gear_goal_level : str, base_cost : int, current_level_cost : int, failstack : int = 0, verbose=False) -> float:
        """Returns cost of enhancing gear in a scenario of a single enhancement.

        Assumes the gear has a price of 'current_level_cost' and is enhanced to the 'gear_goal_level' using
        'failstack' number of failstacks.

        Returns:
            Estimated cost of enhancement.
        """
        if verbose:
            enhancement_probability = self._enhance_chance_all_failstacks(gear_type=gear_type, gear_goal_level=gear_goal_level)
        else:
            enhancement_probability = self.enhance_chance(gear_type=gear_type, gear_goal_level=gear_goal_level, failstack=failstack)

        return (current_level_cost + base_cost) / enhancement_probability


class WeaponEnhancer(ItemEnhancer):

    def __init__(self, strategy : str) -> None:
        """Deal with enhancing chance and cost calculations of accessories
        
        Attributes:
            self._enhancement_levels: list with possible accessory enhancement levels
            self._enhancement_cost_dict: dictionary with minimum average cost required to enhance to particular level
            self._enhancement_cost_df: pandas.DataFrame with average cost of enhancing item

        """
        super(WeaponEnhancer, self).__init__(strategy)  
        self._enhancement_levels = [0, 1, 2, 3, 4, 5, 6, 7, 8 , 9, 10, 11, 12, 
            13, 14, 15, "PRI", "DUO", "TRI", "TET", "PEN"]
        self._enhancement_cost_dict = {
            0 : 0,
            1 : 0,
            2 : 0,
            3 : 0,
            4 : 0,
            5 : 0,
            6 : 0,
            7 : 0,
            8 : 0,
            9 : 0,
            10 : 0,
            11 : 0,
            12 : 0,
            13 : 0,
            14 : 0,
            15 : 0,
            "PRI" : 0,
            "DUO" : 0,
            "TRI" : 0,
            "TET" : 0,
            "PEN" : 0,
        }
        self._enhancement_cost_df = pd.DataFrame()

    def enhance_cost(self, gear_type : str, gear_goal_level : str, base_cost : int, failstack : int = 0) -> tuple:
        """Returns cost of self-enhancing an accessory to 'gear_goal_level' of enhancement.

        Assumes self-enhancing according to the provided strategy from the base enhancement level
        up to the enhancement level provided in 'gear_goal_level'.

        Args:
            gear_type: type of the gear
            gear_goal_level: level of enhancement desired
            base_cost: price of weapon at +0 enhancement level
            failstack: number of current failstacks [default: 0]

        Returns:
            Tuple
            [0]: number of failstacks at which enhancement is least expensive
            [1]: number of silvers needed to enhance
        
        """      
        # Argument check
        if (gear_goal_level not in "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 PRI DUO TRI TET PEN".split()):
            raise ValueError("Gear goal level should be 1-15 | PRI | DUO | TRI | TET | PEN for weapons.")

        failstack = int(failstack)
        if (failstack < 0):
            raise ValueError("Failstack number must be non-negative.")
        
        # Base cost assignment
        self._enhancement_cost_dict[0] = base_cost

        # Flaggin for repairs using base cost or memory fragments
        # memory fragments repair durability by:
        # 10 on white weapons
        # 5 on green weapons
        # 2 on blue weapons
        # 1 on yellow weapons (boss weapons)
        memory_durability_multiplier_dict = {
            "white-weapon" : 10,
            "green-weapon" : 5,
            "blue-weapon" : 2,
            "yellow-weapon" : 1
        }
        memory_repair_multiplier = memory_durability_multiplier_dict[gear_type]

        if base_cost > 10 / memory_repair_multiplier * MEMORY_FRAGMENT_PRICE:
            use_fragments_on_repair = True
        else :
            use_fragments_on_repair = False

        # Calculations loop
        # Each iteration it calculates the cost of enhancing in the range of possible failstack number
        # Each iteration represents a single enhancement level
        # Each iteration it finds the lowest price, considering failstack building cost, base cost
        #   and cost of the already enhanced accessory
        
        failstack_cost = self._strategy._all_failstack_price()

        for _index, _level in enumerate(self._enhancement_levels[1:]):
            # enhancement_chance_slice contains a column of enhancement probabilities for the accessory
            enhancement_chance_slice = self._enhance_chance_all_failstacks(gear_type=gear_type, gear_goal_level=_level)

            # total cost = (failstack building cost + appropriate gem cost + repair cost + 
            #   cost of enhancing to current level if appropriate) / number of times needed to average one success
            total_cost = (failstack_cost + self._enhancement_cost_dict[self._enhancement_levels[_index]]
                             + self._enhancement_cost_dict[0]) / enhancement_chance_slice
            self._enhancement_cost_df[_level] = total_cost

            # Finding out the minimal price for a _level enhancement level
            self._enhancement_cost_dict[_level] = min(total_cost)

            # Early stopping - there is no need to fill the whole _enhancement_cost_dict, just up to the point
            # required by function arguments
            if(_level == gear_goal_level):
                return self._enhancement_cost_dict[_level] # TO-DO (konrad.pagacz@gmail.com) make this a tuple according to the docstring

    def _enhance_cost_all_failstacks(self, gear_type : str, gear_goal_level : str, base_cost : int, failstack : int = 0) -> pd.DataFrame:
        """Returns cost of enhancing for all failstacks number and all enhancement levels 

        Args:
            gear_type: type of gear
            gear_goal_level: target enhancement level of the equipment
            base_cost: price of the +0 item
            failstack: number of failstack

        Returns:
            pandas.DataFrame with enhancement costs. Rows contain failstack numbers and columns are enhancement levels.
            Each cell contains cost of enhancing the equipment to the next enhancement level at a given failstack number.
        """
        self.enhance_cost(gear_type=gear_type, gear_goal_level=gear_goal_level, base_cost=base_cost)
        return self._enhancement_cost_df[gear_goal_level]

    def single_enhancement_cost(self, gear_type : str, gear_goal_level : str, base_cost : int, current_level_cost : int, failstack : int = 0, verbose=False) -> float:
        """Returns cost of enhancing gear in a scenario of a single enhancement.

        Assumes the gear has a price of 'current_level_cost' and is enhanced to the 'gear_goal_level' using
        'failstack' number of failstacks.

        Returns:
            Estimated cost of enhancement.
        """
        if verbose:
            enhancement_probability = self._enhance_chance_all_failstacks(gear_type=gear_type, gear_goal_level=gear_goal_level)
        else:
            enhancement_probability = self.enhance_chance(gear_type=gear_type, gear_goal_level=gear_goal_level, failstack=failstack)

        return (current_level_cost + base_cost) / enhancement_probability


class ArmorEnhancer(ItemEnhancer):
    def __init__(self, strategy : str) -> None:
        super(ArmorEnhancer, self).__init__(strategy)

    def enhance_cost(self, gear_type : str, gear_goal_level : str, base_cost : int, failstack : int = 0) -> float:
        print(failstack)

    def _enhance_cost_all_failstacks(self, gear_type : str, gear_goal_level : str, base_cost : int, failstack : int = 0) -> pd.DataFrame:
        print(failstack)

    def single_enhancement_cost(self, gear_type : str, gear_goal_level : str, base_cost : int, current_level_cost : int, failstack : int = 0) -> float:
        print(failstack)


class Enhancer(object):
    """" Interface class interacting with ItemEnhancer class
    Usage::
        eng = Enhancer(strategy="reblath", gear_type="gold-blue-acc", goal_level="PRI", base_cost=1000, failstack=0)
        print(eng.enhance_cost())

    """
    def __init__(self, strategy : str, gear_type : str, goal_level : str, base_cost : int = None, current_level_cost : int = None, failstack : int = 0) -> None:
        self._gear_type = GEAR_TYPE[gear_type]
        self._goal_level = goal_level
        self._failstack = failstack
        self._strategy = strategy
        self._base_cost = base_cost
        self._current_level_cost = current_level_cost
        self._ENHANCERS = {
            "blue-bound-acc" : AccEnhancer,
            "gold-blue-acc" : AccEnhancer,
            "white-blue-yellow-weapon-life-tool" : WeaponEnhancer,
            "green-armor" : ArmorEnhancer,
            "white-blue-yellow-armor" : ArmorEnhancer,
            "silver-clothes" : AccEnhancer,
            "green-weapon" : WeaponEnhancer,
        }
        self._enhancer = self._ENHANCERS[self._gear_type](self._strategy)

    def enhance_chance(self) -> float: 
        """Returns probability of enhancing gear to 'goal_level'
        
        Returns probability of enhancing gear to given enhancement level assuming number of failstacks
        provided in the 'failstack' parameter.

        Returns:
            Probability of enhancement to 'goal_level'.
        """
        return self._enhancer.enhance_chance(self._gear_type, self._goal_level, self._failstack)

    def enhance_cost(self) -> float:
        """ Returns cost of enhancing gear from +0 to 'goal level'.
        Assumes using only self-enhanced gear, black stones bought at central market,
        strategy for failstack building is 'strategy' and it is assumed that it is the only
        none used in a hypothetical scenario of enhancing.
        Takes into account any possible repairs using bought gear or memory fragments depending
        on the cost of either.
        """
        return self._enhancer.enhance_cost(self._gear_type, self._goal_level, self._base_cost, self._failstack)

    def single_enhancement(self) -> float:
        """Returns cost of enhancing gear from the level lower than the goal level.

        Assumes failstacks given as 'failstack' argument. Takes repairs into account.

        Returns:
            Cost of enhancing gear.
        """
        return self._enhancer.single_enhancement_cost(self._gear_type, self._goal_level, self._base_cost,
            self._current_level_cost, self._failstack)
        
