from dataclasses import dataclass
from pickle import FALSE
import re
import string
from tkinter import X
from tkinter.tix import Tree
import numpy as np
import pandas as pd
from datetime import datetime as dt
from datetime import date
from datetime import timedelta
import csv
import gspread
import json
import gspread_pandas
from gspread_formatting import *
from gspread_formatting.dataframe import format_with_dataframe, BasicFormatter
from gspread_formatting import Color
from pandas.tseries.offsets import *


INPUT_NAME = "KS_SCRIPTED"
OUTPUT_NAME = "KS_DB"

#pull data from sheets, initalize dataframe, set output name
sa = gspread.service_account(filename="DemocracyWorks/servicekeys.json")
sh=sa.open("Data Entry")
wks_input = sh.worksheet(INPUT_NAME)
df=pd.DataFrame(wks_input.get_all_records())


# format start/end dates to datatype for offsetting calendar
df[["start_date","end_date"]] = df[["start_date","end_date"]].apply(pd.to_datetime)

# seperate the data that will  be scripted from dropbox and rows that have been marked out
#conditions
is_db = df['db'] == "y"


# create bucketed dataframes
df = df[is_db]
df.reset_index(drop=True, inplace=True)
df_one = df.groupby('Locality').first()
df_two = df_one.copy()


#set the first row to the correct time and dates 
df_one[['end_time','start_time', 'end_date', 'is_early_voting', "is_drop_box"]] = ['00:00:00', '23:59:59', '2022-11-07', 'FALSE', "TRUE"]


print(df_one[['end_time','start_time', 'end_date', 'is_early_voting', "is_drop_box"]])
#now the second row
df_two[['end_time','start_time', 'start_date' ,'end_date', 'is_early_voting', "is_drop_box"]] = ['00:00:00', '20:00:00', '2022-11-08', '2022-11-08', 'FALSE', "TRUE"]

print(df_one[['end_time','start_time', 'end_date', 'is_early_voting', "is_drop_box"]])
print(df_two[['end_time','start_time', 'start_date' ,'end_date', 'is_early_voting', "is_drop_box"]])




frames=[df_one, df_two]
df_bucket=pd.concat(frames)
df_bucket.reset_index(drop=True, inplace=True)


df_bucket['start_date']=pd.to_datetime(df_bucket['start_date']).dt.date
df_bucket['end_date']=pd.to_datetime(df_bucket['end_date']).dt.date
df_bucket["end_date"] = df_bucket["end_date"].apply(lambda x: str(x))
df_bucket["start_date"] = df_bucket["start_date"].apply(lambda x: str(x))







df_bucket.drop(columns=['db'])

df_bucket = df_bucket.sort_values("location_name")


# Generate and format new worksheet
wks_output = sh.add_worksheet(title=OUTPUT_NAME, rows="1000", cols="30")
set_frozen(wks_output, rows=1)
fmt = CellFormat(
    textFormat=TextFormat(bold=False, foregroundColor=Color(1, 0, 0)),
    )

set_column_width(wks_output, 'A', 100)
set_column_width(wks_output, 'B', 300)
set_column_width(wks_output, 'C', 150)
set_column_width(wks_output, 'D', 225)
set_column_width(wks_output, 'F', 250)


format_with_dataframe(wks_output, df_bucket, include_index=True, include_column_header=True)
format_cell_range(wks_output, 'A2:A', fmt)


wks_output.update([df_bucket.columns.values.tolist()] + df_bucket.values.tolist())

print("COMPLETE :)")



