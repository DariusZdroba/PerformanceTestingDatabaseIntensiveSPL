/*
Selecting customers whose orders were created after a specific date.

Query 2A: Using EXISTS
*/
EXPLAIN
SELECT C.C_CUSTKEY, C.C_NAME
FROM CUSTOMER C
WHERE EXISTS (
    SELECT 1 FROM ORDERS O
    WHERE O.O_CUSTKEY = C.C_CUSTKEY AND O.O_ORDERDATE > '1996-01-01'
);
