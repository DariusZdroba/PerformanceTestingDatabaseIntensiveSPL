/*
Selecting customers whose orders were created after a specific date.

Query 2B: Using JOIN
*/
SELECT DISTINCT C.C_CUSTKEY, C.C_NAME
FROM CUSTOMER C
JOIN ORDERS O ON C.C_CUSTKEY = O.O_CUSTKEY
WHERE O.O_ORDERDATE > '1996-01-01';

