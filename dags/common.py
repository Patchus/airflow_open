from jinja2 import FileSystemLoader, Environment
import os
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import yaml
import smtplib

def get_jinja_env():
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

def create_update_string(table,variables,keys):
    update_q = """update {table} set {variables} from {update_table} b where {keys};"""
    var_set,key_set = "",""
    
    for col in variables:
        var_set += '{column} = b.{column}, '.format(column=col)    
    for k in keys:
        key_set += '{table}.{key}=b.{key} and '.format(table=table,key=k)
    
    update_q_filled = update_q.format(table=table,
                                  variables=var_set[0:len(var_set)-2],
                                  update_table='{}_temp'.format(table),
                                  keys=key_set[0:len(key_set)-4])
    return update_q_filled

def create_insert_string(table,variables,keys):
    insert_q = """INSERT INTO {table} ({variables})
                        SELECT b.*
                        FROM {table}_temp b
                        left outer join
                        {table} a
                        on {keys}
                        WHERE {pk} is null;"""
        
    var_set = ','.join(variables)
    key_set = ""
    for k in keys:
        key_set += 'a.{key}=b.{key} and '.format(key=k)
    
    insert_q_filled = insert_q.format(table=table,
                                     variables=var_set,
                                     keys=key_set[0:len(key_set)-4],
                                     pk='a.{}'.format(keys[0]))
    return insert_q_filled