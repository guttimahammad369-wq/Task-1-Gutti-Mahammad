import plotly.express as px


class VisualizationService:

    def __init__(self, dataframe):
        self.df = dataframe

    def sales_by_product(self):
        data = (
            self.df.groupby("Product")["TotalPrice"]
            .sum()
            .reset_index()
        )

        return px.bar(
            data,
            x="Product",
            y="TotalPrice",
            title="Sales by Product"
        )

    def order_status_distribution(self):
        data = (
            self.df["OrderStatus"]
            .value_counts()
            .reset_index()
        )

        data.columns = ["OrderStatus", "Count"]

        return px.pie(
            data,
            names="OrderStatus",
            values="Count",
            title="Order Status Distribution"
        )

    def payment_method_distribution(self):
        data = (
            self.df["PaymentMethod"]
            .value_counts()
            .reset_index()
        )

        data.columns = ["PaymentMethod", "Count"]

        return px.pie(
            data,
            names="PaymentMethod",
            values="Count",
            title="Payment Method Distribution"
        )

    def referral_source_distribution(self):
        data = (
            self.df["ReferralSource"]
            .value_counts()
            .reset_index()
        )

        data.columns = ["ReferralSource", "Count"]

        return px.bar(
            data,
            x="ReferralSource",
            y="Count",
            title="Referral Source Distribution"
        )

    def monthly_sales(self):
        df = self.df.copy()

        df["Month"] = df["Date"].dt.to_period("M").astype(str)

        data = (
            df.groupby("Month")["TotalPrice"]
            .sum()
            .reset_index()
        )

        return px.line(
            data,
            x="Month",
            y="TotalPrice",
            title="Monthly Sales Trend"
        )