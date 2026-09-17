from pathlib import Path
import pandas as pd


class DatasetLoader:
    """
    Loads all datasets required for the Personalized Marketing AI project.
    """

    def __init__(self, data_directory="data/raw"):
        self.data_directory = Path(data_directory)

    def load_csv(self, filename):
        path = self.data_directory / filename

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return pd.read_csv(path)

    def load_all(self):
        datasets = {
            "customers": self.load_csv("customers.csv"),
            "transactions": self.load_csv("transactions.csv"),
            "product_holdings": self.load_csv("product_holdings.csv"),
            "products": self.load_csv("products.csv"),
            "campaigns": self.load_csv("campaigns.csv"),
            "campaign_interactions": self.load_csv(
                "campaign_interactions.csv"
            ),
            "recommendations": self.load_csv(
                "recommendations.csv"
            ),
        }

        return datasets