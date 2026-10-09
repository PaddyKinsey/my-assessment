"""
The database loan.db consists of 5 tables:
   1. customers - table containing customer data
   2. loans - table containing loan data pertaining to customers
   3. credit - table containing credit and creditscore data pertaining to customers
   4. repayments - table containing loan repayment data pertaining to customers
   5. months - table containing month name and month ID data

You are required to make use of your knowledge in SQL to query the database object (saved as loan.db) and return the requested information.
Simply fill in the vacant space wrapped in triple quotes per question (each function represents a question)

NOTE:
The database will be reset when grading each section. Any changes made to the database in the previous `SQL` section can be ignored.
Each question in this section is isolated unless it is stated that questions are linked.
Remember to clean your data

"""


def question_1():
    """
    Make use of a JOIN to find the `AverageIncome` per `CustomerClass`
    """

    qry = """Select CustomerClass, Round(Avg(income),2) As Avg_Income From credit
    Join customers On credit.CustomerID = customers.CustomerID
    Group By CustomerClass
    """

    return qry


def question_2():
    """
    Make use of a JOIN to return a breakdown of the number of 'RejectedApplications' per 'Province'.
    Ensure consistent use of either the abbreviated or full version of each province, matching the format found in the customer table.
    """

    qry = """Select
                Case
                    When customers.Region = 'Gauteng' Then 'GT'
                    When customers.Region = 'EasternCape' Then 'EC'
                    When customers.Region = 'Mpumalanga' Then 'MP'
                    When customers.Region = 'WesternCape' Then 'WC'
                    When customers.Region = 'NorthWest' Then 'NW'
                    When customers.Region = 'KwaZulu-Natal' Then 'KZN'
                    When customers.Region = 'NorthernCape' Then 'NC'
                    When customers.Region = 'Limpopo' Then 'LP'
                    When customers.Region = 'FreeState' Then 'FS'
                    Else customers.Region
                End As Region,
            Count(loans.CustomerID) As RejectedApplications
            From Customers Join loans
                On customers.CustomerID = loans.CustomerID
            Where ApprovalStatus = 'Rejected'
            Group By
                Case
                    When customers.Region = 'Gauteng' Then 'GT'
                    When customers.Region = 'EasternCape' Then 'EC'
                    When customers.Region = 'Mpumalanga' Then 'MP'
                    When customers.Region = 'WesternCape' Then 'WC'
                    When customers.Region = 'NorthWest' Then 'NW'
                    When customers.Region = 'KwaZulu-Natal' Then 'KZN'
                    When customers.Region = 'NorthernCape' Then 'NC'
                    When customers.Region = 'Limpopo' Then 'LP'
                    When customers.Region = 'FreeState' Then 'FS'
                    Else customers.Region
                End
                    
            """

    return qry


def question_3():
    """
    Making use of the `INSERT` function, create a new table called `financing` which will include the following columns:
    `CustomerID`,`Income`,`LoanAmount`,`LoanTerm`,`InterestRate`,`ApprovalStatus` and `CreditScore`

    Do not return the new table, just create it.
    """

### Why make use of the Insert function when we can just Create Table As with all the information?
    

    qry = """
    Create Table financing As
    Select
        customers.CustomerID,
        customers.income,
        loans.LoanAmount,
        loans.LoanTerm,
        loans.InterestRate,
        loans.ApprovalStatus,
        credit.CreditScore
    From customers Join loans
        ON customers.CustomerID = loans.CustomerID
    Join credit
        On customers.CustomerID = credit.CustomerID
        -- Now we have issues becuase we haven't actually used insert?
    Where 1=0; -- So that the table is empty, excluding this line and the rest of the function will still create the same table, We can remove duplicates though
    Insert Into financing
    Select Distinct
        customers.CustomerID,
        customers.income,
        loans.LoanAmount,
        loans.LoanTerm,
        loans.InterestRate,
        loans.ApprovalStatus,
        credit.CreditScore
    From customers Join loans
        On customers.CustomerID = loans.CustomerID
    Join credit
        On customers.CustomerID = credit.CustomerID
    """
## Now we have successfully used insert to populate an empty create table

    return qry


# Question 4 and 5 are linked


def question_4():

    """
    Using a `CROSS JOIN` and the `months` table, create a new table called `timeline` that sumarises Repayments per customer per month.
    Columns should be: `CustomerID`, `MonthName`, `NumberOfRepayments`, `AmountTotal`.
    Repayments should only occur between 6am and 6pm London Time.
    Null values to be filled with 0.

    Hint: there should be 12x CustomerID = 1.
    """


    qry = """
        Create Table timeline As
        
        Select 
            c.CustomerID,
            m.MonthName,
            Coalesce(Count(RP.Amount), 0) As NumberOfRepayments,
            Coalesce(Sum(RP.Amount), 0) As AmountTotal
        From (Select Distinct CustomerID From Customers) c
        Cross Join months m
        Left Join Repayments RP
            On c.CustomerID = RP.CustomerID
            And m.MonthName = MonthName(RP.RepaymentDate)
            And Cast(
                Cast(
                    (RP.RepaymentDate At Time Zone RP.TimeZone) At Time Zone 'Europe/London' As TimeStamp)
                As Time) Between '06:00:00' And '18:00:00'
       Group By 
            c.CustomerID,
            m.MonthName
        Order By c.CustomerID
        """
        

    return qry

## Assuming the timestamp is local time then we need to offset by the timezone for each repayment date
# Phase 1, Building the 12000 row table
"""  
    qry = 
    Select 
        c.CustomerID,
        m.MonthName
    From (Select Distinct CustomerID From Customers) c
    Cross Join months m                                   --Months Table included thank you David
    Order By CustomerID
"""
# Phase 2, Adding the repayments 
"""
qry = 
    Select 
        c.CustomerID,
        m.MonthName,
        RP.Amount,
        RP.RepaymentDate,
        RP.TimeZone
    From (Select Distinct CustomerID From Customers) c
    Cross Join months m
    Left Join Repayments RP
        On c.CustomerID = RP.CustomerID
        And m.MonthName = MonthName(RP.RepaymentDate)
    Order By RP.CustomerID
"""
### Phase 3 Shift all local times to London time and exclude out of hours payments
"""
qry = 
    Select 
        c.CustomerID,
        m.MonthName,
        RP.Amount,
        RP.RepaymentDate,
        RP.TimeZone
    From (Select Distinct CustomerID From Customers) c
    Cross Join months m
    Left Join Repayments RP
        On c.CustomerID = RP.CustomerID
        And m.MonthName = MonthName(RP.RepaymentDate)
        And Cast(
            Cast(
                (RP.RepaymentDate At Time Zone RP.TimeZone) At Time Zone 'Europe/London' As TimeStamp)
            As Time) Between '06:00:00' And '18:00:00'
    Order By c.CustomerID
"""
### Phase 4 Coalesce and create the table permanently seen above, explaination was just to understand
"""

"""

def question_5():
    """
    Make use of conditional aggregation to pivot the `timeline` table such that the columns are as follows:
    `CustomerID`, `JanuaryRepayments`, `JanuaryTotal`,...,`DecemberRepayments`, `DecemberTotal`,...etc
    MonthRepayments columns (e.g JanuaryRepayments) should be integers

    Hint: there should be 1x CustomerID = 1
    """

    qry = """
    Select 
        CustomerID,
        
        -- January
        Cast(Sum(Case When MonthName = 'January' Then NumberOfRepayments Else 0 End) As Int) As JanuaryRepayments,
        Sum(Case When MonthName = 'January' Then AmountTotal Else 0 End) As JanuaryTotal,
        
        -- February
        Cast(Sum(Case When MonthName = 'February' Then NumberOfRepayments Else 0 End) As Int) As FebruaryRepayments,
        Sum(Case When MonthName = 'February' Then AmountTotal Else 0 End) As FebruaryTotal,
        
        -- March
        Cast(Sum(Case When MonthName = 'March' Then NumberOfRepayments Else 0 End) As Int) As MarchRepayments,
        Sum(Case When MonthName = 'March' Then AmountTotal Else 0 End) As MarchTotal,
        
        -- April
        Cast(Sum(Case When MonthName = 'April' Then NumberOfRepayments Else 0 End) As Int) As AprilRepayments,
        Sum(Case When MonthName = 'April' Then AmountTotal Else 0 End) As AprilTotal,
        
        -- May
        Cast(Sum(Case When MonthName = 'May' Then NumberOfRepayments Else 0 End) As Int) As MayRepayments,
        Sum(Case When MonthName = 'May' Then AmountTotal Else 0 End) As MayTotal,
        
        -- June
        Cast(Sum(Case When MonthName = 'June' Then NumberOfRepayments Else 0 End) As Int) As JuneRepayments,
        Sum(Case When MonthName = 'June' Then AmountTotal Else 0 End) As JuneTotal,
        
        -- July
        Cast(Sum(Case When MonthName = 'July' Then NumberOfRepayments Else 0 End) As Int) As JulyRepayments,
        Sum(Case When MonthName = 'July' Then AmountTotal Else 0 End) As JulyTotal,
        
        -- August
        Cast(Sum(Case When MonthName = 'August' Then NumberOfRepayments Else 0 End) As Int) As AugustRepayments,
        Sum(Case When MonthName = 'August' Then AmountTotal Else 0 End) As AugustTotal,
        
        -- September
        Cast(Sum(Case When MonthName = 'September' Then NumberOfRepayments Else 0 End) As Int) As SeptemberRepayments,
        Sum(Case When MonthName = 'September' Then AmountTotal Else 0 End) As SeptemberTotal,
        
        -- October
        Cast(Sum(Case When MonthName = 'October' Then NumberOfRepayments Else 0 End) As Int) As OctoberRepayments,
        Sum(Case When MonthName = 'October' Then AmountTotal Else 0 End) As OctoberTotal,
        
        -- November
        Cast(Sum(Case When MonthName = 'November' Then NumberOfRepayments Else 0 End) As Int) As NovemberRepayments,
        Sum(Case When MonthName = 'November' Then AmountTotal Else 0 End) As NovemberTotal,
        
        -- December
        Cast(Sum(Case When MonthName = 'December' Then NumberOfRepayments Else 0 End) As Int) As DecemberRepayments,
        Sum(Case When MonthName = 'December' Then AmountTotal Else 0 End) As DecemberTotal,

        -- Year Totals
        Cast(Sum(NumberOfRepayments) As Int) As TotalRepayments,
        Sum(AmountTotal) As TotalAmount

    From timeline
    Group By CustomerID
    Order By CustomerID
    """

    return qry


# QUESTION 6 and 7 are linked, Do not be concerned with timezones or repayment times for these question.


def question_6():
    """
    The `customers` table was created by merging two separate tables: one containing data for male customers and the other for female customers.
    Due to an error, the data in the age columns were misaligned in both original tables, resulting in a shift of two places upwards in relation to the corresponding CustomerID.

    Create a table called `corrected_customers` with columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`
    Utilize a window function to correct this mistake in the new `CorrectedAge` column.
    Null values can be input manually - i.e. values that overflow should loop to the top of each gender.

    Also return a result set for this table (ie SELECT * FROM corrected_customers)
    """

    qry = """
        Create Table corrected_customers As
        -- "Remember to clean your data"
        With CleanCustomers As (Select Distinct CustomerID, Age, Gender
            From customers
        ),
        
        -- Count the exact number of unique males and females
        GenderGroups As (
            Select 
                CustomerID,
                Age,
                Gender,
                Cast(Count(*) Over (Partition By Gender) As Int) As TotalCount
            From CleanCustomers
        )
        
        -- Execute the shift on the clean data, adding the lead to catch the overflow
        Select 
            CustomerID,
            Age,
            Coalesce(
                Lag(Age, 2) Over (Partition By Gender Order By CustomerID),
                Lead(Age, TotalCount - 2) Over (Partition By Gender Order By CustomerID)
            ) As CorrectedAge,
            Gender
        From GenderGroups;
        
        Select * From corrected_customers Order By CustomerID;
    """

    return qry


def question_7():
    """
    Create a column in corrected_customers called 'AgeCategory' that categorizes customers by age.
    Age categories should be as follows:
        - `Teen`: CorrectedAge < 20
        - `Young Adult`: 20 <= CorrectedAge < 30
        - `Adult`: 30 <= CorrectedAge < 60
        - `Pensioner`: CorrectedAge >= 60

    Make use of a windows function to assign a rank to each customer based on the total number of repayments per age group. Add this into a "Rank" column.
    The ranking should not skip numbers in the sequence, even when there are ties, i.e. 1,2,2,2,3,4 not 1,2,2,2,5,6
    Customers with no repayments should be included as 0 in the result.

    Return columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`, `AgeCategory`, `Rank` 
    """ ## We call this CustomerStats

    qry = """
        With CustomerStats As (
            Select 
                cc.CustomerID,
                cc.Age,
                cc.CorrectedAge,
                cc.Gender,
                
                -- Create the AgeCategory column
                Case 
                    When cc.CorrectedAge < 20 Then 'Teen'
                    When cc.CorrectedAge >= 20 And cc.CorrectedAge < 30 Then 'Young Adult'
                    When cc.CorrectedAge >= 30 And cc.CorrectedAge < 60 Then 'Adult'
                    When cc.CorrectedAge >= 60 Then 'Pensioner'
                End As AgeCategory,
                
                -- Count the raw repayments (ignoring timezones as requested)
                Coalesce(Count(r.Amount), 0) As TotalRepayments
                
            From corrected_customers cc
            Left Join repayments r 
                On cc.CustomerID = r.CustomerID
            Group By 
                cc.CustomerID,
                cc.Age,
                cc.CorrectedAge,
                cc.Gender)
        
        Select 
            CustomerID,
            Age,
            CorrectedAge,
            Gender,
            AgeCategory,
            
            --The Window Function Ranker, dense rank to not skip ranks
            Dense_Rank() Over (Partition By AgeCategory Order By TotalRepayments Desc) As Rank
            
        From CustomerStats
        Order By CustomerID
    """

    return qry
