import pandas as pd 

import lib.enhance.strategy
import lib.enhance._utils

# RUN ONLY FROM PACKAGE LEVEL
# This module recalculates failstack costs and appends it to enhance-tables.h5
# for quick access

if __name__ == "__main__":
    recalculated_costs = lib.enhance.strategy.Reblath14()._recalculate_failstack_costs()
    recalculated_costs.to_hdf(lib.enhance._utils.ENHANCE_TABLES_PATH, key=lib.enhance._utils.REBLATH_FAILSTACK_COSTS_TABLE_KEY)
