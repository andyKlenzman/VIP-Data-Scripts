import re


#create a shorthand that reads notes and translates the data entry into the correct format
# to simplify things, it could run before the other scripts, just to get the formatting down
#could select a start week and execute from there
input1 = 'm,w,th 9-4. t 9-6. f,s 10-2'






days = re.findall("(su|m|th|w|t|f|s)", input1)

start_time = re.findall("\d(?!-)", input1)
end_time = re.findall("\d(?=-)", input1)

test1 = re.findall("[a-z0-9](?=\.)", input1)
test2 = re.findall("[A-Z0-9._%+-](?!\.)", input1)
test3 = re.findall(".+?(?=\.)", input1)
test4 = re.findall("\.(.*)", input1)
# print(test, days, start_time, end_time)
print(test1, test2, test3, test4)
