# CMFCore imports
from Products.CMFCore.utils import getToolByName

# email imports
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart

# TODO: Move this to a local utility
def getObjectByUID(context, uid):
    """
    """
    catalog = getToolByName(context, "portal_catalog")
    brains = catalog.searchResults(
        uid = uid
    )
    
    try:
        return brains[0]
    except IndexError:
        return None
        
def sendMultipartMail(context, sender, receiver, cc=[], bcc=[], subject="", text="", charset="utf-8"):
    """
    """
    mail = MIMEMultipart("alternative")
        
    mail['From']    = sender
    mail['To']      = receiver
    mail['Bcc']     = ", ".join(cc)
    mail['Bcc']     = ", ".join(bcc)
    mail['Subject'] = subject
    mail.epilogue   = ''

    # create & attach text part 
    text = text.encode("utf-8")
    text_part = MIMEText(text, "plain", charset)
    mail.attach(text_part)

    # create & attach html part with images            
    html_part = MIMEMultipart("related")
    html_code = MIMEText(text, "html", charset)            
    html_part.attach(html_code)       
    mail.attach(html_part)

    context.MailHost.send(mail.as_string())
    # except:
    #     # catch and do nothing, so that the user doesn't notice an error
    #     pass
        
