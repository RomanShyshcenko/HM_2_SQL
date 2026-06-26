create database bank;

create table  clients (
ClientID SERIAL primary key,
ClientName varchar(100),
BCAName varchar(30));

create table accounts (
AccountID SERIAL primary key,
ClientID int,
foreign key (ClientID) references clients(ClientID),
balance decimal(15,2),
currency varchar(4));

create table transactions (
TransactionID SERIAL primary key,
SenderID int,
ReceiverID int,
foreign key (SenderID) references accounts(AccountID), 
foreign key (ReceiverID) references accounts(AccountID),
money_amount decimal(15,2),
TransactionDate date);

-- ============================================================
-- 1. Non-optimized query
-- ============================================================

/*
 * This query will show us clients whose sum of received transactions is above average sum of
 * received transactions.
 */

explain analyze
select 
    c.ClientID,
    c.ClientName,
    sum(case
    	when a.currency = 'EUR' then t.money_amount*51.19
    	when a.currency = 'USD' then t.money_amount*44.9
    	else t.money_amount
    end) as TotalSumTransactions
from 
    clients c
join 
    accounts a on c.clientID = a.clientID
join
    transactions t on a.AccountID=t.ReceiverID
group by
    c.ClientID, c.ClientName
having
     sum(case
    	when a.currency = 'EUR' then t.money_amount*51.19
    	when a.currency = 'USD' then t.money_amount*44.9
    	else t.money_amount
    end)>(
    select avg(TotalSum) 
           from (
                select sum(case
    	                   when a.currency = 'EUR' then t.money_amount*51.19
    	                   when a.currency = 'USD' then t.money_amount*44.9
    	                   else t.money_amount
                           end) as TotalSum
                           from 
                                clients c
                           join 
                                accounts a on c.clientID = a.clientID
                           join
                                transactions t on a.AccountID=t.ReceiverID
                           group by
                                c.ClientID, c.ClientName
                           )as Sub
                           )
order by
    TotalSumTransactions desc


-- ============================================================
-- 2. Indexes for optimization
-- ============================================================


CREATE INDEX IF NOT EXISTS idx_accounts_clientid
    ON accounts(ClientID);

CREATE INDEX IF NOT EXISTS idx_accounts_currency
    ON accounts(currency);

CREATE INDEX IF NOT EXISTS idx_opt_transactions_receiverid
    ON transactions(ReceiverID);

-- ============================================================
-- 3. Optimized query
-- ============================================================

explain analyze
with filtered_accounts as(
select 
    c.ClientID,
    c.ClientName,
    sum(case
    	when a.currency = 'EUR' then t.money_amount*51.19
    	when a.currency = 'USD' then t.money_amount*44.9
    	else t.money_amount
    end) as TotalSumTransactions
from 
    clients c
join 
    accounts a on c.clientID = a.clientID
join
    transactions t on a.AccountID=t.ReceiverID
group by
    c.ClientID, c.ClientName)
select ClientID, ClientName, TotalSumTransactions
from filtered_accounts 
where TotalSumTransactions>(select avg(TotalSumTransactions) from filtered_accounts)
order by TotalSumTransactions desc

/*
 *The execution time was 80 ms and now 50.863 ms. And now we can see hash joins.
 */

