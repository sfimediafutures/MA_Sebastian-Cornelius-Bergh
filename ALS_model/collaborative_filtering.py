import logging
import uuid

import numpy as np
import pandas as pd

from scipy.sparse import coo_matrix
from implicit_train import Implicit


USERS_MIN = 2
ITEMS_MIN = 2

class CollaborativeFiltering(object):
    
    def __init__(self, config):
        self.config = config

    def run(self, job_id, sessions):

        params = self.config.jobs['jobs'][job_id]['params']
        params['use_gpu'] = self.config.USE_GPU
        lib = params['library']
        alg = params['algorithm']

        # Calculate user-item matrix

        uim = self.uim(sessions)
        logging.info("UIM of shape {}".format(uim.shape))
        

        # Items dictonary mapping idx to ids 
        # {0: 'fotball', 1: 'håndball', 2: 'ishockey'}
        items = dict(enumerate(sessions['aggColumn'].cat.categories))
        logging.info("Items of length {}".format(len(items)))
        
        # Users dictonary mapping idx to ids
        # {0: 'userId1', 1: 'userId2', 2: 'userId3'}
        users = dict(enumerate(sessions['profileId'].cat.categories))
        logging.info("Users of length {}".format(len(users)))

        if len(uim.shape) != 2:
            raise ValueError("invalid model uim")
        
        if len(items) != uim.shape[1]:
            raise ValueError("invalid model. length of items and shape uim differ")

        if len(users) != uim.shape[0]:
            raise ValueError("invalid model. length of users and shape of uim differ")

        # Just removed while testing code
        if len(items) < ITEMS_MIN:
            raise ValueError("insufficent items for building model")

        if len(users) < USERS_MIN:
            raise ValueError("insufficent users for building model")
        
        # Model to return
        model = None
        
        # Train model
        logging.info("Fitting model {}" \
                     .format(params))

        if lib == 'implicit':
            model = Implicit(uim, **params)
            
        model = model.fit()

        if hasattr(model, "no_components"):
            n_factors = model.no_components
        elif hasattr(model, "factors"):
            n_factors = model.factors
        else:
            raise ValueError("invalid model")

        if model.user_factors.shape[0] != len(users):
            raise ValueError("invalid model; {} vs {}".format(model.user_factors.shape[0], len(users)))
        if model.item_factors.shape[0] != len(items):
            raise ValueError("invalid model; {} vs {}".format(model.item_factors.shape[0], len(items)))
        if model.item_factors.shape[1] != model.user_factors.shape[1]:
            raise ValueError("invalid model; {} vs {}".format(model.item_factors.shape[1], model.user_factors.shape[1]))

        logging.info("Model {} trained successfully with {} factors, {} items, {} users".format(
            job_id, n_factors, len(items), len(users),
        ))
                     
        experiment_id = '{id}-{lib}-{alg}-{factors}fct-{iterations}it-{reg}reg-{b}b-{k}k'.format(
            id=job_id, lib=lib, alg=alg, factors=n_factors, iterations=params['iterations'],
            reg=params['regularization'], b=params['b'], k=params['k1']
        )

        # unqiue id for model
        model_id = str(uuid.uuid4())
        
        return {
            'model': model,
            'uim': uim,
            'items': items,
            'users': users,
            'experiment_id': experiment_id,
            'model_id': model_id,
        }


    """
    Returns a coo matrix of shape [n_items, n_users]
    """
    def uim(self, sessions):

        print(sessions)

        uim = coo_matrix(
            (sessions['normDuration'].astype(np.float32),
             (sessions['profileId'].cat.codes,
              sessions['aggColumn'].cat.codes))
        )


        return uim