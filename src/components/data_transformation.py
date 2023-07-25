import sys
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.exception import CustomException
from src.logger import logging

from src.utils import save_object


@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path = os.path.join('artifacts', "preprocessor.pkl")


class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()

    def get_data_transformer_object(self):
        '''
            Responsible for data transformation
            On Numerical and Categorical Columns
        '''
        try:
            numerical_columns = ['work_year',
                                 'salary_in_usd', 'salary_in_k_usd']

            categorical_columns = ['experience_level', 'employment_type', 'job_title',
                                   'employee_residence', 'remote_ratio', 'company_location', 'company_size']

            numerical_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler())
                ]
            )

            categorical_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("one_hot_encoder", OneHotEncoder()),
                    ("scaler", StandardScaler(with_mean=False))
                ]
            )

            logging.info(
                f"Categorical columns encoding completed: {categorical_columns}")
            logging.info(
                f"Numerical columns encoding completed {numerical_columns}")

            preprocessor = ColumnTransformer(
                [
                    ("numerical_pipeline", numerical_pipeline, numerical_columns),
                    ("categorical_pipeline", categorical_pipeline, categorical_columns)
                ]
            )

            return preprocessor

        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_transformation(self, train_path, test_path):
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)

            # Check the column names in the DataFrames after reading the CSV files
            print(train_df.columns)
            print(test_df.columns)
            print(train_df.dtypes)
            print(test_df.dtypes)
            print(train_df.index)

            logging.info("Read train and test dataframe completed")

            logging.info("Get preprocessing object...")
            preprocessing_obj = self.get_data_transformer_object()

            target_column_name = "salary_in_k_usd"

            # Instead of dropping the target column from input_features_train_df, drop it from train_df
            # input_features_train_df = train_df.drop(
            #     columns=[target_column_name], axis=1)
            # target_feature_train_df = train_df[target_column_name]

            # input_feature_test_df = test_df.drop(
            #     columns=[target_column_name], axis=1)
            # target_feature_test_df = test_df[target_column_name]

            # Separate target column from the features
            target_feature_train_df = train_df[target_column_name]
            target_feature_test_df = test_df[target_column_name]

            input_features_train_df = train_df['experience_level', 'employment_type', 'job_title',
                                               'employee_residence', 'remote_ratio', 'company_location', 'company_size']
            input_features_test_df = test_df['experience_level', 'employment_type', 'job_title',
                                             'employee_residence', 'remote_ratio', 'company_location', 'company_size']

            logging.info(
                "Apply preprocessing object on training and testing dataframes")
            input_feature_train_arr = preprocessing_obj.fit_transform(
                input_features_train_df)
            input_feature_test_arr = preprocessing_obj.transform(
                input_features_test_df)

            # Concatenate target column back to the features
            train_arr = np.c_[input_feature_train_arr,
                              np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr,
                             np.array(target_feature_test_df)]

            save_object(file_path=self.data_transformation_config.preprocessor_obj_file_path,
                        obj=preprocessing_obj)

            logging.info("Saved preprocessing objects.")

            return (
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_obj_file_path
            )

        except Exception as e:
            logging.info(f"Exception: {e}")
            raise CustomException(e, sys)
