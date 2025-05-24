
-- Selecting customers whose orders are > 1000
/*
Query 1A: Simple Nested Select
*/
EXPLAIN
SELECT C_CUSTKEY, C_NAME
FROM CUSTOMER
WHERE C_CUSTKEY IN (
    SELECT O_CUSTKEY
    FROM ORDERS
    WHERE O_TOTALPRICE > 100000
);
