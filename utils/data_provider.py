import pandas as pd
import numpy as np


def split_dataset(configs):
    # Loading
    df_all = pd.read_csv(configs['data_location'])

    # Make dataset implicit (ie User had interaction/User did not have interaction)
    df_all = df_all[df_all['rating'] >= configs['implicit_rating']]
    df_all.loc[df_all['rating'] >= configs['implicit_rating'], 'rating'] = 1

    if configs['minimum_user_interaction'] != -1:
        users_interactions_counts = df_all.groupby(['userId']).count()
        # For each interaction, check whether the userId occurred more than MINIMUM_MOVIE_INTERACTION times
        df_all = df_all.loc[df_all['userId'].isin(users_interactions_counts[users_interactions_counts['timestamp'] >=
                                                                            configs['minimum_user_interaction']].index)]

    # Sorting is done so that the model does not have access to future interactions
    df_sorted_by_timestamp = df_all.sort_values(by=['timestamp'])

    validation_size = int(len(df_sorted_by_timestamp) * configs['validation_set_size'])
    test_size = int(len(df_sorted_by_timestamp) * configs['test_set_size'])

    validation_indexes_start = len(df_sorted_by_timestamp) - (validation_size + test_size)
    test_indexes_start = validation_indexes_start + validation_size

    df_train, df_val, df_test = np.split(df_sorted_by_timestamp, [validation_indexes_start, test_indexes_start])

    # Remove any movies that do not appear in the training set from the test set
    df_test = df_test.loc[df_test['movieId'].isin(df_train['movieId'].unique())]

    # Remove any movies that do not appear in the training set from the validation set
    df_val = df_val.loc[df_val['movieId'].isin(df_train['movieId'].unique())]

    return df_train, df_val, df_test
