import win32com.client as win32 # pip install pywin32
from datetime import datetime
import db
import os


def SendEmail(row):
    mail = win32.Dispatch('outlook.application').CreateItem(0)
    mail.To = row.email
    mail.Subject = 'Verified Vendor Capability Statement'
    attachment = mail.Attachments.Add(r"") # file path to whatever attachement to be sent on the email is required.
    attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "MyId1")
    mail.HTMLBody = "<html><body><p style='font-family:sans-serif;font-size:14pt;'> REDACTED</p>" \
                    "</body></html>" # create and paste a html formated message here for the email body.
    mail.Send()
    db.update_contract(row) # updates the contract if an email was sent using bool values(0 or 1).


def StartEmails():
    '''
        Start sending emails by checking each row in the contractsDB.
    '''
    reader = db.get_contracts()
    for row in reader:
        if row.sent == 1: 
            # if row value sent = 1, check the time it was sent, if it is in the past, send a new email using that row.
            try:
                if datetime.strptime(row.lastDateSent, "%Y-%m-%d") < datetime.today():
                    print("Over Due. Sent = 1")
                    SendEmail(row)
                    # if lastDateSent is not in the past, than email was sent and it isn't over due.
                else:
                    print("Email already sent, not overdue.")
                    pass

            except ValueError:
                print("change date")
        else: # send email if row.sent == 0
            print("Haven't Sent anything, sending now.")
            SendEmail(row)
    reader.clear()
    os.system('cls')
