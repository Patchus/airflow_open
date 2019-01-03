from jinja2 import FileSystemLoader, Environment
import os
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

def get_jinja_env()
    FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    env = Environment(
        loader=FileSystemLoader(FILE_DIR),
        trim_blocks=True,
        autoescape=True
    )
    return env

env = get_jinja_env()

def send_email(
    subject,
    message,
    recipients=None,
    attachments=None,
    fromaddr=None,
    html_info=None,
    config_file_path=os.environ.get('EMAIL_YAML')
):
    with open(config_file_path) as f:
        email_info = yaml.load(f.read())
    sender = email_info['from'] if not fromaddr else fromaddr
    if not recipients:
        recipients = email_info['to'].split(",")
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = '<{sender}>'.format(sender=sender)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    if attachments:
        for attach in attachments:
            ctype, encoding = mimetypes.guess_type(attach)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"
            maintype, subtype = ctype.split("/", 1)
            fp = open(attach, "rb")
            _attachment = MIMEBase(maintype, subtype)
            _attachment.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(_attachment)
            _attachment.add_header("Content-Disposition", "attachment", filename=attach.split('/')[-1])
            msg.attach(_attachment)

    if html_info:
        msg.attach(MIMEText(html_info, 'html'))

    msg.attach(MIMEText(message, 'plain'))
    server.starttls()
    server.login(email_info['from'], email_info['key'])
    text = msg.as_string()
    server.sendmail(sender, recipients, text)
    server.quit()

