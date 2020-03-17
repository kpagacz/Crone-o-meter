import pandas as pd
import glob

file_list = glob.glob("data/*.xlsx")
data_list = [pd.read_excel(file_path) for file_path in file_list]

data_table_names = [file_name.split(".")[0].split("data\\")[1] for file_name in file_list]

for id_, table in enumerate(data_list) :
    table.to_hdf("data/enhance-tables.h5", data_table_names[id_])