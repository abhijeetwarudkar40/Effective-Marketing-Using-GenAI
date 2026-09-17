import pandas as pd


def profile_dataframe(df):
    """
    Generate a basic profile of a dataframe.
    """

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
    }


def print_profile(name, df):
    """
    Print dataset information.
    """

    profile = profile_dataframe(df)

    print("\n" + "=" * 70)
    print(f"DATASET: {name.upper()}")
    print("=" * 70)

    print(f"Rows      : {profile['rows']}")
    print(f"Columns   : {profile['columns']}")
    print(f"Duplicates: {profile['duplicate_rows']}")

    print("\nColumns:")

    for column in profile["column_names"]:
        print(f"  - {column}")

    print("\nData Types:")

    for column, dtype in profile["data_types"].items():
        print(f"  {column}: {dtype}")

    print("\nMissing Values:")

    for column, missing in profile["missing_values"].items():
        if missing > 0:
            print(f"  {column}: {missing}")