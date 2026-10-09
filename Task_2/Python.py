import os

import numpy as np
import pandas as pd

"""
To answer the following questions, make use of datasets: 
    'scheduled_loan_repayments.csv'
    'actual_loan_repayments.csv'
These files are located in the 'data' folder. 

'scheduled_loan_repayments.csv' contains the expected monthly payments for each loan. These values are constant regardless of what is actually paid.
'actual_loan_repayments.csv' contains the actual amount paid to each loan for each month.

All loans have a loan term of 2 years with an annual interest rate of 10%. Repayments are scheduled monthly.
A type 1 default occurs on a loan when any scheduled monthly repayment is not met in full.
A type 2 default occurs on a loan when more than 15% of the expected total payments are unpaid for the year.

Note: Do not round any final answers.

"""


def calculate_df_balances(df_scheduled, df_actual):
    """
    This is a utility function that creates a merged dataframe that will be used in the following questions.
    This function will not be graded, do not make changes to it.

    Args:
        df_scheduled (DataFrame): Dataframe created from the 'scheduled_loan_repayments.csv' dataset
        df_actual (DataFrame): Dataframe created from the 'actual_loan_repayments.csv' dataset

    Returns:
        DataFrame: A merged Dataframe with additional calculated columns to help with the following questions.

    """

    df_merged = pd.merge(df_actual, df_scheduled)

    def calculate_balance(group):
        r_monthly = 0.1 / 12
        group = group.sort_values("Month")
        balances = []
        interest_payments = []
        loan_start_balances = []
        for index, row in group.iterrows():
            if balances:
                interest_payment = balances[-1] * r_monthly
                balance_with_interest = balances[-1] + interest_payment
            else:
                interest_payment = row["LoanAmount"] * r_monthly
                balance_with_interest = row["LoanAmount"] + interest_payment
                loan_start_balances.append(row["LoanAmount"])

            new_balance = balance_with_interest - row["ActualRepayment"]
            interest_payments.append(interest_payment)

            new_balance = max(0, new_balance)
            balances.append(new_balance)

        loan_start_balances.extend(balances)
        loan_start_balances.pop()
        group["LoanBalanceStart"] = loan_start_balances
        group["LoanBalanceEnd"] = balances
        group["InterestPayment"] = interest_payments
        return group

    df_balances = (
        df_merged.groupby("LoanID", as_index=False)
        .apply(calculate_balance)
        .reset_index(drop=True)
    )

    df_balances["LoanBalanceEnd"] = df_balances["LoanBalanceEnd"].round(2)
    df_balances["InterestPayment"] = df_balances["InterestPayment"].round(2)
    df_balances["LoanBalanceStart"] = df_balances["LoanBalanceStart"].round(2)

    return df_balances


# Do not edit these directories
root = os.getcwd()

if "Task_2" in root:
    df_scheduled = pd.read_csv("data/scheduled_loan_repayments.csv")
    df_actual = pd.read_csv("data/actual_loan_repayments.csv")
else:
    df_scheduled = pd.read_csv("Task_2/data/scheduled_loan_repayments.csv")
    df_actual = pd.read_csv("Task_2/data/actual_loan_repayments.csv")

df_balances = calculate_df_balances(df_scheduled, df_actual)


def question_1(df_balances):
    """
    Calculate the percent of loans that defaulted as per the type 1 default definition.

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The percentage of type 1 defaulted loans (ie 50.0 not 0.5)

    """

    # filter for any month where a customer paid less than they were supposed to
    missed_payments = df_balances[df_balances["ActualRepayment"] < df_balances["ScheduledRepayment"]]
    
    # extract the unique LoanIDs from those defaulted months
    defaulted_loans_count = missed_payments["LoanID"].nunique()
    
    # find the total number of unique loans in the entire dataframe
    total_loans_count = df_balances["LoanID"].nunique()
    
    # calculate the percentage
    default_rate_percent = (defaulted_loans_count / total_loans_count) * 100

    return default_rate_percent


def question_2(df_scheduled, df_balances):
    """
    Calculate the percent of loans that defaulted as per the type 2 default definition

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function
        df_scheduled (DataFrame): Dataframe created from the 'scheduled_loan_repayments.csv' dataset

    Returns:
        float: The percentage of type 2 defaulted loans (ie 50.0 not 0.5)

    """
    # group the data into Year 1 and Year 2 blocks and sum the payments, the actual_loan_repayment.csv only goes to month 12 but we include this for posterity
    yearly_totals = (
        df_balances.assign(Year=(df_balances["Month"] - 1) // 12 + 1)
        .groupby(["LoanID", "Year"])
        .agg(
            TotalScheduled=("ScheduledRepayment", "sum"),
            TotalActual=("ActualRepayment", "sum"))
        .reset_index())
    
    # calculate the percentage of unpaid scheduled payments for each year
    yearly_totals["UnpaidPercent"] = ((yearly_totals["TotalScheduled"] - yearly_totals["TotalActual"]) / yearly_totals["TotalScheduled"])
    
    # count unique loans that exceeded the 15% unpaid threshold in ANY year
    defaulted_loans_count = yearly_totals[yearly_totals["UnpaidPercent"] > 0.15]["LoanID"].nunique()
    
    # calculate type 2 default percentage
    total_loans_count = df_balances["LoanID"].nunique()
    default_rate_percent = (defaulted_loans_count / total_loans_count) * 100

    return default_rate_percent


def question_3(df_balances):
    """
    Calculate the anualized portfolio CPR (As a %) from the geometric mean SMM.
    SMM is calculated as: (Unscheduled Principal)/(Start of Month Loan Balance)
    SMM_mean is calculated as (∏(1+SMM))^(1/12) - 1
    CPR is calcualted as: 1 - (1- SMM_mean)^12

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The anualized CPR of the loan portfolio as a percent.

    """
    #isolate genuine prepayments 
    # .clip(lower=0) ensures underpayments (defaults) don't act as negative prepayments
    df_balances["UnscheduledPrincipal"] = (
        df_balances["ActualRepayment"] - df_balances["ScheduledRepayment"]
    ).clip(lower=0)

    # aggregate to the portfolio level per month
    monthly_stats = df_balances.groupby("Month").agg(
        TotalUnscheduled=("UnscheduledPrincipal", "sum"),
        TotalStartBalance=("LoanBalanceStart", "sum"))

    # calculate SMMM
    monthly_stats["SMM"] = monthly_stats["TotalUnscheduled"] / monthly_stats["TotalStartBalance"]

    # 4. Calculate the geometric mean SMM
    # np.prod() perfectly handles the ∏ operator across the array
    smm_mean = (np.prod(1 + monthly_stats["SMM"]) ** (1 / 12)) - 1

    # 5. Annualize to Conditional Prepayment Rate (CPR)
    cpr = 1 - (1 - smm_mean) ** 12
    cpr_percent = cpr * 100

    return cpr_percent


def question_4(df_balances):
    """
    Calculate the predicted total loss for the second year in the loan term.
    Use the equation: probability_of_default * total_loan_balance * (1 - recovery_rate).
    The probability_of_default value must be taken from either your question_1 or question_2 answer.
    Decide between the two answers based on which default definition you believe to be the more useful metric.
    Assume a recovery rate of 80%

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The predicted total loss for the second year in the loan term.

    """
    """
    We use Type 2 because severe annual deficits (>15%) accurately represent loans that will be written off, whereas Type 1 includes minor, recoverable late payments.We divide by 100 to convert the returned percentage (e.g., 1.2) back into a probability ratio (0.012).
    """
    probability_of_default = question_2(df_scheduled, df_balances) / 100

    """
     determine Total Loan Balance for Year 2 By taking the ending balance of Month 12
     """
    total_loan_balance = df_balances[df_balances["Month"] == 12]["LoanBalanceEnd"].sum()
    
    ### calculate Total Predicted Loss TPL
    
    recovery_rate = 0.80
    TPL = probability_of_default * total_loan_balance * (1 - recovery_rate)
    
    return TPL


"""
if __name__ == "__main__":
    q1_result = question_1(df_balances)
    print(f"Type 1 Default Rate: {q1_result}%")

    q2_result = question_2(df_scheduled, df_balances)
    print(f"Type 2 Default Rate: {q2_result}%")

    q3_result = question_3(df_balances)
    print(f"Annualized Portfolio CPR: {q3_result}%")

    q4_result = question_4(df_balances)
    print(f"Predicted Year 2 Loss: {q4_result:,.2f}")

"""