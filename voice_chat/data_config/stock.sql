-- this table contains information about stock sectors
-- use this table if you want information about specific stocks sectors
-- you can use symbol column to filter / join with stock_history table by symbol column
create table airbnb.stock
(
    symbol     text COMMENT 'symbol of stock',
    title      text COMMENT 'description of stock',
    sector     text COMMENT 'sector of the stock',
);