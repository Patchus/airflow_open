select * 
from currency.currency_rates 
where pull_date::date = '{{ pull_date }}';