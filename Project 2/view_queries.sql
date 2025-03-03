CREATE VIEW StockDays AS
                SELECT Distinct Stock.tDate
                FROM Stock;


-- Qa
CREATE VIEW VarInv AS
SELECT Investor.Name
            FROM Buying, Company, Investor, Stock,
             (
                SELECT Buying.ID, Buying.tDate
                FROM Buying
                JOIN Company ON Buying.Symbol = Company.Symbol
                GROUP BY Buying.ID, Buying.tDate
                HAVING COUNT(DISTINCT Company.Sector) >= 6
            ) AS DiverseInvestors
            WHERE Buying.Symbol = Company.Symbol AND Buying.ID = Investor.ID
            AND Buying.Symbol = Stock.Symbol AND Buying.tDate = Stock.tDate
            AND Buying.ID = DiverseInvestors.ID AND Buying.tDate = DiverseInvestors.tDate
            GROUP BY Investor.ID, Investor.Name;


-- Query B
CREATE VIEW EachDayInvBuy AS
SELECT Company.Symbol
FROM Buying B, Company
WHERE B.Symbol = Company.Symbol
GROUP BY Company.Symbol, Company.Sector
HAVING COUNT(DISTINCT B.tDate) = (SELECT COUNT(Distinct Buying.tDate) FROM Buying);


CREATE VIEW PopComp AS
SELECT Company.Symbol
FROM
(SELECT Company.Sector
FROM EachDayInvBuy, Company
WHERE EachDayInvBuy.Symbol = Company.Symbol
GROUP BY Company.Sector
HAVING COUNT(*) >= 1) as Strs, Company, EachDayInvBuy
Where Company.Sector = Strs.Sector AND Company.Symbol = EachDayInvBuy.Symbol;


CREATE VIEW popQuantity AS
SELECT PopComp.Symbol, SUM(Buying.BQuantity) quantity, Buying.ID,
       RANK() OVER (PARTITION BY PopComp.Symbol ORDER BY SUM(Buying.BQuantity) DESC) InvestorRank
FROM PopComp, Buying, Investor
WHERE PopComp.Symbol = Buying.Symbol AND Buying.ID = Investor.ID
GROUP BY PopComp.Symbol, Buying.ID;

