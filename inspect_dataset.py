from src.data.loader import DatasetLoader
from src.data.validator import print_profile


def main():

    loader = DatasetLoader()

    datasets = loader.load_all()

    print("\n")
    print("#" * 70)
    print("PERSONALIZED MARKETING AI")
    print("DATASET INSPECTION")
    print("#" * 70)

    for name, df in datasets.items():

        print_profile(name, df)

        print("\nFirst 5 rows:")
        print(df.head().to_string())

    print("\n")
    print("#" * 70)
    print("DATASET INSPECTION COMPLETED")
    print("#" * 70)


if __name__ == "__main__":
    main()