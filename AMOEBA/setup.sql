/*
LOAD DATA:
TPCH DB Generation was used to generate 2048MB of mock data, refer to https://github.com/electrum/tpch-dbgen for
similar generated data.
*/


/* Allow loading from files*/
SET GLOBAL local_infile = 1;

/* Load Sample Data, replace path with path to mock data generated using tpch-dbgen */
LOAD DATA LOCAL INFILE '/code_testing/tpch-dbgen/customer.tbl'
INTO TABLE customer
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n';

LOAD DATA LOCAL INFILE '/code_testing/tpch-dbgen/orders.tbl'
INTO TABLE orders
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n';

LOAD DATA LOCAL INFILE '/code_testing/tpch-dbgen/part.tbl'
INTO TABLE part
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n';

LOAD DATA LOCAL INFILE '/code_testing/tpch-dbgen/lineitem.tbl'
INTO TABLE lineitem
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n';



/*
     CREATE INDEXES:
*/

CREATE INDEX idx_orders_custkey ON ORDERS(O_CUSTKEY);
CREATE INDEX idx_orders_orderkey ON ORDERS(O_ORDERKEY);

CREATE INDEX idx_lineitem_orderkey ON LINEITEM(L_ORDERKEY);
CREATE INDEX idx_lineitem_partkey ON LINEITEM(L_PARTKEY);

CREATE INDEX idx_part_partkey ON PART(P_PARTKEY);
CREATE INDEX idx_part_price ON PART(P_RETAILPRICE);
