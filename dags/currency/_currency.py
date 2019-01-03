import http.client
import os
import json
from jinja2 import FileSystemLoader, Environment
from common import env
import yaml
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import smtplib

def aquire_currency_rates(**context):

    conn = http.client.HTTPConnection("data.fixer.io")
    conn.request("GET", "/api/latest?access_key={ACCESS_KEY}".format(ACCESS_KEY=os.environ.get('CURRENCY_ACCESS_KEY')))

    res = conn.getresponse()
    data = res.read().decode("utf-8")

    return data

def convert_data(**context):
    currency = context['task_instance'].xcom_pull(task_ids='pull_currency_data')
    currency = json.loads(currency)
    gbp = currency['rates']['GBP']
    usd = currency['rates']['USD']
    usd_to_gbp = round((1/gbp)/(1/usd),3)
    usd_to_chf = round((1/currency['rates']['CHF'])/(1/usd),3)
    usd_to_dkk = round((1/currency['rates']['DKK'])/(1/usd),3)
    usd_to_euro = round(usd,3)

    conversions = {"EURO":usd_to_euro,
                   "GBP" :usd_to_gbp,
                   "DKK" :usd_to_dkk,
                   "CHF": usd_to_chf}

    return conversions

def email_currency(**context):
    currency = context['task_instance'].xcom_pull(task_ids='convert_data')    
    euro = currency['EURO']
    gbp  = currency['GBP']
    chf  = currency['CHF']
    dkk  = currency['DKK']
    
    send_email(
        subject='Daily Currency {}'.format(context['ds']),
        message='',        
        html_info=get_email_body(gbp,euro,chf,dkk),
        fromaddr='dontfoimebro@gmail.com',
        config_file_path='{}/dags/currency/templates/currency.yaml'.format(os.environ.get('AIRFLOW_HOME'))
    )

def get_email_body(gdp,euro,chf,dkk):        
    template = env.get_template('currency/templates/currency.html')
    html_to_send = template.render(
        gdp=gdp,
        euro=euro,
        chf=chf,
        dkk=dkk        
    )
    return html_to_send

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

