
-- Selecting customers whose orders are > 1000

/*
Query 1B: JOIN Method
*/
EXPLAIN
SELECT DISTINCT C.C_CUSTKEY, C.C_NAME
FROM CUSTOMER C
JOIN ORDERS O ON C.C_CUSTKEY = O.O_CUSTKEY
WHERE O.O_TOTALPRICE > 100000;

