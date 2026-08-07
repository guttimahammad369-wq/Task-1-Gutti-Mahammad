from typing import Any, Dict, Optional, Union
import pandas as pd

from analytics.data_loader import DataLoader, data_loader
from utils.logger import logger


class AnalyticsEngine:
    """Deterministic analytics calculation engine operating over the Pandas DataFrame.

    Provides modular, isolated data aggregation functions for revenue, sales trends,
    product performance, order status analysis, and payment breakdowns.
    """

    def __init__(self, df: Optional[pd.DataFrame] = None):
        """Initializes AnalyticsEngine with a DataFrame or loads from DataLoader.

        Args:
            df: Optional Pandas DataFrame. Defaults to data_loader.load_data().
        """
        if df is not None:
            self.df = df
        else:
            self.df = data_loader.load_data()

    def get_summary_kpis(self) -> Dict[str, Any]:
        """Calculates macro-level business KPI metrics.

        Returns:
            Dict containing total revenue, total orders, total products sold,
            average order value (AOV), and cancellation rate.
        """
        total_revenue = float(self.df["TotalPrice"].sum()) if "TotalPrice" in self.df.columns else 0.0
        total_orders = len(self.df)
        total_quantity = int(self.df["Quantity"].sum()) if "Quantity" in self.df.columns else 0
        aov = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0

        cancelled_orders = 0
        if "OrderStatus" in self.df.columns:
            cancelled_orders = int((self.df["OrderStatus"].str.lower() == "cancelled").sum())
        cancellation_rate = round((cancelled_orders / total_orders) * 100, 2) if total_orders > 0 else 0.0

        return {
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "total_items_sold": total_quantity,
            "average_order_value": aov,
            "cancelled_orders": cancelled_orders,
            "cancellation_rate_pct": cancellation_rate,
        }

    def get_revenue_by_product(self, top_n: int = 10) -> pd.DataFrame:
        """Aggregates revenue and items sold grouped by product.

        Args:
            top_n: Number of top products to return.

        Returns:
            pd.DataFrame: Sorted product sales summary.
        """
        if "Product" not in self.df.columns or "TotalPrice" not in self.df.columns:
            return pd.DataFrame()

        summary = (
            self.df.groupby("Product")
            .agg(
                TotalRevenue=("TotalPrice", "sum"),
                UnitsSold=("Quantity", "sum"),
                OrderCount=("OrderID", "count"),
                AveragePrice=("UnitPrice", "mean"),
            )
            .reset_index()
        )

        summary["TotalRevenue"] = summary["TotalRevenue"].round(2)
        summary["AveragePrice"] = summary["AveragePrice"].round(2)
        return summary.sort_values(by="TotalRevenue", ascending=False).head(top_n)

    def get_monthly_sales_trend(self) -> pd.DataFrame:
        """Computes monthly aggregated sales revenue and order counts.

        Returns:
            pd.DataFrame: Chronological monthly revenue breakdown.
        """
        if "Date" not in self.df.columns or "TotalPrice" not in self.df.columns:
            return pd.DataFrame()

        temp_df = self.df.copy()
        temp_df["YearMonth"] = temp_df["Date"].dt.to_period("M").astype(str)

        monthly = (
            temp_df.groupby("YearMonth")
            .agg(
                TotalRevenue=("TotalPrice", "sum"),
                OrderCount=("OrderID", "count"),
                AverageOrderValue=("TotalPrice", "mean"),
            )
            .reset_index()
        )

        monthly["TotalRevenue"] = monthly["TotalRevenue"].round(2)
        monthly["AverageOrderValue"] = monthly["AverageOrderValue"].round(2)
        return monthly.sort_values(by="YearMonth", ascending=True)

    def get_order_status_distribution(self) -> pd.DataFrame:
        """Aggregates order counts and total revenue by order status.

        Returns:
            pd.DataFrame: Order status breakdown.
        """
        if "OrderStatus" not in self.df.columns:
            return pd.DataFrame()

        dist = (
            self.df.groupby("OrderStatus")
            .agg(
                OrderCount=("OrderID", "count"),
                TotalRevenue=("TotalPrice", "sum"),
            )
            .reset_index()
        )

        dist["Percentage"] = round((dist["OrderCount"] / len(self.df)) * 100, 2)
        dist["TotalRevenue"] = dist["TotalRevenue"].round(2)
        return dist.sort_values(by="OrderCount", ascending=False)

    def get_referral_source_performance(self) -> pd.DataFrame:
        """Aggregates revenue performance by marketing referral source.

        Returns:
            pd.DataFrame: Referral source revenue summary.
        """
        if "ReferralSource" not in self.df.columns:
            return pd.DataFrame()

        ref = (
            self.df.groupby("ReferralSource")
            .agg(
                TotalRevenue=("TotalPrice", "sum"),
                OrderCount=("OrderID", "count"),
                AverageOrderValue=("TotalPrice", "mean"),
            )
            .reset_index()
        )

        ref["TotalRevenue"] = ref["TotalRevenue"].round(2)
        ref["AverageOrderValue"] = ref["AverageOrderValue"].round(2)
        return ref.sort_values(by="TotalRevenue", ascending=False)

    def get_payment_method_distribution(self) -> pd.DataFrame:
        """Aggregates payment method usage and revenue split.

        Returns:
            pd.DataFrame: Payment method breakdown.
        """
        if "PaymentMethod" not in self.df.columns:
            return pd.DataFrame()

        pay = (
            self.df.groupby("PaymentMethod")
            .agg(
                OrderCount=("OrderID", "count"),
                TotalRevenue=("TotalPrice", "sum"),
            )
            .reset_index()
        )

        pay["UsagePercentage"] = round((pay["OrderCount"] / len(self.df)) * 100, 2)
        pay["TotalRevenue"] = pay["TotalRevenue"].round(2)
        return pay.sort_values(by="OrderCount", ascending=False)

    def get_coupon_code_performance(self) -> pd.DataFrame:
        """Aggregates revenue and order metrics grouped by coupon codes.

        Returns:
            pd.DataFrame: Coupon performance breakdown.
        """
        if "CouponCode" not in self.df.columns:
            return pd.DataFrame()

        coupons = (
            self.df.groupby("CouponCode")
            .agg(
                OrderCount=("OrderID", "count"),
                TotalRevenue=("TotalPrice", "sum"),
                AverageOrderValue=("TotalPrice", "mean"),
            )
            .reset_index()
        )

        coupons["TotalRevenue"] = coupons["TotalRevenue"].round(2)
        coupons["AverageOrderValue"] = coupons["AverageOrderValue"].round(2)
        return coupons.sort_values(by="TotalRevenue", ascending=False)

    def filter_dataset(
        self,
        product: Optional[str] = None,
        order_status: Optional[str] = None,
        payment_method: Optional[str] = None,
        referral_source: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """Applies dynamic filters over the dataset for targeted analysis.

        Args:
            product: Case-insensitive product name.
            order_status: Order status string.
            payment_method: Payment method string.
            referral_source: Marketing referral source.
            start_date: Filter start date (YYYY-MM-DD).
            end_date: Filter end date (YYYY-MM-DD).

        Returns:
            pd.DataFrame: Filtered dataset subset.
        """
        filtered_df = self.df.copy()

        if product:
            filtered_df = filtered_df[
                filtered_df["Product"].str.contains(product, case=False, na=False)
            ]
        if order_status:
            filtered_df = filtered_df[
                filtered_df["OrderStatus"].str.contains(order_status, case=False, na=False)
            ]
        if payment_method:
            filtered_df = filtered_df[
                filtered_df["PaymentMethod"].str.contains(payment_method, case=False, na=False)
            ]
        if referral_source:
            filtered_df = filtered_df[
                filtered_df["ReferralSource"].str.contains(referral_source, case=False, na=False)
            ]
        if start_date:
            filtered_df = filtered_df[filtered_df["Date"] >= pd.to_datetime(start_date)]
        if end_date:
            filtered_df = filtered_df[filtered_df["Date"] <= pd.to_datetime(end_date)]

        return filtered_df


# Global singleton instance for single engine execution
analytics_engine = AnalyticsEngine()
