import logging

import pandas as pd
from feature_engine.encoding import OrdinalEncoder, OneHotEncoder
from feature_engine.transformation import YeoJohnsonTransformer
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

from src.config.core import RANDOM_STATE, TEST_SIZE, VARS_TO_DROP, TARGET, CAT_VARS_ONEHOT, \
        CAT_VARS_ORDINAL_ARBITARY, NUM_VARS_YEO_YOHNSON, VAR_REPLACE_EMPTY_DATA

from logging import log

def check_keys(dict_, required_keys):
    """
    Check if a dictionary contains all expected keys
    :param dict_:
    :param required_keys:
    :return:
    """

    for key in required_keys:
        if key not in dict_:
            raise ValueError(f'input argument "data_files" is missing required key {key}')

def get_read_data(filepath) -> pd.DataFrame:
    return pd.read_csv(filepath)

def read_data(data_files):
    """
    Read and save a csv from the provided path
    :param data_files:  A dictionary of data file paths.
    The keys that this function will use are:
        'input_raw_data_file': the initial raw file to use for the pipeline
        'raw_data_file': the (same) raw file, but saved in a different dir to use the rest of the pipeline
    :return:
    """

    required_keys = [
        'input_raw_data_file',
        'raw_data_file'
    ]

    check_keys(data_files, required_keys)

    data = get_read_data(data_files['input_raw_data_file'])
    data.to_csv(data_files['raw_data_file'], index=False)
    logging.Logger(f"File {data_files['raw_data_file']} was saved successfully.")

def get_split_train_test(data):
    x_train, x_test, y_train, y_test = train_test_split(data.drop(VARS_TO_DROP+[TARGET], axis=1),
                                                        data[TARGET],
                                                        test_size=TEST_SIZE,
                                                        random_state=RANDOM_STATE,
                                                        )

    return x_train,x_test,y_train,y_test

def split_train_test(data_files):
    """
    Save and return the train and test data of the initial raw data
    :param data_files: A dictionary of data file paths.
    :return:
    """

    required_keys = [
        'raw_data_file', 'raw_x_train_file', 'raw_x_test_file', 'raw_y_train_file', 'raw_y_test_file'
    ]

    check_keys(data_files, required_keys)

    data = pd.read_csv(data_files['raw_data_file'])
    x_train, x_test, y_train, y_test = get_split_train_test(data)

    x_train.to_csv(data_files['raw_x_train_file'], index=False)
    x_test.to_csv(data_files['raw_x_test_file'], index=False)
    y_train.to_csv(data_files['raw_y_train_file'], index=False)
    y_test.to_csv(data_files['raw_y_test_file'], index=False)

    logging.Logger("Initial dataset was split and saved successfully.")

def replace_empty_in_col(data: pd.DataFrame) -> pd.DataFrame:
    """
    In order to convert a string variable that is numeric to float,
    replace empty space value with -1
    :param data:
    :return:
    """

    for feature in VAR_REPLACE_EMPTY_DATA:
        data[feature] = data[feature].str.replace(' ', '-1').astype(float)

    return  data

def fit_categorical_encoders(x_train: pd.DataFrame, y_train: pd.Series) -> dict:
    """
    Fit categorical encoders on train data
    :param x_train:
    :param y_train:
    :return:
    """

    ordinal_encoder_arbitrary = OrdinalEncoder(encoding_method='arbitrary', variables=CAT_VARS_ORDINAL_ARBITARY)
    ordinal_encoder_arbitrary.fit(x_train, y_train)

    onehot_encoder = OneHotEncoder(variables=CAT_VARS_ONEHOT)
    onehot_encoder.fit(x_train)

    cat_encoders = {'ordinal_encoder': ordinal_encoder_arbitrary, 'onehot_encoder': onehot_encoder}

    return cat_encoders

def transform_categorical_encoders(x_to_encode: pd.DataFrame, cat_encoders: dict) -> pd.DataFrame:
    """
    Use pre-fitted categorical encoders to transform data
    :param x_to_encode:
    :param cat_encoders:
    :return:
    """

    for encoder in cat_encoders.values():
        x_to_encode = encoder.transform(x_to_encode)

    return x_to_encode

def fit_numerical_transformers(x_train: pd.DataFrame) -> dict:
    """
    Fit numerical transformers on train data
    :param x_train:
    :return:
    """

    yeo_transformer = YeoJohnsonTransformer(variables=NUM_VARS_YEO_YOHNSON)
    yeo_transformer.fit(x_train)

    num_transformers = {'yeo_transformer': yeo_transformer}

    return num_transformers

def transform_numerical_transformers(x_to_transform: pd.DataFrame, num_transformers: dict) -> pd.DataFrame:
    """
    Use pre-defined numerical transfomers to transform data
    :param x_to_transform:
    :param num_transformers:
    :return:
    """

    for transformer in num_transformers.values():
        x_to_transform = transformer.trasform(x_to_transform)

    return x_to_transform

def fit_target_encoder(y_train: pd.Series):
    """
    Fit on encoder for the target variable
    :param y_train:
    :return:
    """

    le = LabelEncoder()
    le.fit(y_train)

    return le

def transform_target_encoder(encoder, y_to_transform: pd.Series) -> pd.Series:
    """
    Use a pre-defined encoder to transform a Series
    :param encoder:
    :param y_to_transform:
    :return:
    """

    y_to_transform = encoder.transform(y_to_transform)

    return y_to_transform

def fit_data_scaler(x_train: pd.DataFrame):
    """
    Fit a scaler to normalize data
    :param x_train:
    :return:
    """

    min_max_scaler = MinMaxScaler()
    min_max_scaler.fit(x_train)

    return min_max_scaler


def transform_data_scaler(scaler, x_to_transform: pd.DataFrame) -> pd.DataFrame:
    """
    Use a are-fitted scaler to normalize data
    :param scaler:
    :param x_to_transform:
    :return:
    """

    x_to_transform = pd.DataFrame(scaler.transform(x_to_transform), columns=x_to_transform.columns)

    return x_to_transform

def oversample_data(x_train: pd.DataFrame, y_train:pd.Series):
    """
    Create artifical rows so that both classes have equal observations
    :param x_train:
    :param y_train:
    :return:
    """

    x_train, y_train = SMOTE(random_state=RANDOM_STATE).fit_resample(x_train, y_train)

    return x_train, y_train

def get_preprocess_data(x_train, x_test, y_train, y_test):

    x_train = replace_empty_in_col(x_train)
    x_test = replace_empty_in_col(x_test)

    cat_encoders = fit_categorical_encoders(x_train, y_train)
    x_train = transform_categorical_encoders(x_train, cat_encoders)
    x_test = transform_categorical_encoders(x_test, cat_encoders)

    num_transformers = fit_numerical_transformers(x_train)
    x_train = transform_numerical_transformers(x_train, num_transformers)
    x_test = transform_numerical_transformers(x_test, num_transformers)

    target_encoder = fit_target_encoder(y_train)
    y_train = transform_target_encoder(target_encoder, y_train)
    y_test = transform_target_encoder(target_encoder, y_test)

    scaler = fit_data_scaler(x_train)
    x_train = transform_data_scaler(scaler, x_train)
    x_test = transform_data_scaler(scaler, x_test)

    x_train, y_train = oversample_data(x_train, y_train)

    return x_train, x_test, y_train, y_test

def preprocess_data(data_files):
    """
    pipeline of all preprocessing functions
    :param data_files:
    :return:
    """

    required_keys = [
        'raw_x_train_file',
        'raw_x_test_file',
        'raw_y_train_file',
        'raw_y_test_file',
        'transformed_x_train_file',
        'transformed_x_test_file',
        'transformed_y_train_file',
        'transformed_y_test_file'
    ]

    check_keys(data_files, required_keys)

    x_train = pd.read_csv(data_files['raw_x_train_file'])
    x_test = pd.read_csv(data_files['raw_x_test_file'])
    y_train = pd.read_csv(data_files['raw_y_train_file'])
    y_test = pd.read_csv(data_files['raw_y_test_file'])

    x_train, x_test, y_train, y_test = get_preprocess_data(x_train, x_test, y_train, y_test)

    x_train.to_csv(data_files['transformed_x_train_file'], index=False)
    x_test.to_csv(data_files['transformed_x_test_file'], index=False)
    pd.DataFrame(y_train).to_csv(data_files['transformed_y_train_file'], index=False)
    pd.DataFrame(y_test).to_csv(data_files['transformed_y_test_file'], index=False)

    logging.Logger("Data were transformed and saved successfully")