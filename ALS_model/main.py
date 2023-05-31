import pandas as pd
import logging
import gc
import pickle

from import_viewing import ViewingImporter
from transform_data import DataTransformer
from collaborative_filtering import CollaborativeFiltering
from export_pb import ProtoBufExporter

# import config

logging.info("Configuring jobs")
config = config.Config.fromdict(config.defaultEnvVars)
logger = logging.getLogger()
logger.setLevel(level=config.LOGLEVEL)
logHandler = logging.StreamHandler()
logger.addHandler(logHandler)

# Raise an error on settingwithcopywarning
pd.set_option('mode.chained_assignment', 'raise')


for job_id in config.MODEL_IDS:

    # ----------- Import viewing ------------ #

    viewingDataPath = config.jobs['jobs'][job_id]['viewing_data_path']
    aggColumn = config.jobs['jobs'][job_id]['aggColumn']
    logging.info("Importing viewing data for job {}".format(job_id))
    sport_viewing = ViewingImporter(config).read(viewingDataPath, aggColumn, config.TESTING)

    logging.info("Transforming viewing data for job {}".format(job_id))
    sessions = DataTransformer(sport_viewing).transform()


    # ----------- Training model ------------ #

    logging.info("Training model (job {})".format(job_id))
    model = CollaborativeFiltering(config) \
            .run(job_id, sessions)
    

    # ----------- Export model to kafka and GCS ------------ # 

    if config.EXPORT_KAFKA:
        logging.info("Exporting sport model to GCS+Kafka (job {})".format(job_id))
        exporter = ProtoBufExporter(config)
        exporter.run(job_id, model)

    del model
    gc.collect()
 
logging.info("All done!")
