import re
import pickle
from sys import argv
from collections import defaultdict
from json import dumps, dump, loads, JSONEncoder, JSONDecoder

'''filename = argv'''
filename = "C:\Users\linikova\Desktop\maillog.txt"


class Message(object):
    id = ""
    client = ""
    sender = ""
    recipient = set()

    def __init__(self, id):
        self.id = id


class REProper(object):
    def __init__(self, matchstring):
        self.matchstring = matchstring

    def match(self, regexp):
        self.rematch = re.search(regexp, self.matchstring)
        return bool(self.rematch)

    def group(self, i):
        return self.rematch.group(i)


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

def notlast(itr):
    itr = iter(itr)  # ensure we have an iterator
    prev = itr.next()
    for item in itr:
        yield prev
        prev = item

def lineparse(line):
    elem = line.split(' ', 6)

    if (bool(re.match(r"([a-zA-Z0-9:]{1,})", elem[5]))):
        e_id = elem[5].strip(':')
        m = REProper(line)
        email = Message(e_id)
        if m.match(r".*client=(.*).*"):
            email.client = m.group(1)
            return email

        elif m.match(r"from=<(.*?)>"):
            email.sender = m.group(1)
            return email

        elif m.match(r"to=<(.*?)>"):
            email.recipient.add(m.group(1))
            return email

    return None


emailarray = defaultdict(Message)
with open(filename, mode='r') as f:
    for line in f:
        message = lineparse(line)
        if bool(message):
            if message.id in emailarray:
                current = emailarray[message.id]
                if bool(message.client):
                    current.client = message.client
                elif bool(message.sender):
                    current.sender = message.sender
                elif bool(message.recipient):
                    current.recipient.union(message.recipient)
            else:
                emailarray[message.id] = message
out_filename = 'C:\maillog_parsed.txt'
with open(out_filename, 'w') as outfile:
    outfile.write("[\n")
for mail in notlast(emailarray.values()):
    # mail.recipient = dumps(mail.recipient, default=set_default)
    mail.recipient = dumps(mail.recipient, default=set_default)
    mail = dumps(mail, default=lambda o: o.__dict__)
    with open(out_filename, 'a') as outfile:
        dump(mail, outfile)
        outfile.write(",\n")
#process last element with no delimiter
mail = emailarray.values()[-1]
mail.recipient = dumps(mail.recipient, default=set_default)
mail = dumps(mail, default=lambda o: o.__dict__)
with open(out_filename, 'a') as outfile:
    dump(mail, outfile)
with open(out_filename, 'a') as outfile:
    outfile.write("\n]")