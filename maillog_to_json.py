import re
from sys import argv
from json import dumps, dump
import copy
'''filename, out_filename  = argv'''
#filename = "D:\GitProjects\maillog_to_json\maillog.0"
filename = 'C:\Users\linikova\Desktop\maillog.txt'
out_filename = 'C:\Users\linikova\Desktop\maillog_parsed.txt'



class Message(object):
    client = ""
    sender = ""

    def __init__(self, id):
        self.id = id
        self.recipient = list()

    def addRecipient(self, rcpt):
        self.recipient.append(rcpt)

    def get_rejected(self):
        m = REProper(self.sender)
        if m.match(r"(.*?@(?!kontur.ru|buhonline.ru|kontur-extern.ru|e-kontur.ru).*$)"):
            return True
        else:
            return False


class REProper(object):

    def __init__(self, matchstring):
        self.matchstring = matchstring

    def match(self, regexp):
        self.rematch = re.search(regexp, self.matchstring)
        return bool(self.rematch)

    def group(self, i):
        return self.rematch.group()


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
    if (bool(elem[5])):
        if (bool(re.match(r"([a-zA-Z0-9:]{1,})", elem[5]))):
            e_id = elem[5].strip(':')
            m = REProper(line)
            email = copy.copy(Message(e_id))
            if m.match(r": client=(.*).*"):
                email.client = m.group(1)
                return email

            elif m.match(r": from=<(.*?)>"):
                email.sender = m.group(1)
                return email

            elif m.match(r": to=<(.*?)>"):
                email.addRecipient(m.group(1))
                return email

    return None


def result_to_file(out_filename, rejectedarray):
    with open(out_filename, 'w') as outfile:
        outfile.write("[\n")
    for mail in notlast(rejectedarray.values()):
        # mail.recipient = dumps(mail.recipient, default=set_default)
        mail.recipient = dumps(mail.recipient, default=set_default)
        mail = dumps(mail, default=lambda o: o.__dict__)
        with open(out_filename, 'a') as outfile:
            dump(mail, outfile)
            outfile.write(",\n")
    # process last element with no delimiter
    mail = rejectedarray.values()[-1]
    mail.recipient = dumps(mail.recipient, default=set_default)
    mail = dumps(mail, default=lambda o: o.__dict__)
    with open(out_filename, 'a') as outfile:
        dump(mail, outfile)
    with open(out_filename, 'a') as outfile:
        outfile.write("\n]")





emailarray = dict()
with open(filename, mode='r') as f:
    for line in f:
        msg = lineparse(line)
        if bool(msg):
            if msg.id in emailarray:
                if bool(msg.client):
                    emailarray[msg.id].client = msg.client
                elif bool(msg.sender):
                    emailarray[msg.id].sender = msg.sender
                elif bool(msg.recipient):
                    if not msg.recipient in emailarray[msg.id].recipient:
                        emailarray[msg.id].addRecipient(msg.recipient)
            else:
                emailarray[msg.id] = msg
# parse rejected
rejectedarray = dict()
for message_id in emailarray.keys():
    if (emailarray[message_id]).get_rejected():
        rejectedarray[message_id] = emailarray[message_id]


# results to file
if(bool(rejectedarray)):
    result_to_file(out_filename, rejectedarray)
