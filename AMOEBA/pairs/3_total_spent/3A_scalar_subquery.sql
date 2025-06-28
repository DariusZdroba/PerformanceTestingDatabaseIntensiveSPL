/* Selecting customers total spent

Query 3A: Scalar subquery
*/
-- AMOEBA Experiment: Scalar Subquery Approach (Inefficient)
-- Calculate total spending per customer using correlated subqueries
SELECT 
    C_CUSTKEY,
    C_NAME,
    (SELECT SUM(O_TOTALPRICE) 
     FROM {ORDERS_TABLE} 
     WHERE O_CUSTKEY = C_CUSTKEY) AS TOTAL_SPENT
FROM {CUSTOMER_TABLE}
WHERE (SELECT SUM(O_TOTALPRICE) 
       FROM {ORDERS_TABLE} 
       WHERE O_CUSTKEY = C_CUSTKEY) > 200000
ORDER BY TOTAL_SPENT DESC;
