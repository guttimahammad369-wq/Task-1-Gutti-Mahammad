import re


class QueryPlanner:

    def __init__(self, dataframe):
        self.df = dataframe
        self.columns = list(dataframe.columns)

    # -------------------------
    # Detect Column
    # -------------------------

    def detect_column(self, question):

        q = question.lower()

        for col in self.columns:

            if col.lower() in q:
                return col

        synonyms = {

            "customer": "CustomerID",
            "customers": "CustomerID",

            "buyer": "CustomerID",

            "product": "Product",

            "products": "Product",

            "payment": "PaymentMethod",

            "payment method": "PaymentMethod",

            "status": "OrderStatus",

            "order status": "OrderStatus",

            "referral": "ReferralSource",

            "source": "ReferralSource",

            "date": "Date",

            "month": "Date",

            "revenue": "TotalPrice",

            "sales": "TotalPrice",

            "price": "TotalPrice",

            "quantity": "Quantity"

        }

        for key, value in synonyms.items():

            if key in q:
                return value

        return None

    # -------------------------
    # Detect Aggregation
    # -------------------------

    def detect_aggregation(self, question):

        q = question.lower()

        if any(x in q for x in [
            "sum",
            "total",
            "revenue",
            "sales"
        ]):
            return "sum"

        if any(x in q for x in [
            "average",
            "mean"
        ]):
            return "mean"

        if any(x in q for x in [
            "count",
            "how many",
            "number of"
        ]):
            return "count"

        if any(x in q for x in [
            "maximum",
            "highest",
            "largest",
            "top"
        ]):
            return "max"

        if any(x in q for x in [
            "minimum",
            "lowest"
        ]):
            return "min"

        return None

    # -------------------------
    # Detect Limit
    # -------------------------

    def detect_limit(self, question):

        m = re.search(r"\b(\d+)\b", question)

        if m:
            return int(m.group(1))

        return None

    # -------------------------
    # Build Plan
    # -------------------------

    def build(self, question):

        return {

            "column": self.detect_column(question),

            "aggregation": self.detect_aggregation(question),

            "limit": self.detect_limit(question)

        }