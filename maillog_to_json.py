import re
import glob
from sys import argv
from json import dumps, dump
import copy
'''filename, out_filename, out_type  = argv'''
'''report or json'''
out_type = 'report'

filename = 'D:\\maillog\\*'
out_dir = 'D:\\maillog'


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
    elem = line.split(' ', 7)
    if (bool(elem[5])):
        if (bool(re.match(r"[a-zA-Z0-9]{1,}:", elem[5]))):
            e_id = elem[5].strip(':')
            m = REProper(line)
            email = copy.copy(Message(e_id))
            if m.match(r": client=(.*)"):
                email.client = m.group(1)
                return email

            elif m.match(r": from=<(.*?)>"):
                email.sender = m.group(1)
                return email

            elif m.match(r": to=<(.*?)>"):
                email.addRecipient(m.group(1))
                return email

    return None


def result_to_json(out_dir, rejectedarray):
    out_filename = out_dir + '\\other.log'
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


def result_to_report(out_dir, rejectedarray):
    for mail in rejectedarray.values():
        n = REProper(mail.client)
        if n.match(r".*?keweb.*"):
            out_filename = out_dir + '\\keweb.log'
        elif n.match(r".*?billy.*"):
            out_filename = out_dir + '\\billy.log'
        elif n.match(r".*?normativ.*"):
            out_filename = out_dir + '\\normativ.log'
        elif n.match(r".*?referent.*"):
            out_filename = out_dir + '\\referent.log'
        elif n.match(r".*?help.*"):
            out_filename = out_dir + '\\help.log'
        elif (bool(re.match(r".*?(adaptec|blinovu|StorView|ipmi).*", mail.sender))):
            out_filename = out_dir + '\\sps.log'
        elif n.match(".*?sites.*"):
            out_filename = out_dir + '\\websites.log'
        else:
            out_filename = out_dir + '\\other.log'
        with open(out_filename, 'a') as outfile:
            outfile.write("ID: %s \n" % str(mail.id))
            outfile.write("CLIENT: %s \n" % str(mail.client))
            outfile.write("SENDER: %s \n" % str(mail.sender))
            outfile.write("RECIPIENT: ")
            outfile.write(', '.join([str(item) for item in mail.recipient]))
            outfile.write("\n\n")


emailarray = dict()
listing = glob.glob(filename)
for file_log in listing:
    with open(file_log, mode='r') as f:
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
if bool(rejectedarray):
    if str(out_type) is 'report':
        result_to_report(out_dir, rejectedarray)
    elif str(out_type) is 'json':
        result_to_json(out_dir, rejectedarray)
