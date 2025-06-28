/* Selecting customers total spent

Query 3B JOIN with GROUP BY
*/
-- AMOEBA Experiment: JOIN with GROUP BY Approach (Efficient)
-- Calculate total spending per customer using efficient JOIN and aggregation
SELECT 
    C.C_CUSTKEY,
    C.C_NAME,
    SUM(O.O_TOTALPRICE) AS TOTAL_SPENT
FROM {CUSTOMER_TABLE} C
INNER JOIN {ORDERS_TABLE} O ON C.C_CUSTKEY = O.O_CUSTKEY
GROUP BY C.C_CUSTKEY, C.C_NAME
HAVING SUM(O.O_TOTALPRICE) > 200000
ORDER BY TOTAL_SPENT DESC;

