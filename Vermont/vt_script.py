import re
from tkinter.tix import Tree
import numpy as np
import pandas as pd
from datetime import datetime as dt
import csv
import gspread
import json
import gspread_pandas



sa = gspread.service_account(filename="DemocracyWorks/servicekeys.json")
sh=sa.open("Data Entry")
wks = sh.worksheet("Test")


df=pd.DataFrame(wks.get_all_records())
#open and prep the data

# df = pd.read_csv('DemocracyWorks/csv/Data Entry - Sheet9 (1).csv', index_col=None, header=0)

df['start_date']=pd.to_datetime(df['start_date']).dt.date
df['end_date']=pd.to_datetime(df['end_date']).dt.date
df.reset_index(inplace=True)

pd.DatetimeIndex(df[['start_date','end_date']])


electionDay = pd.to_datetime("2022-11-08")
holiday = pd.to_datetime("2022-10-10")

#initalize data that will be merged with the original database after dates are copied for each week
dfCopy = pd.DataFrame(columns=["Locality ", "start_date", "end_date", 'address_line1', 'address_city', 'address_state', 'address_zip','time_zone','start_time', 'end_time'])

# print(dfCopy)


indexCopy = 0

for index, row in df.iterrows():
    name = df.loc[index, "Locality "]
    address = df.loc[index, "address_line1"]
    city = df.loc[index, "address_city"]
    state = df.loc[index, "address_state"]
    zipcode = df.loc[index, "address_zip"]
    timezone = df.loc[index, "time_zone"]
    startTime = df.loc[index, 'start_time']
    endTime = df.loc[index, 'end_time']

    newStart = df.loc[index, 'start_date'] + pd.DateOffset(days=7)
    newEnd = df.loc[index, 'end_date']+ pd.DateOffset(days=7)

    indexCopy = indexCopy + 1
    dfCopy.loc[indexCopy] = [name, newStart, newEnd, address, city, state,zipcode,timezone,startTime,endTime]

    dfCopy['start_date']=pd.to_datetime(dfCopy['start_date']).dt.date
    dfCopy['end_date']=pd.to_datetime(dfCopy['end_date']).dt.date

    if newEnd < electionDay:
        switch = True


    while switch:
        #add a week to each day
        newStart = newStart + pd.DateOffset(days=7)
        newEnd = newEnd + pd.DateOffset(days=7)
    
        # increment the index copy and add the data to the new entry
        indexCopy = indexCopy + 1
        dfCopy.loc[indexCopy] = [name, newStart, newEnd, address, city, state,zipcode,timezone,startTime,endTime]


        #stop cycle once the dates aare past the election date
        #better to have data be left in than left out!!
        if newStart > electionDay:
            switch = False
            dfCopy['start_date']=pd.to_datetime(dfCopy['start_date']).dt.date
            dfCopy['end_date']=pd.to_datetime(dfCopy['end_date']).dt.date



#check data for too many dates and adjust for holidays
for index, row in dfCopy.iterrows():
    if (row.start_date == holiday) and (row.end_date == holiday):
        dfCopy.drop(index, inplace=True)

    if (row.start_date == holiday) and (row.end_date != holiday):
        dfCopy.loc[index, 'start_date'] = row.start_date + pd.DateOffset(days=1)
    
    if (row.start_date != holiday) and (row.end_date == holiday):
        dfCopy.loc[index, 'end_date']= row.end_date - pd.DateOffset(days=1)

    if (row.start_date >= electionDay):
        dfCopy.drop(index, inplace=True)
    
    if(row.start_date < electionDay and row.end_date >= electionDay):
        dfCopy.loc[index, 'end_date']= electionDay - pd.DateOffset(days=1)


    # this instance doesn't happen because the holiday is on a monday, but useful to keep around just in case
    # if (holiday > row.start_date) and (holiday < row.end_date):
        # trickier, will have to delete rows, copy them and offset, who knows

dfCopy['start_date']=pd.to_datetime(dfCopy['start_date']).dt.date
dfCopy['end_date']=pd.to_datetime(dfCopy['end_date']).dt.date



final = pd.concat([df,dfCopy], axis=0)



print(df.columns, final)
final.columns = ['index','status', 'ocd-division', 'Locality ', 'Location Name', 'directions', 'address_line1','address_line2','address_city','address_state','address_zip','time_zone','TEMP COLUM TIME', 'start_time', 'end_time', 'start_date' , 'end_date', 'is_only_by_appointment', 'is_or_by_appointment','is_drop_box','is_early_voting', 'internal_notes']

# this sort stuff doesnt really work
final.sort_values(by=['Locality '], ascending=False)


final['start_date']=pd.to_datetime(final['start_date']).dt.date
final['end_date']=pd.to_datetime(final['end_date']).dt.date
# print(final)

#write the data to a csv file
f = open('VT_df-entry2.csv', 'w')
writer = csv.writer(f)
final=pd.DataFrame(final)


#how to write row to csv
for index, row in final.iterrows():
    # print(row)
    writer.writerow(row)

# close the file
f.close()
print("ERBIUBE")
pd.DataFrame(wks.get_all_records())



final = final.fillna('')
print(final['start_date'])
for index, row in final.iterrows():
    start_date_copy = row.start_date
    print(start_date_copy.l.apply(type))

    final.loc[index, 'start_date'] = start_date_copy.strftime('%Y-%m-%d')

    end_date_copy = row.end_date
    final.loc[index, 'end_date'] = end_date_copy.strftime('%Y-%m-%d')


wks.update([final.columns.values.tolist()] + final.values.tolist())




#okay, this is a pretty cool start. The next thing to add next week is gspread, so I can enter this infomration into a page and automatically get the information I want.