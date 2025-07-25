-- SPL-DB-Sync Experiment: Modular Approach (Efficient)
-- Clean, efficient identification of newsletter-worthy customers
SELECT 
    C.C_NAME,
    C.C_ACCTBAL,
    COUNT(O.O_ORDERKEY) as ORDER_COUNT
FROM {CUSTOMER_TABLE} C
INNER JOIN {ORDERS_TABLE} O ON C.C_CUSTKEY = O.O_CUSTKEY
WHERE O.O_TOTALPRICE > 100000 
AND C.C_ACCTBAL > 5000
GROUP BY C.C_CUSTKEY, C.C_NAME, C.C_ACCTBAL
HAVING COUNT(O.O_ORDERKEY) >= 2
ORDER BY C.C_ACCTBAL DESC;
