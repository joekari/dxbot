#TODO--------------TODO#
#----------------------#

#Add year w/ default
#Strip @channel from messages
#Don't allow reminders to be sent by PM

#----------------------#
#TODO--------------TODO#

import string, uuid
from time import strftime
remindersList = []

with open('reminders.txt') as fo:
    for line in fo:
        split = line.split("|")
        split[3] = string.replace(split[3], "\n", '').lower()
        split.insert(0, uuid.uuid1())
        remindersList.append(split)

fo.close()

def checkReminders() :
    curMonth   = int(strftime('%m'))
    curDay     = int(strftime('%d'))
    curHour    = int(strftime('%H'))
    curMinute  = int(strftime('%M'))
    foundList = []

    for reminder in remindersList :
        date = reminder[2].split('/')
        time = reminder[3].split(':')
        month = int(date[0])
        day = int(date[1])
        hour = int(time[0])
        minute = int(time[1])

        #There's an error with this in either hour or minute block
        if curMonth > month or (curMonth == month and curDay > day) or (curMonth == month and curDay == day and curHour > hour) or (curMonth == month and curDay == day and curHour == hour and curMinute >= minute) :
            foundList.append(reminder)

    if len(foundList) > 0 :
        return foundList
    else :
        return False

def addReminder(nick, date, time, message) :
    toAppend = nick + '|' + date + '|' + time + '|' + message + '\n'
    with open("reminders.txt", "a") as fo:
        fo.write(toAppend)
    fo.close()
    remindersList.append([uuid.uuid1(), nick, date, time, message])

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
