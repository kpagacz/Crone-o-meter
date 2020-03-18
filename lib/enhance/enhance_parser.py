"""
Usage:
    crone enhance [--help, -h] [--chance] [--fail-stacks <stacks>] 

Options:
    -h, --help          Display this help page
    -c, --chance        Display the probability of enhancing 
    -f <stacks>, --fail-stacks <stacks>
                        Designate the number of starting fail stacks [default: 0]

"""
from docopt import docopt

def main(**kwargs):
    print(kwargs)

