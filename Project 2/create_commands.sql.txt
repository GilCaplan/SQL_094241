
CREATE TABLE Investor(
    ID          INTEGER  PRIMARY KEY,
    Name        VARCHAR(40),
    Amount      FLOAT
);


CREATE TABLE Company(
    Symbol          VARCHAR(10)  PRIMARY KEY,
    Sector          VARCHAR(40),
    Location        VARCHAR(40),
    Founded         INTEGER
);


CREATE TABLE Stock(
    Symbol          VARCHAR(10),
    tDate           DATE,
    Price           FLOAT,
    PRIMARY KEY (Symbol, tDate),
    FOREIGN KEY (Symbol) REFERENCES Company ON DELETE CASCADE
);


CREATE TABLE Buying(
    tDate           DATE,
    ID              INTEGER,
    Symbol          VARCHAR(10),
    BQuantity       INTEGER,
    PRIMARY KEY (tDate, ID,Symbol),
    FOREIGN KEY (Symbol, tDate) REFERENCES Stock ON DELETE CASCADE,
    FOREIGN KEY (ID) REFERENCES Investor ON DELETE CASCADE
);


CREATE TABLE Transactions(
    tDate           DATE,
    ID              INTEGER,
    TAmount         INTEGER,
    PRIMARY KEY (tDate, ID),
    FOREIGN KEY (ID) REFERENCES Investor ON DELETE CASCADE
);


