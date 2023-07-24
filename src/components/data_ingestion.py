import os
import sys
from src.exception import CustomException
from src.logger import logging
import pandas as pd
from sklearn.model_selection import train_test_split
from dataclasses import dataclass


@dataclass
class DataIngestionConfig:
    train_data_path: str = os.path.join('artifacts', 'train.csv')
    test_data_path: str = os.path.join('artifacts', 'test.csv')
    raw_data_path: str = os.path.join('artifacts', 'data.csv')


class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self):
        logging.info("Start ingestion component")
        try:
            # Read dataset from csv
            df = pd.read_csv(
                'notebook/data/cleaned_data_science_jobs.csv')
            logging.info("Read cleaned_data_science_jobs dataset as dataframe")

            # make directory for our artifacts
            logging.info(
                "Creating artifact directory, and copy ingested data into artifact directory")
            os.makedirs(os.path.dirname(
                self.ingestion_config.raw_data_path), exist_ok=True)
            df.to_csv(self.ingestion_config.raw_data_path,
                      index=False, header=True)

            # Initiate train test split
            logging.info("Initiate train test split of our raw data")
            train_set, test_set = train_test_split(
                df, test_size=0.2, random_state=44)

            # Save train set, and test set to artifact
            logging.info("Save train set and test set into artifact directory")
            train_set.to_csv(
                self.ingestion_config.train_data_path, index=False, header=True)
            test_set.to_csv(self.ingestion_config.test_data_path,
                            index=False, header=True)

            logging.info("Data Ingestion Complete...")

            return (
                self.ingestion_config.raw_data_path,
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path
            )

        except Exception as e:
            logging.info("Raised exception ", e)
            raise CustomException(e, sys)


if __name__ == "__main__":
    dataIngestion = DataIngestion()
    dataIngestion.initiate_data_ingestion()
