class PromptService:

    def __init__(self, dataframe):

        self.df = dataframe

    def build(self, question):

        columns = ", ".join(self.df.columns)

        sample = self.df.head(5).to_markdown(index=False)

        return f"""
You are a Senior Data Analyst.

You are provided with a pandas DataFrame named df.

Dataset Information

Columns:

{columns}

First Five Rows:

{sample}

User Question:

{question}

Generate ONLY executable Python code.

Rules:

1. Use dataframe name df.
2. Store final answer in variable result.
3. Never explain.
4. Never use markdown.
5. Never import anything.
6. Never read any file.
"""