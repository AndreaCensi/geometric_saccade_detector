__version__ = '1.1'

from contracts import contract
import numpy as np

import logging
logging.basicConfig()
logger = logging.getLogger("geo_sac_detect")
logger.setLevel(logging.DEBUG)


from .well_formed_saccade import *
from .structures import *
from .math_utils import * 
from .well_formed_saccade import *
