import logging
import numpy as np

from implicit.als import AlternatingLeastSquares

# There is more to this but i did not include it due to TV 2 privacy

# Først få denne train til å kjøre og evaluere. 
# Hente inn modellen og kjøre den på et testdatasett.  
class Implicit(object):
    def __init__(self, uim, **kwargs):

        self.algorithm = kwargs.get('algorithm', 'als')
        self.factors = kwargs.get('factors', 8)
        self.iterations = kwargs.get('iterations', 30)
        
        self.uim = uim.tocsr()
        self.model = self._model()
        
    def _model(self):

        """ 
        Initate model based on input parameters dictionary
        """

        if self.algorithm == 'als':
            model = AlternatingLeastSquares(
                factors=self.factors,
                dtype=np.float32,
                iterations=self.iterations,
            )

            # Disable building approximate recommend index
            model.approximate_recommend = False

        else:
            raise ValueError("algorithm must be als, lmf or bpr")
            
        return model
