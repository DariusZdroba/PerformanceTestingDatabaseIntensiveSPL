
-- SPL-DB Sync
CREATE TABLE CUSTOMER_LOYALTY (
  CL_ID INT PRIMARY KEY AUTO_INCREMENT,
  C_CUSTKEY INT NOT NULL,
  POINTS INT,
  LOYALTY_LEVEL VARCHAR(10),
  FOREIGN KEY (C_CUSTKEY) REFERENCES CUSTOMER(C_CUSTKEY)
);


INSERT INTO CUSTOMER_LOYALTY (C_CUSTKEY, POINTS, LOYALTY_LEVEL)
SELECT
  C_CUSTKEY,
  FLOOR(RAND() * 1000) AS POINTS,
  CASE
    WHEN C_ACCTBAL > 10000 THEN 'Gold'
    WHEN C_ACCTBAL > 5000 THEN 'Silver'
    ELSE 'Bronze'
  END AS LOYALTY_LEVEL
FROM CUSTOMER
WHERE C_CUSTKEY % 3 = 0;



-- Newsletter Module, Inline - Flat vs Modular - Seperate table

CREATE TABLE CUSTOMER_NEWSLETTER (
  CN_ID INT AUTO_INCREMENT PRIMARY KEY,
  C_CUSTKEY INT,
  IS_SUBSCRIBED BOOLEAN,
  FOREIGN KEY (C_CUSTKEY) REFERENCES CUSTOMER(C_CUSTKEY)
);

INSERT INTO CUSTOMER_NEWSLETTER (C_CUSTKEY, IS_SUBSCRIBED)
SELECT C_CUSTKEY, TRUE
FROM CUSTOMER
WHERE MOD(C_CUSTKEY, 7) = 0;  -- roughly every 7th customer


-- Purchase Summary Module

CREATE TABLE CUSTOMER_PURCHASE_SUMMARY (
  CPS_ID INT AUTO_INCREMENT PRIMARY KEY,
  C_CUSTKEY INT,
  TOTAL_SPENT DECIMAL(15,2),
  FOREIGN KEY (C_CUSTKEY) REFERENCES CUSTOMER(C_CUSTKEY)
);

INSERT INTO CUSTOMER_PURCHASE_SUMMARY (C_CUSTKEY, TOTAL_SPENT)
SELECT O_CUSTKEY, SUM(O_TOTALPRICE)
FROM ORDERS
GROUP BY O_CUSTKEY;

ALTER TABLE CUSTOMER ADD C_NEWSLETTER BOOLEAN DEFAULT FALSE;


ALTER TABLE CUSTOMER_NEWSLETTER
ADD COLUMN EMAIL VARCHAR(255);

UPDATE CUSTOMER_NEWSLETTER
SET EMAIL = CONCAT('user', C_CUSTKEY, '@example.com');

