CREATE TABLE Investor(
    ID BIGINT CHECK(ID >= 100000000 AND ID <= 999999999) PRIMARY KEY,
    Name varchar(40),
    Paccount varchar(40),
    BDate DATE, CHECK ((YEAR(BDate) < 2006)),
    Mail char(40) check(Mail LIKE '%@%._%') UNIQUE,
    DateSys DATE, CHECK (YEAR(BDate) < YEAR(DateSys)),
);


CREATE TABLE Premium(
    ID BIGINT, FOREIGN KEY (ID) REFERENCES Investor(ID),
    Fgoals varchar(40),
    PRIMARY KEY(ID)
);

CREATE TABLE Worker(
    ID BIGINT, FOREIGN KEY (ID) REFERENCES Premium(ID),
    PRIMARY KEY (ID)
);

CREATE TABLE Beginner( --CAN'T CHECK THAT FOR EVERY WORKER THERES AT LEAST ONE BEGINNER HE GUIDES: WRITE THIS IN COMMENTS
    ID BIGINT, FOREIGN KEY (ID) REFERENCES Investor(ID),
    MentorID BIGINT, FOREIGN KEY (MentorID) REFERENCES Worker(ID),
    PRIMARY KEY(ID)
);

CREATE TABLE Company(
    Symbol varchar(40),
    Founded INT, CHECK (Founded>0 AND Founded < 9999),
    Location varchar(40),
    Sector varchar(40),
    PRIMARY KEY (Symbol)
);


CREATE TABLE Rivalry(
    Company1 varchar(40) NOT NULL, FOREIGN KEY (Company1) REFERENCES Company(Symbol),
    Company2 varchar(40) NOT NULL, FOREIGN KEY (Company2) REFERENCES Company(Symbol),
    Reason varchar(40),
    CHECK(Company1 > Company2),
    PRIMARY KEY (Company1, Company2)
);

CREATE TABLE FollowsRivalry(
    FollowerID BIGINT UNIQUE NOT NULL, FOREIGN KEY (FollowerID) REFERENCES Worker(ID),
    CompanyFollowed_1 varchar(40) NOT NULL,
    CompanyFollowed_2 varchar(40) NOT NULL,
    Report varchar(40),
    UNIQUE (CompanyFollowed_1, CompanyFollowed_2),
    PRIMARY KEY (FollowerID, CompanyFollowed_1, CompanyFollowed_2),
    FOREIGN KEY (CompanyFollowed_1, CompanyFollowed_2) REFERENCES Rivalry(Company1, Company2),
);

CREATE TABLE TradingAccount(
    SumAvailable INT,
    AccID CHAR(10) NOT NULL,
    ID BIGINT NOT NULL, FOREIGN KEY (ID) REFERENCES Investor(ID),
    UNIQUE (AccID),
    PRIMARY KEY (ID, AccID)
);

CREATE TABLE [Transaction](
    AccID CHAR(10) NOT NULL,
    AmountTransferred INT, CHECK (AmountTransferred >= 1000),
    Date DATE,
    ID BIGINT NOT NULL,
    PRIMARY KEY (Date, ACCID, ID),
    FOREIGN KEY (AccID, ID) REFERENCES TradingAccount(AccID, ID)
);

CREATE TABLE Suspicious_Trade(
    TransactionAcc CHAR(10) NOT NULL,
    Date DATE NOT NULL,
    TrID BIGINT NOT NULL,
    WorkerID BIGINT, FOREIGN KEY(WorkerID) REFERENCES Worker(ID),
    Decision BIT,
    PRIMARY KEY(WorkerID, TransactionAcc, DATE, TrID),
    FOREIGN KEY (Date, TransactionAcc, TrID) REFERENCES [Transaction](Date, AccID, ID),
);

CREATE TABLE Stock (
    Date DATE,
    Value INT,
    Symbol varchar(40) NOT NULL,
    PRIMARY KEY (Date, Symbol),
    FOREIGN KEY (Symbol) REFERENCES Company(Symbol)
);

CREATE TABLE Buying(
    uID INT NOT NULL,
    AccID INT NOT NULL,
    Date DATE,
    Symbol varchar(40),
    Quantity INT,
    PRIMARY KEY (uID, AccID, Date, Symbol),
    FOREIGN KEY(uID, AccID) REFERENCES TradingAccount (ID, AccID),
    FOREIGN KEY(Date, Symbol) REFERENCES Stock(Date, Symbol)
);


