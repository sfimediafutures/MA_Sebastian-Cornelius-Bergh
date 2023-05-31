import pandas as pd
import numpy as np
import logging
import datetime
from sklearn import preprocessing


class DataTransformer(object):
    
    def __init__(self,viewing):
        self.viewing = viewing
        
    def transform(self): 

        self.viewing.dropna(inplace=True)

        self.ceiling(360000)\

        self.scale().clean().to_category()


        if not self.viewing.empty:
            logging.info("")
        else:
            logging.warn("Empty sessions dataframe for job")

        return self.viewing


    def scale(self):
        """ Scale the duration of each users watch time """

        min_max_scaler = preprocessing.MinMaxScaler()
        x = np.array(self.viewing["playingTime"]).reshape(-1,1)
        x_scaled = min_max_scaler.fit_transform(x)
        self.viewing["normDuration"] = x_scaled
        self.viewing.drop(["playingTime"], axis=1,inplace=True)

        return self


    def clean(self):
        """ Filter out rows with empty keys """

        invalid_rows = (self.viewing['profileId'].str.len() == 0) | \
            (self.viewing['aggColumn'].str.len() == 0)

        if invalid_rows.sum() == 0:
            return self
        
        logging.warning("rows with invalid keys: {}".format(invalid_rows.sum()))
        
        self.viewing = self.viewing[~invalid_rows]
        return self

    def to_category(self):
        """ As type Category """

        self.viewing['profileId'] = self.viewing['profileId'].astype("category")
        self.viewing['aggColumn'] = self.viewing['aggColumn'].astype("category")
        return self

    
    def ceiling(self, max_score):
        """ Set score ceiling """

        mask = self.viewing['playingTime'] > max_score
        self.viewing.loc[mask, 'playingTime'] = max_score
        return self