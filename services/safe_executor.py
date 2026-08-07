import pandas as pd


class SafeExecutor:

    BLOCKED = [

        "import os",
        "import sys",
        "subprocess",
        "socket",
        "shutil",
        "open(",
        "exec(",
        "eval(",
        "__import__",
        "compile(",
        "globals(",
        "locals(",
        "os.",
        "sys.",
        "pathlib",
        "requests",
        "http",
        "pip",

    ]

    def execute(self, df, code):

        lower = code.lower()

        for word in self.BLOCKED:

            if word in lower:
                return f"❌ Unsafe code detected:\n{word}"

        variables = {

            "df": df,
            "pd": pd,

        }

        try:

            exec(code, {}, variables)

            if "result" not in variables:
                return "No result generated."

            return variables["result"]

        except Exception as e:

            return f"Execution Error:\n\n{e}"