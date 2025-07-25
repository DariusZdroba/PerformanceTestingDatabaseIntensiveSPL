-- SPL-DB-Sync Experiment: Modular Approach (Efficient)
-- Clean, efficient purchase summary calculation
SELECT 
    C.C_NAME,
    SUM(O.O_TOTALPRICE) AS TOTAL_SPENT,
    COUNT(O.O_ORDERKEY) AS ORDER_COUNT,
    AVG(O.O_TOTALPRICE) AS AVG_ORDER_VALUE
FROM {CUSTOMER_TABLE} C
INNER JOIN {ORDERS_TABLE} O ON C.C_CUSTKEY = O.O_CUSTKEY
GROUP BY C.C_CUSTKEY, C.C_NAME
HAVING SUM(O.O_TOTALPRICE) > 100000
ORDER BY TOTAL_SPENT DESC
LIMIT 500;
