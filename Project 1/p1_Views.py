VIEWS_DICT = {
    "Q3":
        [
            """
                CREATE VIEW StockDays AS
                SELECT Distinct Stock.tDate
                FROM Stock
            """,
            """
                CREATE VIEW Investors AS
                SELECT Distinct Buying.ID
                FROM Buying
            """,
            """
                CREATE VIEW DaysInvested AS
                SELECT Investors.ID
                FROM Investors, StockDays, Buying
                WHERE Buying.ID = Investors.ID AND StockDays.tDate = Buying.tDate
                GROUP BY Investors.ID, StockDays.tDate
                HAVING COUNT(DISTINCT Buying.Symbol) > 1;
            """,
            """
                CREATE VIEW ActiveUser AS
                SELECT DaysInvested.ID
                FROM DaysInvested
                GROUP BY DaysInvested.ID
                HAVING COUNT(DaysInvested.ID) = (SELECT COUNT(*) FROM StockDays);
            """,
            """
                CREATE VIEW AUserPerCompany AS
                SELECT ActiveUser.ID, Symbol, SUM(Buying.BQuantity) AS quantity
                FROM ActiveUser, Buying
                WHERE ActiveUser.ID = Buying.ID
                GROUP BY Buying.Symbol, ActiveUser.ID
            """
        ]
    ,
    "Q4":
        [
            """
                CREATE VIEW SingleStockPurchase AS
                SELECT Symbol
                FROM Buying
                GROUP BY Symbol
                HAVING COUNT(Symbol) = 1;
            """,
            """
            CREATE VIEW StockDays2 AS
            SELECT Distinct Stock.tDate
            FROM Stock
            """,
            """
            CREATE VIEW CompanyFulfill AS
            SELECT B.ID
            FROM Buying B, SingleStockPurchase S, Stock st
            WHERE B.Symbol = S.Symbol
              AND st.Symbol = S.Symbol
              AND st.tDate = B.tDate
              AND st.Price * 1.02 < (
                  SELECT st2.Price
                  FROM Stock st2
                  WHERE st2.Symbol = st.Symbol
                    AND st2.tDate = (
                        SELECT MIN(tDate)
                        FROM StockDays2
                        WHERE StockDays2.tDate > st.tDate
                    )
              );
            """
        ]
}











