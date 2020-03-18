class Strategy(object):
    """An abstract base class for a strategy class.
    
    """
    def __init__(self):
        pass

    def cost_of_failstack(self, enhancement_goal : int) -> float:
        raise NotImplementedError("{} needs to be overloaded"
                                  "in the child classes.".format("cost_of_failstack()"))

    
class Reblath14(Strategy):
    """Strategy class for Reblath failstack building.
    Calculations are based on the assumption that the failstack is built
    only using +14 Reblath armor piece. Each failstack is gained by enhancing
    a +14 Reblath armor piece with Black Stone (Armor).

    """
    def __init__(self):
        pass

    def cost_of_failstack(self, enhancement_goal : int) -> float:
        print(enhancement_goal)

    
