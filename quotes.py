import string
quotesList = []
userQuotes = []
with open('quotes.txt') as fo:
    for line in fo:
        split = line.split("|")
        split[1] = string.replace(split[1], "\n", '').lower()
        quotesList.append([split[0].lower(), split[1]])

        if len(userQuotes) == 0:
            userQuotes.append([split[0], [split[1]]])
        else:
            flag = True
            for index in range(0,len(userQuotes)):
                if split[0].lower() == userQuotes[index][0].lower():
                    userQuotes[index][1].append(split[1])
                    flag = False
            if flag:
                userQuotes.append([split[0].lower(), [split[1]]])
fo.close()

def addQuote(name, quote):
    name = name.lower()
    quote = ' '.join(quote).lstrip()
    toAppend = (name + "|" + quote + "\n")
    with open("quotes.txt", "a") as fo:
        fo.write(toAppend)
    fo.close()
    quotesList.append([name.lower(), quote])
    flag = True
    for index in range(0,len(userQuotes)):
        if name == userQuotes[index][0].lower():
            userQuotes[index][1].append(quote)
            flag = False
    if flag:
        userQuotes.append([name.lower(), [quote]])