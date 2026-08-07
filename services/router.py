class Router:

    def classify(self, question):

        q = question.lower()

        analytics_keywords = [

            # Sales
            "sales",
            "sale",
            "revenue",
            "income",
            "profit",

            # Customers
            "customer",
            "customers",
            "buyer",
            "buyers",
            "client",
            "clients",
            "spender",
            "spending",

            # Products
            "product",
            "products",
            "item",
            "items",

            # Orders
            "order",
            "orders",

            # Payment
            "payment",
            "payment method",
            "paid",

            # Referral
            "referral",
            "source",
            "marketing",

            # Time
            "month",
            "monthly",
            "year",
            "date",

            # Metrics
            "quantity",
            "average",
            "mean",
            "highest",
            "lowest",
            "best",
            "worst",
            "top",
            "most",
            "least",
            "count",
            "total",

            # Status
            "cancelled",
            "canceled",
            "returned",
            "delivered",
            "shipped",
            "pending",

            # Summary
            "summary",
            "summarize",
            "overview",
            "report",

            # Dataset
            "dataset",
            "dataframe",
            "data"
        ]

        for keyword in analytics_keywords:
            if keyword in q:
                return "analytics"

        return "general"