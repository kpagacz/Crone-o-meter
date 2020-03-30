"""
Usage:
    crone enhance [options] [--prob | --cost] [--strategy <strategy>] <gear-type> <goal-enhancement-level> [<base-cost>] [<current-level-cost>]
    crone enhance [--strategy <strategy>] --stack-cost <fail-stack-number>

Displays the optimal # TO-DO (konrad.pagacz@gmail.com) finish this docstring

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
    -i, --stack-cost <fail-stack-number>
                        Displays the cost of making a single stack given the number of failstacks
                            instead of calculating item cost.

Positional arguments:
    <gear-type>         Type of gear to enhance. Can be one of the following:
                            blue-acc
                            bound-acc
                            blue-ship-part
                            gold-acc
                            blue-acc
                            green-acc
                            green-armor
                            green-weapon
                            life-acc
                            life-clothes
                            silver-clothes
                            white-armor
                            blue-armor
                            yellow-amor
                            white-weapon
                            blue-weapon
                            yellow-weapon
                            life-tool
    <goal-enhancement-level>
                        Goal to which enhance. Can be one of the following:
                            [1 - 15] PRI DUO TRI TET PEN
    <base-cost>         Base cost of the item at +0
    <current-level-cost>
                        Cost of the gear on the current level of enhancement - needs to be one lower
                            than the goal level

"""
import pandas as pd
from docopt import docopt

import lib.enhance.enhance
import lib.enhance.strategy

def main(**kwargs):
    # Variables assignment
    verbose = kwargs["--verbose"]
    prob = kwargs["--prob"]
    cost = kwargs["--cost"]
    if kwargs["--fail-stacks"] is not None:
        fail_stacks = int(kwargs["--fail-stacks"])
    strategy = kwargs["--strategy"]
    gear_type = kwargs["<gear-type>"]
    goal = kwargs["<goal-enhancement-level>"]
    if kwargs["<base-cost>"] is not None:
        base_cost = int(kwargs["<base-cost>"])
    if kwargs["<current-level-cost>"] is not None:
        current_level_cost = int(kwargs["<current-level-cost>"])

    # Probability pipeline
    if prob:
        # Probability output
        enhancer = lib.enhance.enhance.Enhancer(strategy=strategy, gear_type=gear_type, 
                                                goal_level=goal)
        if verbose:
            result = enhancer._enhancer._enhance_chance_all_failstacks(gear_type=gear_type, gear_goal_level=goal)
            pd.set_option('display.max_rows', result.shape[0] + 1)
            print(result)
        else :
            print(enhancer.enhance_chance())
        exit()

    # Cost pipeline
    if cost:
        # Single enhancement case
        if kwargs["<current-level-cost>"] is not None:
            enhancer = lib.enhance.enhance.Enhancer(strategy=strategy, gear_type=gear_type, 
                goal_level=goal, base_cost=base_cost, current_level_cost=current_level_cost, failstack=fail_stacks)

            if verbose:
                result = (enhancer._enhancer.single_enhancement_cost(gear_type=gear_type, gear_goal_level=goal,
                    base_cost=base_cost, current_level_cost=current_level_cost, verbose=verbose))
                pd.set_option("display.max_rows", result.shape[0] + 1)
                print(result)
            else:
                print(enhancer.single_enhancement())
            exit()
        
        # Cost tables
        enhancer = lib.enhance.enhance.Enhancer(strategy=strategy, gear_type=gear_type, 
                                                goal_level=goal, base_cost=base_cost, failstack=fail_stacks)
        if verbose:
            result = enhancer._enhancer._enhance_cost_all_failstacks(gear_type=gear_type, gear_goal_level=goal, base_cost=base_cost)
            pd.set_option("display.max_rows", result.shape[0] + 1)
            print(result)
        else:
            print(enhancer.enhance_cost()) 
        exit()

    # Cost of buidling failstacks pipeline
    if kwargs["--stack-cost"]:
        # Output only failstack building cost
        print(lib.enhance.strategy.Reblath14().fs_cost(int(kwargs["--stack-cost"])))
        exit()


