import pandas as pd 
import numpy as np
import random
import tqdm

from lib.enhance import _utils

# RUN ONLY FROM PACKAGE LEVEL
# This module simulates enhancing process to determine mean clicks to enhance to next level

def simulate_enhancement(probability_df : pd.DataFrame, row : int, column : int) -> float:
    mean_clicks_to_enhance = 0
    # set failstack increase
    # print("Row {} Column {}".format(row, column))
    # print("Shape of probability df {}".format(probability_df.shape))
    if probability_df.shape[1] < 15:
        failstack_increase = 1
    else:
        failstack_increase = np.max([1, column - 14])
    
    clicks_to_enhance_array = []

    # print("failstack increase: {}".format(failstack_increase))
    # print("Start probability: {}".format(probability_df.iloc[row, column]))

    for _repetition in range(NUMBER_OF_REPETITIONS):
        # print("Start new simulation")
        _simulation_row = row
        clicks_to_enhance = 0
        succesfully_enhanced = False
        while (succesfully_enhanced == False):
            # print("Simulation row: {}".format(_simulation_row))
            random_number = random.uniform(0, 1)
            if (random_number <= probability_df.iloc[_simulation_row, column]):
                succesfully_enhanced = True
                clicks_to_enhance = clicks_to_enhance + 1
                clicks_to_enhance_array.append(clicks_to_enhance)
                # print("Success. Clicks to enhance: {}. Simulation row still: {}".format(clicks_to_enhance, _simulation_row))
            else:
                clicks_to_enhance = clicks_to_enhance + 1
                _simulation_row = np.min([failstack_increase + _simulation_row, probability_df.shape[0] - 1])
                # print("Failure. Clicks to enhance: {}. New simulation row: {}".format(clicks_to_enhance, _simulation_row))

    mean_clicks_to_enhance = np.mean(clicks_to_enhance_array)
    # print("Mean clicks to enhance: {}".format(mean_clicks_to_enhance))
    return mean_clicks_to_enhance

def calculate_one_table(probability_table : pd.DataFrame) -> pd.DataFrame:
    """Calculates mean number of clicks to enhance to next level
    It works on a pd.DataFrame containing probabilities of enhancement
    depending on the enhancement level (columns) and failstack number (verses).

    Args:
        probability_table: contains probabilities of enhancing given
            enhancement level (columns) and failstack number (verses)

    Returns:
        pd.DataFrame containing mean number of clicks in each cell.
        Size of the return dataframe is the same as the input dataframe.
    
    """
    ret = pd.DataFrame(index=probability_table.index, columns=probability_table.columns)
    ret["FS"] = probability_table["FS"]

    rows_no = ret.shape[0]
    columns_no = ret.shape[1]

    for _i in tqdm.trange(rows_no):
        for _j in range(1, columns_no):
            ret.at[ret.index[_i], ret.columns[_j]] = simulate_enhancement(probability_df=probability_table, row=_i, column=_j)
    
    return ret

def main():
    random.seed()
    # List of table names in the enhance-tables file.
    # Each table contains probabilities of enhancing
    probability_tables_names = [
    "gold-blue-acc",
    "blue-bound-acc",
    "white-blue-yellow-weapon-life-tool",
    "green-armor",
    "white-blue-yellow-armor",
    "silver-clothes",
    "green-weapon",
    ]
    # This list contains dataframes of probability enhancement tables
    # Each element is pd.DataFrame
    probability_tables_list = [pd.read_hdf(_utils.ENHANCE_TABLES_PATH, table_name) for table_name in probability_tables_names]

    mean_clicks_tables_list = []


    for _table in tqdm.tqdm(probability_tables_list):
        mean_clicks_df = calculate_one_table(_table)
        mean_clicks_tables_list.append(mean_clicks_df)

    mean_clicks_dict = {name : table for name, table in zip(probability_tables_names, mean_clicks_tables_list)}
    for key in mean_clicks_dict:
        mean_clicks_dict[key].to_hdf(_utils.MEAN_CLICKS_TABLES_PATH, key)

if __name__ == "__main__":
    NUMBER_OF_REPETITIONS = 1000
    main()