import logging
import pandas as pd
from sumoutils import parquet_handler

class ViewingImporter(object):
    
    def __init__(self, config):
        self.config = config


    def read(self, viewingPath, aggColumn, testing):
        
        if testing == True:
            sessions = pd.read_csv("test_data/viewing.csv")
            return sessions
        
        """ Read sessions """
        pqh = parquet_handler.ParquetHandler(
            bucket = self.config.GOOGLE_CLOUD_STORAGE_BUCKET_READ,
            cloud_prefix = '{}/{}'.format(self.config.GS_READ_PREFIX, viewingPath),
            local_prefix = self.config.DATA_DIR
        )
        
        # filter blobs on date 
        blobs = pqh.list_blobs()

        # download relevant blobs
        parquet_files = pqh.parquet_download(blobs)

        sessions = pd.DataFrame()
        if not len(parquet_files) > 0:
            logging.error("No parquet files found")
        else:
            logging.info("Successfully downloaded {} files from Storage".format(len(parquet_files)))
            sessions = pqh.parquet_read(
                parquet_files, cols=['profileId', aggColumn, 'sumDurationSec']
            )

        sessions.rename(columns={'sumDurationSec': 'playingTime', aggColumn: 'aggColumn'}, inplace=True)



        return sessions
