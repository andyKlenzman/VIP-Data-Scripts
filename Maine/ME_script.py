from dataclasses import dataclass
from pickle import FALSE
import re
import string
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

#crazy how much this is like philosophy, deciding anchor words to use to make the code understandable, like intuition for my research paper. Really learning how to explain the decisions in the logic

#


# FEATURES
# e

# WISH LIST
# # Add a row for marking locations that are open for holidays
# # format the columns so they are aligned to the correct side
## transdorm the formatting so that you can write date and time based on what is most comfortable for you, then it conversts it to the time you want, as long as it is formatted in the correct data type
# # create a address confirmation w google api ,  
# # regex system faster for entering dates, a row for each time group,
#  # auto organize the rows and formatinting
## error handling and server based, can use it straight from google sheets and there is a page for exaplining errors
# # better system for dealing with towns that are one off...ie they dont script
## cinsead of entering true, if null just script it, make it a check box


# QUESTIONS
# # if there is a row just encompassing monday, will it continue to script it, or will columbus day delete it?
# #
# #

# CHECk
# # Did I accidently script rows marked with dropbox? They should be left alone
# #
# #

INPUT_NAME = "COPY_MN_CITIES_MAIN"
OUTPUT_NAME = "MN_CITIES_SCRIPTED"

#pull data from sheets, initalize dataframe, set output name
sa = gspread.service_account(filename="DemocracyWorks/servicekeys.json")
sh=sa.open("Data Entry")
wks_input = sh.worksheet(INPUT_NAME)

df=pd.DataFrame(wks_input.get_all_records())


# set important variables
election_day = pd.to_datetime("2022-11-08")
early_voting_deadline_ME = pd.to_datetime("2022-11-07")
columbus_day = pd.to_datetime("2022-10-10")
after_columbus_day = pd.to_datetime("2022-10-11")

# format start/end dates to datatype for offsetting calendar
df[["start_date","end_date"]] = df[["start_date","end_date"]].apply(pd.to_datetime)

# bucket data that is marked for scripting (the order is important)
# conditions
is_scriptable = df['script'] == "TRUE"
is_drop_box = df['is_drop_box'] == "TRUE"
is_not_drop_box = df['is_drop_box'] == FALSE

# dataframes
no_script = df[~is_scriptable]
dropbox = df[is_drop_box]
df = df[is_scriptable & ~is_drop_box]



# Use OG, batch, and bucket dataframes to add new dates.
# OG is caopied, batch is processed with new dates, bucket stores each new process.
df_batch = df
df_bucket = df

# loops until there are no more scriptable rows
num_rows_incomplete = len(df_batch[is_scriptable])

while num_rows_incomplete > 0:
    #filter out rows that need scripting (marked at end of each loop and in manual dataentry)
    df_batch = df_batch[is_scriptable]
    
    # if there are none left, loop stops
    num_rows_incomplete = len(df_batch[is_scriptable])

    #add 7 days to start/end date
    df_batch[['start_date', 'end_date']] = df_batch[['start_date', 'end_date']] + timedelta(days=7)


    #if start date is past the early voting deadline, drop the row from the batch.
    df_batch = df_batch[df_batch['start_date'] <= early_voting_deadline_ME]
   

    #if end_dates are greater than early voting deadline, mark them as unscriptable so they are not duplicated the next round. During the cleanup process I adjust or delete these values depending on if the start date is past the date as well
    df_batch.loc[df_batch['end_date'] > early_voting_deadline_ME, 'script'] = "FALSE"
    df_batch.loc[df_batch['end_date'] <= early_voting_deadline_ME, 'script'] = "TRUE"

    
    # Add work to the bucket
    frames=[df_batch, df_bucket]
    df_bucket=pd.concat(frames)

    
# cleanup the index
df_bucket.reset_index(drop=True, inplace=True)


# if the end date is past the early voting deadline, adjust the end date to the election date. Do not need to worry about the start date because we removed overrun start dates in the loop
df_bucket.loc[df_bucket['end_date'] > early_voting_deadline_ME, 'end_date'] = early_voting_deadline_ME


# check for columbus day, remove row or adjust dates (CHANGE SCRIPT IF DATA/HOLIDAY CHANGES, makes some weak assumptions) assumes that columbus day will always be the start date, NOT inside a range or end date
#drop row if both dates are Mondays
# rows that end w columbus day are probably just monday hours that need to be dropped for that wee
df_bucket = df_bucket.loc[df_bucket['end_date'] != columbus_day]
df_bucket.reset_index(drop=True, inplace=True)
# now that purely Columbus day rows are dropped, just move the date forward one day becauswe the only options are dates that are tuesday and beyond


# columbus day transformation
df_bucket.loc[df_bucket['start_date'] == columbus_day, ['start_date']] = columbus_day




# dropbox formatting
dropbox_end_date = pd.to_datetime("2022-11-07")
dropbox_start_date = pd.to_datetime("2022-10-11")
dropbox_cap_date = pd.to_datetime("2022-11-08")


dropbox.reset_index(drop=True, inplace=True)
# dropbox_cap_dates=dropbox
# dropbox['start_date']  = dropbox_start_date
# dropbox['end_date']  = dropbox_end_date
# dropbox_cap_dates=dropbox


# dropbox_cap_dates['start_date']=dropbox_cap_date
# dropbox_cap_dates['end_date']=dropbox_cap_date
# dropbox_cap_dates['start_time']="00:00:00"
# dropbox_cap_dates['end_time']="23:59:59"


frames=[dropbox, dropbox]
dropbox=pd.concat(frames)

frames = [dropbox, df_bucket]
df_bucket=pd.concat(frames)
df_bucket.reset_index(drop=True, inplace=True)



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
quit()


