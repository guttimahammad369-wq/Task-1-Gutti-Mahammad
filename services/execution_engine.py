import pandas as pd


class ExecutionEngine:

    def __init__(self, dataframe):
        self.df = dataframe

    def execute(self, plan):

        column = plan.get("column")
        aggregation = plan.get("aggregation")
        limit = plan.get("limit")

        if column is None:
            return None

        # -----------------------------
        # COUNT
        # -----------------------------
        if aggregation == "count":

            return (
                self.df[column]
                .value_counts()
            )

        # -----------------------------
        # SUM
        # -----------------------------
        if aggregation == "sum":

            metric = self.find_metric(column)

            if metric is None:
                return None

            result = (
                self.df
                .groupby(column)[metric]
                .sum()
                .sort_values(ascending=False)
            )

            if limit:
                result = result.head(limit)

            return result

        # -----------------------------
        # MEAN
        # -----------------------------
        if aggregation == "mean":

            metric = self.find_metric(column)

            if metric is None:
                return None

            result = (
                self.df
                .groupby(column)[metric]
                .mean()
                .sort_values(ascending=False)
            )

            if limit:
                result = result.head(limit)

            return result

        # -----------------------------
        # MAX
        # -----------------------------
        if aggregation == "max":

            metric = self.find_metric(column)

            if metric is None:
                return None

            result = (
                self.df
                .groupby(column)[metric]
                .sum()
                .sort_values(ascending=False)
            )

            if limit:
                result = result.head(limit)
            else:
                result = result.head(1)

            return result

        # -----------------------------
        # MIN
        # -----------------------------
        if aggregation == "min":

            metric = self.find_metric(column)

            if metric is None:
                return None

            result = (
                self.df
                .groupby(column)[metric]
                .sum()
                .sort_values()
            )

            if limit:
                result = result.head(limit)
            else:
                result = result.head(1)

            return result

        return None

    # -----------------------------------------
    # Automatically detect numeric metric
    # -----------------------------------------

    def find_metric(self, group_column):

        priority = [

            "TotalPrice",
            "Quantity",
            "UnitPrice"

        ]

        for col in priority:

            if col in self.df.columns and col != group_column:
                return col

        numeric = self.df.select_dtypes(include="number").columns

        for col in numeric:

            if col != group_column:
                return col

        return None