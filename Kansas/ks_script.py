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


INPUT_NAME = "KS"
OUTPUT_NAME = "KS_SCRIPTED"

#pull data from sheets, initalize dataframe, set output name
sa = gspread.service_account(filename="DemocracyWorks/servicekeys.json")
sh=sa.open("Data Entry")
wks_input = sh.worksheet(INPUT_NAME)
df=pd.DataFrame(wks_input.get_all_records())


# set important variables
election_day = pd.to_datetime("2022-11-08")
end_script_date = pd.to_datetime("2022-11-07")

# format start/end dates to datatype for offsetting calendar
df[["start_date","end_date"]] = df[["start_date","end_date"]].apply(pd.to_datetime)

# seperate the data that will  be scripted from dropbox and rows that have been marked out
#conditions
is_scriptable = df['script'] == "TRUE"
is_drop_box = df['is_drop_box'] == "TRUE"
is_not_drop_box = df['is_drop_box'] == FALSE

# create bucketeddataframes
no_script = df[~is_scriptable]
dropbox = df[is_drop_box]
df = df[is_scriptable & ~is_drop_box]



# create a batch and bucket dataframe. The batch will contain the data that is being transformed. The bucket will hold the original data and the data that has already been transformed
df_batch = df
df_bucket = df

# loops until there are no more scriptable rows (could delete this line with do...while)
num_rows_incomplete = len(df_batch[is_scriptable])





#left off with a series of numbers which I could use to transorm the dates correctly...This might take a minute.
while num_rows_incomplete > 0:
    #select the rows that need to be scripted still, if there are none, the while loop stops
    df_batch = df_batch[is_scriptable]
    num_rows_incomplete = len(df_batch[is_scriptable])



    #convert all start dates to the following Monday
    pd.to_datetime(df_batch['start_date'])
    df_batch['start_date'] = df_batch['start_date']+ Week(weekday=0)
    df_batch['end_date'] = df_batch['end_date'] + timedelta(days=7)
    print(df_batch[['Locality','start_date', 'end_date']])
    #convert all end dates to next week 


    #select all the rows that are less than the end script date, anything greater is not needed
    df_batch = df_batch[df_batch['start_date'] < end_script_date]
   

    #if the end dates are greater than or equal to early voting deadline, mark them as unscriptable so they are not duplicated the next round. During the cleanup process I adjust or delete these values depending on if the start date is past the date as well
    df_batch.loc[df_batch['end_date'] >= end_script_date, 'script'] = "FALSE"

    
    # Add work to the bucket
    frames=[df_batch, df_bucket]
    df_bucket=pd.concat(frames)

    
# cleanup the index
df_bucket.reset_index(drop=True, inplace=True)

print(df_bucket[['Locality','start_date', 'end_date']].to_string())



frames = [df_bucket, no_script]
df_bucket=pd.concat(frames)
df_bucket.reset_index(drop=True, inplace=True)



# add the extra monday, keeping it simple and handing some capabilities to manual labor to save time
# df_monday=pd.DataFrame
# def add_monday (x):
#     monday = pd.to_datetime("2022-11-07")
#     row = x.iloc[-1]
#     row[['start_date', 'end_date']] = monday
#     row['end_time'] = "12:00:00"
#     print(x)
#     x = x.append(row, ignore_index=True)
#     print(x)





# print(df_bucket)

# df_bucket.groupby('Locality').apply(add_monday)

# print(df_bucket)



# quit()
# format dates for gspread
df_bucket['start_date']=pd.to_datetime(df_bucket['start_date']).dt.date
df_bucket['end_date']=pd.to_datetime(df_bucket['end_date']).dt.date
df_bucket["end_date"] = df_bucket["end_date"].apply(lambda x: str(x))
df_bucket["start_date"] = df_bucket["start_date"].apply(lambda x: str(x))


df_bucket.drop('script', axis=1, inplace=True)






df_bucket = df_bucket.sort_values(["Locality","start_date"])





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



