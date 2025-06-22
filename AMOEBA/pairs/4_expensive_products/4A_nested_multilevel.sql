
/*
Customers that placed orders that included at least one product priced > 5000

Query 4A: Nested subqueries
*/
SELECT C.C_CUSTKEY, C.C_NAME
FROM CUSTOMER C
WHERE C.C_CUSTKEY IN (
    SELECT O.O_CUSTKEY
    FROM ORDERS O
    WHERE O.O_ORDERKEY IN (
        SELECT L.L_ORDERKEY
        FROM LINEITEM L
        JOIN PART P ON L.L_PARTKEY = P.P_PARTKEY
        WHERE P.P_RETAILPRICE > 500
    )
);
