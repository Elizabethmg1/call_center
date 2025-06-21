-- this table contains price history of specific stocks
-- use this table if you want information about specific stocks prices
-- you can use symbol column to filter / join with stock table by symbol column
-- IMPORTANT: to get stock sector - JOIN stock table by symbol
-- IMPORTANT: to calculate the price change after a certain date or event, use the construction: AVG(CASE WHEN date [after event or date] THEN close END) - AVG(CASE WHEN date [before event or date] THEN close END)
create table airbnb.stock_history
(
    symbol text COMMENT 'symbol of stock',
    close  numeric COMMENT 'close price of trading day date',
    date   date COMMENT'trading day date'
);