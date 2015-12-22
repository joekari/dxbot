#TODO--------------TODO#
#----------------------#

#Strip @channel from messages
#Switch to unix time from mm/dd/yy hh:mm format

#----------------------#
#TODO--------------TODO#

import string, uuid
from time import strftime
from calendar import monthrange
remindersList = []

with open('reminders.txt') as fo:
    for line in fo:
        #Uses | character to separate parts of the message
        split = line.split("|")
        #Uses UUID to differentiate between messages rather than trying to compare date, then time, then message
        split.insert(0, uuid.uuid1())
        remindersList.append(split)
fo.close()

'''Used to check if there are any reminders that need to be printed'''
def checkReminders() :
    curMonth   = int(strftime('%m'))
    curDay     = int(strftime('%d'))
    curYear    = int(strftime('%y'))
    curHour    = int(strftime('%H'))
    curMinute  = int(strftime('%M'))
    foundList = []

    #5 Hours is the GMT offset for the EST timezone (where bot is running)
    if curHour < 5:
        curHour = 24 + (curHour - 5)
        if curDay == 1 :
            if curMonth == 1 :
                curMonth = 12
            else :
                curMonth -= 1
            curDay = monthrange(int(strftime('%Y')), int(curMonth))
        else :
            curDay -= 1
    else :
        curHour -= 5

    for reminder in remindersList :
        date = reminder[2].split('/')
        time = reminder[3].split(':')
        month = int(date[0])
        day = int(date[1])
        year = int(date[2])
        hour = int(time[0])
        minute = int(time[1])

        if curYear > year or (curYear == year and curMonth > month) or (curYear == year and curMonth == month and curDay > day) or (curYear == year and curMonth == month and curDay == day and curHour > hour) or (curYear == year and curMonth == month and curDay == day and curHour == hour and curMinute >= minute) :
            foundList.append(reminder)

    if len(foundList) > 0 :
        return foundList
    else :
        return False

'''Add a reminder to the reminders.txt file and the list of reminders'''
def addReminder(nick, date, time, message) :
    toAppend = nick + '|' + date + '|' + time + '|' + message + '\n'
    with open("reminders.txt", "a") as fo:
        fo.write(toAppend)
    fo.close()
    remindersList.append([uuid.uuid1(), nick, date, time, message])

'''Remove a reminder from the list of reminders, then rewrite reminders.txt with the new list'''
def removeReminder(uuid) :
    toWrite = '';
    toDelete = []
    for i in range(0, len(remindersList)) :
        if uuid == remindersList[i][0] :
            toDelete.append(i)
        else :
            temp = '|'.join(remindersList[i][1:])
            toWrite = toWrite + temp + '\n'
    for index in toDelete :
        del remindersList[index]
    with open("reminders.txt", "w") as fo:
        fo.write(toWrite)
    fo.close()
