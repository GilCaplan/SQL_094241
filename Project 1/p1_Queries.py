QUERY_ANSWERS = {
    "Q3":
        """
         SELECT Buying.ID, COUNT(*) AS actions,
           ROUND(SUM(Buying.BQuantity * Stock.Price) ,3) as TotalSum,
               (
                SELECT TOP 1 Company.Sector
                FROM Company, Buying B
                WHERE B.ID = Buying.ID AND Company.Symbol = B.Symbol
                GROUP BY Company.Sector
                ORDER BY COUNT(*) DESC, Company.Sector
               ) AS Sector
            FROM ActiveUser, Buying, Stock
            WHERE ActiveUser.ID = Buying.ID AND Buying.Symbol = Stock.Symbol and Buying.tDate = Stock.tDate
            GROUP BY Buying.ID
            ORDER BY actions DESC;
        """,

    "Q4":
        """
            SELECT cf.ID, COUNT(*) AS Actions
            FROM CompanyFulfill cf, Company, Buying B
            WHERE B.ID = cf.ID AND B.Symbol = Company.Symbol
            AND Company.Founded < 2000 AND Company.Location = 'California'
            GROUP BY cf.ID
        """
}
