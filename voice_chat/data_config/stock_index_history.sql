-- this table contains price history of stock market indexes.
-- use this table if you want information about the market in general, rather than individual stocks
create table airbnb.stock_index_history
(
    index_name  text COMMENT 'index name - such as S&P500',
    close       numeric COMMENT 'close price of trading day date',
    date        date COMMENT 'trading day date'
);