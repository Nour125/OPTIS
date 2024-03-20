import simpy
import random

from case import Case


class BusinessProcess(object):
    """ 
    A class used to represent a Business Process

    ....

    Attributes
    ----------
    env : simpy.Environment
        an environment for the simulation of the process
    system = simpy.Resource
        the number of the resources of this type the process has
    order_taker : simpy.Resource
        the number of the resources of this type the process has
    stock_handler_a : simpy.Resource
        the number of the resources of this type the process has
    stock_handler_b : simpy.Resource
        the number of the resources of this type the process has
    stock_handler_c : simpy.Resource
        the number of the resources of this type the process has
    manufacturer_a : simpy.Resource
        the number of the resources of this type the process has
    manufacturer_b : simpy.Resource
        the number of the resources of this type the process has
    packer_a : simpy.Resource
        the number of the resources of this type the process has
    packer_b : simpy.Resource
        the number of the resources of this type the process has
    packer_c : simpy.Resource
        the number of the resources of this type the process has
    delivery_service_a : simpy.Resource
        the number of the resources of this type the process has
    delivery_service_b : simpy.Resource
        the number of the resources of this type the process has
    delivery_service_c : simpy.Resource
        the number of the resources of this type the process has
    active_cases : list of int
        a list containing the case-ids of all the currently active cases
    case_objects = list of case.Case
        a list containing all the case objects created in the process
    flag : bool
        indicates whether the process is currently controlled by a RL-agent
    case_id : int
        if a RL-agent controls the process, this varable saves the case-id of the currently controlled case
    next : int
        if a RL-agent controls the process, this varaiable saves what the next action the agent chose is
    done_cases : set of case.Case
        if a RL-agent controls the process, this set saves all the done cases of the agent
    event_log_flag : bool
        if we're using the process to generate an event log by simulating it, this flag is set to true 
    event_log : dict of {int : dict of {str : int}, dict of {str : str}, dict of {str: float}, dict of {str, float}}
        if the event_log_flag is set to true, we save the events of the process to this variable,
        an event includes it's case-id, activity, start timestamp and end timestamp 
    event_counter : int
        a counter for the number of events which happened (useful when adding a new event to the event_log)

    Methods
    -------
    place_order()
        executes the activity by yielding a timeout with a certain duration
    arrange_standard_order()
        executes the activity by yielding a timeout with a certain duration
    arrange_custom_order()
        executes the activity by yielding a timeout with a certain duration
    pick_from_stock_a()
        executes the activity by yielding a timeout with a certain duration
    pick_from_stock_b()
        executes the activity by yielding a timeout with a certain duration
    pick_from_stock_c()
        executes the activity by yielding a timeout with a certain duration
    manufacture_a()
        executes the activity by yielding a timeout with a certain duration
    manufacture_b()
        executes the activity by yielding a timeout with a certain duration
    pack_a()
        executes the activity by yielding a timeout with a certain duration
    pack_b()
        executes the activity by yielding a timeout with a certain duration
    pack_c()
        executes the activity by yielding a timeout with a certain duration
    attempt_delivery_a()
        executes the activity by yielding a timeout with a certain duration
    attempt_delivery_b()
        executes the activity by yielding a timeout with a certain duration
    attempt_delivery_c()
        executes the activity by yielding a timeout with a certain duration
    order_completed()
        executes the activity by yielding a timeout with a certain duration
    is_valid(event, action, case_obj)
        checks whether the next action after a certain event in a case is valid 
    """

    def __init__(self, env, ressources):
        """
        Parameters
        ----------
        env : simpy.Environment
            An environment for the simulation of the process
        ressources : list of int
            A list storing the number of the different resources available (13 types of resources)
        """

        # initialize simulation environment
        self.env = env

        # initialize ressources
        self.system = simpy.Resource(env, ressources[0] - 1)
        self.order_taker = simpy.Resource(env, ressources[1] - 1)
        self.stock_handler_a = simpy.Resource(env, ressources[2] - 1)
        self.stock_handler_b = simpy.Resource(env, ressources[3] - 1)
        self.stock_handler_c = simpy.Resource(env, ressources[4] - 1)
        self.manufacturer_a = simpy.Resource(env, ressources[5] - 1)
        self.manufacturer_b = simpy.Resource(env, ressources[6] - 1)
        self.packer_a = simpy.Resource(env, ressources[7] - 1)
        self.packer_b = simpy.Resource(env, ressources[8] - 1)
        self.packer_c = simpy.Resource(env, ressources[9] - 1)
        # capacity of each delivery service instead of numbers of workers
        self.delivery_service_a = simpy.Resource(env, ressources[10] - 1)
        self.delivery_service_b = simpy.Resource(env, ressources[11] - 1)
        self.delivery_service_c = simpy.Resource(env, ressources[12] - 1)
    
        # initialize lists with active cases and all case objects
        # we decided that at the start of the process there are already 3 cases waiting 
        self.active_cases = [0, 1, 2] # saves case_ids
        case_0 = Case(0)
        case_1 = Case(1)
        case_2 = Case(2)
        self.case_objects = [case_0, case_1, case_2] # saves case objects

        # flag indicates whether the process is currently controlled by the agent and we set it on false every time the agent does an activity
        self.flag = True

        # if the agent controls a case, this varable saves the case_id of the controlled case
        self.case_id = None

        # if the agent controls a case, this varaiable saves what the next action the agent chose is
        self.next = 0

        # initialize set containg all the done cases of the agent
        self.done_cases = set([])

        # if we're using the simmodel to generate an event log this flag is set to true 
        self.event_log_flag = False

        # if the event_log_flag is true we save the events to this variable
        self.event_log = []

        # a counter for the number of events which happened (useful for the event log generator)
        self.event_counter = 0

    def place_order(self):
        """Executes the activity "place order" by yielding a timeout of 2 time units. 
        """
        yield self.env.timeout(2)

    def arrange_standard_order(self):
        """Executes the activity "arrange standard order" by yielding a timeout in the interval of 10 to 15 time units.
        """
        yield self.env.timeout(random.randint(10, 15))
    
    def arrange_custom_order(self):
        """Executes the activity "arrange custom order" by yielding a timeout in the interval of 20 to 30 time units.
        """
        yield self.env.timeout(random.randint(20, 30))
    
    def pick_from_stock_a(self):
        """Executes the activity "pick from stock A" by yielding a timeout in the interval of 10 to 40 time units.
        """
        yield self.env.timeout(random.randint(10, 40))
    
    def pick_from_stock_b(self):
        """Executes the activity "pick from stock B" by yielding a timeout in the interval of 20 to 60 time units.
        """
        yield self.env.timeout(random.randint(20, 60))

    def pick_from_stock_c(self):
        """Executes the activity "pick from stock C" by yielding a timeout in the interval of 30 to 80 time units.
        """
        yield self.env.timeout(random.randint(30, 80))
    
    def manufacture_a(self):
        """Executes the activity "manufacture A" by yielding a timeout in the interval of 240 to 360 time units.
        """
        yield self.env.timeout(random.randint(240, 360))
    
    def manufacture_b(self):
        """Executes the activity "manufacture B" by yielding a timeout in the interval of 360 to 480 time units.
        """
        yield self.env.timeout(random.randint(360, 480))
    
    def pack_a(self):
        """Executes the activity "pack A" by yielding a timeout in the interval of 10 to 20 time units.
        """
        yield self.env.timeout(random.randint(10, 20))
    
    def pack_b(self):
        """Executes the activity "pack B" by yielding a timeout in the interval of 15 to 30 time units.
        """
        yield self.env.timeout(random.randint(15, 30))
    
    def pack_c(self):
        """Executes the activity "pack C" by yielding a timeout in the interval of 25 to 50 time units.
        """
        yield self.env.timeout(random.randint(25, 50))
    
    def attempt_delivery_a(self):
        """Executes the activity "attempt delivery A" by yielding a timeout in the interval of 720 to 1440 time units.
        """
        yield self.env.timeout(random.randint(720, 1440))
    
    def attempt_delivery_b(self):
        """Executes the activity "attempt delivery B" by yielding a timeout in the interval of 1440 to 2160 time units.
        """
        yield self.env.timeout(random.randint(1440, 2160))

    def attempt_delivery_c(self):
        """Executes the activity "attempt delivery C" by yielding a timeout in the interval of 1440 to 2880 time units.
        """
        yield self.env.timeout(random.randint(1440, 2880))
    
    def order_completed(self):
        """Executes the activity "order completed" by yielding a timeout of 1 time unit.
        """
        yield self.env.timeout(1)

    def is_valid(self, event, action, case_obj):
        """Checks whether the next action after a certain event in a case is valid based on the predefined process flow. 

        Parameters
        ----------
        event : int
            the current event of the case
        action : int
            an encoded activity
        case_obj: case.Case
            the case for which we're doing the check
        
        Returns
        -------
        bool
            whether the action is valid or not
        """

        if event == 0 and action == 1:
            return True
        elif event == 1 and (action == 2 or action == 3):
            return True
        elif event == 2 and case_obj.standard_order and (action == 4 or action == 5 or action == 6):
            return True
        elif event == 3 and (not case_obj.standard_order) and (action == 7 or action == 8):
            return True
        elif (4 <= event <= 8) and (action == 9 or action == 10 or action == 11):
            return True
        elif (9 <= event <= 11) and (12 <= action <=14):
            return True
        elif (12 <= event <=14) and action == 15:
            return True
        else:
            return False
    