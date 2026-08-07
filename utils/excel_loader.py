import pandas as pd

# Path to the Excel file
file_path = "data/Dataset for Data Analytics (1).xlsx"

# Read the Excel file
df = pd.read_excel(file_path)

print("=" * 60)
print("✅ DATASET LOADED SUCCESSFULLY")
print("=" * 60)

print("\nFirst 5 Rows:")
print(df.head())

print("\n" + "=" * 60)
print("Dataset Shape")
print("=" * 60)
print(df.shape)

print("\n" + "=" * 60)
print("Column Names")
print("=" * 60)
print(df.columns.tolist())

print("\n" + "=" * 60)
print("Dataset Information")
print("=" * 60)
df.info()

print("\n" + "=" * 60)
print("Missing Values")
print("=" * 60)
print(df.isnull().sum())