import datetime

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from _currency import (
    aquire_currency_rates,
    convert_data,
    email_currency
)

DAG_ARGS = {
    'owner': 'patchus',
    'depends_on_past': False,
    'start_date': datetime.datetime(2018, 12, 28),
    'email': ['a@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 5,
    'retry_delay': datetime.timedelta(minutes=1),
    'provide_context': True
}

dag = DAG('currency', schedule_interval='0 11 * * *', default_args=DAG_ARGS)

pull_task = PythonOperator(
    task_id='pull_currency_data',
    python_callable=aquire_currency_rates,
    queue='datastream',
    dag=dag
)
run_task = PythonOperator(
    task_id='convert_data',
    python_callable=convert_data,    
    queue='datastream',
    dag=dag
)
email_task = PythonOperator(
    task_id='email_currency',
    python_callable=email_currency,    
    dag=dag
)
pull_task.set_downstream(run_task)
run_task.set_downstream(email_task)
