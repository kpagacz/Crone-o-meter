"""
Usage:
    crone enhance [options] [--prob | --cost] [--fail-stacks <stacks>] [--strategy <strategy>] <gear-type> <goal-enhancement-level> <base-cost>
    crone enhance [options] --fs <fail-stack-number>

Displays the optimal

Generic options:
    -h, --help          Display this help page
    -v, --verbose       Display more of the output
    
Specific options:    
    -p, --prob          Display the probability of enhancing to <goal-enhancement-level> having <stacks> number of
                            of fail stacks instead of cost
    -f <stacks>, --fail-stacks <stacks>
                        Designate the number of starting fail stacks [default: 0]
    -c, --cost          Display the cost of enhancing from +0 using only Reblath-built failstacks
    -s, --strategy <strategy>
                        Specify the desired fail stacking strategy [default: reblath]
                            Possible values:
                                reblath         Using only +14 Reblath armor piece to failstack
    --fs <fail-stack-number>
                        Displays the cost of making a single stack given the number of failstacks
                            instead of calculating item cost.

Positional arguments:
    <gear-type>         Type of gear to enhance. Can be one of the following:
                            blue-bound-acc
                            blue-ship-part
                            gold-blue-acc
                            green-acc
                            green-armor
                            green-weapon
                            life-acc
                            life-clothes
                            silver-clothes
                            white-blue-yellow-armor
                            white-blue-yellow-weapon-life-tool
    <goal-enhancement-level>
                        Goal to which enhance. Can be one of the following:
                            [1 - 15] PRI DUO TRI TET PEN
    <base-cost>         Base cost of the item at +0

"""
import pandas as pd
from docopt import docopt

import lib.enhance.enhance
import lib.enhance.strategy

def main(**kwargs):
    verbose = kwargs["--verbose"]
    prob = kwargs["--prob"]
    cost = kwargs["--cost"]
    fail_stacks = int(kwargs["--fail-stacks"])
    strategy = kwargs["--strategy"]
    gear_type = kwargs["<gear-type>"]
    goal = kwargs["<goal-enhancement-level>"]
    base_cost = int(kwargs["<base-cost>"])
    if prob:
        # Output only chance
        enhancer = lib.enhance.enhance.Enhancer(strategy=strategy, gear_type=gear_type, 
                                                goal_level=goal, base_cost=base_cost, failstack=fail_stacks)
        if verbose:
            result = enhancer._enhancer._enhance_chance_all_failstacks(gear_type=gear_type, gear_goal_level=goal)
            pd.set_option('display.max_rows', result.shape[0] + 1)
            print(result)
        else :
            print(enhancer.enhance_chance())
        exit()

    if cost:
        # Cost output
        enhancer = lib.enhance.enhance.Enhancer(strategy=strategy, gear_type=gear_type, 
                                                goal_level=goal, base_cost=base_cost, failstack=fail_stacks)
        if verbose:
            result = enhancer._enhancer._enhance_cost_all_failstacks(gear_type=gear_type, gear_goal_level=goal)
            pd.set_option("display.max_rows", result.shape[0] + 1)
            print(result)
        else:
            print(enhancer.enhance_cost())

    if kwargs["--fs"]:
        # Output only failstack building cost
        print(lib.enhance.strategy.Reblath14().fs_cost(int(kwargs["<fail-stack-number>"])))
        exit()


