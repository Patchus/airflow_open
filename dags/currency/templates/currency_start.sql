create database currency;
create schema currency;
create table currency.currency_rates (pull_date timestamp,currency_name text, currency_name_long text,rate_to_euro numeric ,rate_to_dollar numeric);

insert into currency.currency_rates values ('2019-01-05','gbp','Great British Pound',0.90,1.273);
insert into currency.currency_rates values ('2019-01-04','gbp','Great British Pound',0.895886,1.273887);
insert into currency.currency_rates values ('2019-01-03','gbp','Great British Pound',0.902566,1.263322);
insert into currency.currency_rates values ('2019-01-02','gbp','Great British Pound',0.901539,1.259769);
insert into currency.currency_rates values ('2019-01-01','gbp','Great British Pound',0.910069,1.269644);

insert into currency.currency_rates values ('2019-01-05','euro','Euro',1,1.139421);
insert into currency.currency_rates values ('2019-01-04','euro','Euro',1,1.141258);
insert into currency.currency_rates values ('2019-01-03','euro','Euro',1,1.140231);
insert into currency.currency_rates values ('2019-01-02','euro','Euro',1,1.135730);
insert into currency.currency_rates values ('2019-01-01','euro','Euro',1,1.155463);

insert into currency.currency_rates values ('2019-01-05','dkk','Danish Kronen',7.466332,0.152608);
insert into currency.currency_rates values ('2019-01-04','dkk','Danish Kronen',7.468441,0.152811);
insert into currency.currency_rates values ('2019-01-03','dkk','Danish Kronen',7.467485,0.152693);
insert into currency.currency_rates values ('2019-01-02','dkk','Danish Kronen',7.467388,0.152092);
insert into currency.currency_rates values ('2019-01-01','dkk','Danish Kronen',7.518814,0.153676);

insert into currency.currency_rates values ('2019-01-05','chf','Swiss Franc',1.133024,1.019804);
insert into currency.currency_rates values ('2019-01-04','chf','Swiss Franc',1.125135,1.014329);
insert into currency.currency_rates values ('2019-01-03','chf','Swiss Franc',1.127162,1.011594);
insert into currency.currency_rates values ('2019-01-02','chf','Swiss Franc',1.122673,1.011630);
insert into currency.currency_rates values ('2019-01-01','chf','Swiss Franc',1.133024,1.019804);
