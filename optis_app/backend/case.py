import numpy as np

class Case(object):
    """
    A class representing a single Case from the process 

    ....

    Attributes
    ----------
    case_id : int
        unique case-id
    state : numpy.ndarray
        shows the trace of the case - which activities have been already done
    current : int 
        shows the current activity being executed in the case
    agent : bool
        flag showing if a RL-agent is currently controlling the case
    standard_order: bool 
        flag showing whether the order is standard or custom
    """

    def __init__(self, case):
        """
        Parameters
        ----------
        case : int
            case-id of the case
        """
        
        self.case_id = case
        self.state = np.zeros(15, dtype = int)
        self.current = 0
        self.agent = False 
        self.standard_order = True
