import pandas as pd


class AnalyticsService:

    def __init__(self, dataframe):
        self.df = dataframe

    # ------------------------
    # BASIC
    # ------------------------

    def total_sales(self):
        return self.df["TotalPrice"].sum()

    def total_orders(self):
        return len(self.df)

    def unique_customers(self):
        return self.df["CustomerID"].nunique()

    def average_order_value(self):
        return self.df["TotalPrice"].mean()

    def best_selling_product(self):
        return (
            self.df.groupby("Product")["Quantity"]
            .sum()
            .idxmax()
        )

    # ------------------------
    # TOP CUSTOMERS
    # ------------------------

    def top_customers(self, n=10):
        return (
            self.df.groupby("CustomerID")["TotalPrice"]
            .sum()
            .sort_values(ascending=False)
            .head(n)
        )

    # ------------------------
    # PAYMENT
    # ------------------------

    def most_used_payment_method(self):
        return (
            self.df["PaymentMethod"]
            .value_counts()
            .idxmax()
        )

    # ------------------------
    # REFERRAL
    # ------------------------

    def best_referral_source(self):
        return (
            self.df.groupby("ReferralSource")["TotalPrice"]
            .sum()
            .idxmax()
        )

    # ------------------------
    # MONTHLY SALES
    # ------------------------

    def highest_sales_month(self):

        temp = self.df.copy()

        temp["Date"] = pd.to_datetime(temp["Date"])

        temp["Month"] = temp["Date"].dt.strftime("%B")

        return (
            temp.groupby("Month")["TotalPrice"]
            .sum()
            .idxmax()
        )

    # ------------------------
    # CANCELLED ORDERS
    # ------------------------

    def cancelled_orders(self):
        return (
            self.df["OrderStatus"]
            .str.lower()
            .eq("cancelled")
            .sum()
        )

    # ------------------------
    # SUMMARY
    # ------------------------

    def summary(self):
        return f"""
📊 DATASET SUMMARY

Total Orders: {self.total_orders()}

Total Revenue: ₹{self.total_sales():,.2f}

Unique Customers: {self.unique_customers()}

Average Order Value: ₹{self.average_order_value():,.2f}

Best Selling Product: {self.best_selling_product()}

Most Used Payment Method: {self.most_used_payment_method()}

Best Referral Source: {self.best_referral_source()}

Highest Sales Month: {self.highest_sales_month()}

Cancelled Orders: {self.cancelled_orders()}
"""