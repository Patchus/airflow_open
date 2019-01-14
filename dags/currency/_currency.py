import http.client
import os
import json
from jinja2 import FileSystemLoader, Environment
from common import env,send_email,create_update_string,create_insert_string
import yaml
import smtplib
import pandas as pd
import datetime as dt
import sqlalchemy as sa 

def aquire_currency_rates(**context):

    conn = http.client.HTTPConnection("data.fixer.io")
    conn.request("GET", "/api/latest?access_key={ACCESS_KEY}".format(ACCESS_KEY=os.environ.get('CURRENCY_ACCESS_KEY')))

    res = conn.getresponse()
    data = res.read().decode("utf-8")

    return data

def convert_data(**context):
    currency = context['task_instance'].xcom_pull(task_ids='pull_currency_data')    
    currency = json.loads(currency)
    
    usd_to_gbp = round((1/currency['rates']['GBP'])/(1/currency['rates']['USD']),3)
    usd_to_chf = round((1/currency['rates']['CHF'])/(1/currency['rates']['USD']),3)
    usd_to_dkk = round((1/currency['rates']['DKK'])/(1/currency['rates']['USD']),3)
    usd_to_euro = round(currency['rates']['USD'],3)

    conversions = {"EURO":usd_to_euro,
                   "GBP" :usd_to_gbp,
                   "DKK" :usd_to_dkk,
                   "CHF": usd_to_chf}

    pull_time = dt.datetime.strptime((dt.datetime.now() - dt.timedelta(days = 1)).strftime('%Y-%m-%d'),'%Y-%m-%d')

    currency_l = [{'pull_date' : pull_time,
                   'currency_name': 'gbp',
                   'currency_name_long': 'Great British Pound',
                   'rate_to_euro': currency['rates']['GBP'],
                   'rate_to_dollar':usd_to_gbp},
                   {'pull_date' : pull_time,
                   'currency_name': 'euro',
                   'currency_name_long': 'Euro',
                   'rate_to_euro': 1,
                   'rate_to_dollar':usd_to_euro},
                   {'pull_date' : pull_time,
                   'currency_name': 'dkk',
                   'currency_name_long': 'Danish Kronen',
                   'rate_to_euro': currency['rates']['DKK'],
                   'rate_to_dollar':usd_to_dkk},
                    {'pull_date' : pull_time,
                   'currency_name': 'chf',
                   'currency_name_long': 'Swiss Franc',
                   'rate_to_euro': currency['rates']['CHF'],
                   'rate_to_dollar':usd_to_chf}
    ]
    currency_df = pd.DataFrame(currency_l)
    return currency_df

def email_currency(**context):
    currency = context['task_instance'].xcom_pull(task_ids='convert_data')    
    euro = float(currency[currency['currency_name'] == 'euro']['rate_to_dollar'])
    gbp  = float(currency[currency['currency_name'] == 'gbp']['rate_to_dollar'])
    chf  = float(currency[currency['currency_name'] == 'chf']['rate_to_dollar'])
    dkk  = float(currency[currency['currency_name'] == 'dkk']['rate_to_dollar'])
    
    yesterday_currency = context['task_instance'].xcom_pull(task_ids='yesterday_currency')    
    gbp_y = float(yesterday_currency[yesterday_currency['currency_name'] == 'gbp']['rate_to_dollar'])
    euro_y = float(yesterday_currency[yesterday_currency['currency_name'] == 'euro']['rate_to_dollar'])
    chf_y = float(yesterday_currency[yesterday_currency['currency_name'] == 'chf']['rate_to_dollar'])
    dkk_y = float(yesterday_currency[yesterday_currency['currency_name'] == 'dkk']['rate_to_dollar'])

    gbp_d = round(((gbp_y-gbp)/gbp_y),4)
    euro_d = round(((euro_y-euro)/euro_y),4)
    chf_d = round(((chf_y-chf)/chf_y),4)
    dkk_d = round(((dkk_y-dkk)/dkk_y),4)

    send_email(
        subject='Daily Currency {}'.format(context['ds']),
        message='',        
        html_info=get_email_body(gbp,euro,chf,dkk,
                                 gbp_y,euro_y,chf_y,dkk_y,
                                 gbp_d,euro_d,chf_d,dkk_d),        
        config_file_path='{}'.format(os.environ.get('EMAIL_YAML_PERSONAL'))
    )

def get_email_body(gbp,euro,chf,dkk,gbp_y,euro_y,chf_y,dkk_y,gbp_d,euro_d,chf_d,dkk_d):        
    template = env.get_template('currency/templates/currency.html')
    html_to_send = template.render(
        gbp=gbp,
        euro=euro,
        chf=chf,
        dkk=dkk,
        gbp_y=gbp_y,
        euro_y=euro_y,
        chf_y=chf_y,
        dkk_y=dkk_y,
        gbp_d=gbp_d,
        euro_d=euro_d,
        chf_d=chf_d,
        dkk_d=dkk_d,

    )
    return html_to_send

def get_yesterdays_data(engine, **context):
    tpl = env.get_template('currency/templates/currency_yest.sql')
    pull_time = dt.datetime.strptime((context['execution_date'] - dt.timedelta(days = 2)).strftime('%Y-%m-%d'),'%Y-%m-%d')    
    yesterdays_data = pd.read_sql(tpl.render(pull_date=pull_time), engine)     
    return yesterdays_data


def upsert_yesterdays_data(engine, **context):
    currency = context['task_instance'].xcom_pull(task_ids='convert_data')
    conn = sa.create_engine(engine)
    currency.to_sql('currency_rates_temp',conn,if_exists='replace',index=False)    
    conn.execute(create_insert_string('currency_rates',currency.columns,['pull_date','currency_name']))
    conn.execute(create_update_string('currency_rates',currency.columns,['pull_date','currency_name']))
