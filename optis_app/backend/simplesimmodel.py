"""
Simulation Model for a Simple Business Process

This module contains the following functions related to the simulation of a business process:
    
    * map_activity_to_number(activity), map_number_to_activity(number) - the encoding of the activities of the process
    * execute_case(env, case, process) - the process flow of a case in the process
    * run_process(env, process) - the process flow of the whole process
    * get_ressources(process), get_current_state - functions to get relevant state information about the process and the cases in it
"""

import random

from case import Case
import eventlog as log


def map_activity_to_number(activity):
    """ Gets an activity name and returns the corresponding number in the mapping.

    Parameters
    ----------
    activity : str
        name of the activity

    Returns
    -------
    int
        number of the activity
    """

    activity_mapping = {
        'place order': 1,
        'arrange standard order': 2,
        'arrange custom order': 3,
        'pick from stock A': 4, 
        'pick from stock B': 5, 
        'pick from stock C': 6, 
        'manufacture A': 7, 
        'manufacture B': 8, 
        'pack A': 9,
        'pack B': 10,
        'pack C': 11,
        'attempt delivery A': 12,
        'attempt delivery B': 13,
        'attempt delivery C': 14,
        'order completed': 15,
    }

    return activity_mapping[activity]
    
def map_number_to_activity(number):
    """ Gets a number and returns the corresponding activity name in the mapping.

    Parameters
    ----------
    number : int
        number of the activity

    Returns
    -------
    str
        name of the activity
    """

    number_mapping = {
        1: 'place order',
        2: 'arrange standard order',
        3: 'arrange custom order',
        4: 'pick from stock A', 
        5: 'pick from stock B', 
        6: 'pick from stock C', 
        7: 'manufacture A', 
        8: 'manufacture B', 
        9: 'pack A',
        10: 'pack B',
        11: 'pack C',
        12: 'attempt delivery A',
        13: 'attempt delivery B',
        14: 'attempt delivery C',
        15: 'order completed',
    }

    return number_mapping[number]

def execute_case(env, case, process):
    """ A function, which represents the process model with it's control flow and ressource allocation.
    A customer places an order at the system and then is redirected to the order takers, where it's arranged 
    what type of order the customer wants - standard or custom. After that depending on whether the order 
    is standard or custom, respectively a stock or manufacturer is chosen. 
    Afterwards one of three packing options is chosen and executed. 
    Following the packing one of the three delivery services deliver the order. 
    With that the order is completed.

    Parameters
    ----------
    env : simpy.Environment
        environment for the simulation 
    case : int
        case-id of the case which is being executed
    process : businessprocess.BusinessProcess
        the process to which the case belongs
    """

    # create a case object to keep track of case attributes if not already existing
    if case >= len(process.case_objects):
        case_obj = Case(case)

        # add the case to the process's active cases list
        process.case_objects.append(case_obj)
        process.active_cases.append(case) 
    
    # if the case is one of the first three choose it from the list
    if len(process.case_objects) <= 3:
        case_obj = process.case_objects[case]

    # if case chosen by agent set agent flag to true
    if process.case_id == case: 
        case_obj.agent = True

    # place order
    # update the state of the case
    case_obj.state[0] += 1
    case_obj.current = 1
    # request resource
    with process.system.request() as request:
        yield request
        # if the event_log_flag is set add the event to the log
        if process.event_log_flag:
            event_counter = process.event_counter
            start = env.now
            log.add_start_event(process, event_counter, case, "place order", start)

        yield env.process(process.place_order()) # do the activity

        if process.event_log_flag: 
            duration = env.now - start
            log.add_end_event(process, event_counter, duration)


    # if the last action was made from the agent set the process flag to be able to return to the environment's step function
    if case_obj.agent: 
        process.flag = False

    with process.system.request() as request:
        yield request

    # before a new action is executed check if the agent is controlling the case and set the flag to true if yes
    if process.case_id == case: case_obj.agent = True 

    # standard order XOR custom order
    # if the simmodel is running independently for this case choose the next action randomly, if the agent is controlling the case choose the agent's action
    choice = random.randint(2,3) if not case_obj.agent else process.next 
    if choice == 2:
        # set the standard_order flag
        case_obj.standard_order = True
        # exactly the same as for palce order
        case_obj.state[1] += 1
        case_obj.current = 2
        with process.order_taker.request() as request:
            yield request
            if process.event_log_flag:
                event_counter = process.event_counter
                start = env.now
                log.add_start_event(process, event_counter, case, "arrange standard order", env.now)
            yield env.process(process.arrange_standard_order())
            if process.event_log_flag: 
                duration = env.now - start
                log.add_end_event(process, event_counter, duration)
            if case_obj.agent: 
                process.flag = False
            with process.system.request() as request:
                    yield request
    else:
        # analog
        case_obj.state[2] += 1
        case_obj.current = 3
        case_obj.standard_order = False
        with process.order_taker.request() as request:
            yield request
            if process.event_log_flag:
                event_counter = process.event_counter
                start = env.now
                log.add_start_event(process, event_counter, case, "arrange custom order", env.now)
            yield env.process(process.arrange_custom_order())
            if process.event_log_flag:
                duration = env.now - start 
                log.add_end_event(process, event_counter, duration)
            if case_obj.agent: 
                process.flag = False
            with process.system.request() as request:
                    yield request


    if process.case_id == case: case_obj.agent = True 

    # exactly the same but we choose different activities for standard and custom order based on the flag
    if case_obj.standard_order and (not case_obj.agent):
        choice = random.randint(4,6)
    elif (not case_obj.standard_order) and (not case_obj.agent):
        choice = random.randint(7,8)
    else:
        choice = process.next

    # the rest of the function is pretty much the same for each new action
     
    # choose stock or manufacturer
    if choice == 4:
        case_obj.state[3] += 1
        case_obj.current = 4
        with process.stock_handler_a.request() as request:
            yield request
            if process.event_log_flag:
                event_counter = process.event_counter
                start = env.now
                log.add_start_event(process, event_counter, case, "pick from stock A", env.now)
            yield env.process(process.pick_from_stock_a())
            if process.event_log_flag: 
                duration = env.now - start
                log.add_end_event(process, event_counter, duration)
            if case_obj.agent: 
                process.flag = False
            with process.system.request() as request:
                yield request
    elif choice == 5:
        case_obj.state[4] += 1
        case_obj.current = 5
        with process.stock_handler_b.request() as request:
            yield request
            if process.event_log_flag:
                event_counter = process.event_counter
                start = env.now
                log.add_start_event(process, event_counter, case, "pick from stock B", env.now)
            yield env.process(process.pick_from_stock_b())
            if process.event_log_flag: 
                duration = env.now - start
                log.add_end_event(process, event_counter, duration)
            if case_obj.agent: 
                process.flag = False
            with process.system.request() as request:
                yield request
    elif choice == 6:
        case_obj.state[5] += 1
        case_obj.current = 6
        with process.stock_handler_c.request() as request:
            yield request
            if process.event_log_flag:
                event_counter = process.event_counter
                start = env.now
                log.add_start_event(process, event_counter, case, "pick from stock C", env.now)
            yield env.process(process.pick_from_stock_c())
            if process.event_log_flag: 
                duration = env.now - start
                log.add_end_event(process, event_counter, duration)
            if case_obj.agent: 
                process.flag = False
            with process.system.request() as request:
                yield request
    elif choice == 7:
        case_obj.state[6] += 1
        case_obj.current = 7
        with process.manufacturer_a.request() as request:
            yield request
            if process.event_log_flag:
                event_counter = process.event_counter
                start = env.now
                log.add_start_event(process, event_counter, case, "manufacture A", env.now)
            yield env.process(process.manufacture_a())
            if process.event_log_flag: 
                duration = env.now - start
                log.add_end_event(process, event_counter, duration)
            if case_obj.agent: 
                process.flag = False
            with process.system.request() as request:
                yield request
    else:
        case_obj.state[7] += 1
        case_obj.current = 8
        with process.manufacturer_b.request() as request:
            yield request
            if process.event_log_flag:
                event_counter = process.event_counter
                start = env.now
                log.add_start_event(process, event_counter, case, "manufacture B", env.now)
            yield env.process(process.manufacture_b())
            if process.event_log_flag: 
                duration = env.now - start
                log.add_end_event(process, event_counter, duration)
            if case_obj.agent: 
                process.flag = False
            with process.system.request() as request:
                yield request


    if process.case_id == case: case_obj.agent = True 

    choice = random.randint(9,11) if not case_obj.agent else process.next

    if choice == 9:
        case_obj.state[8] += 1
        case_obj.current = 9
        with process.packer_a.request() as request:
            yield request
            if process.event_log_flag:
                event_counter = process.event_counter
                start = env.now
                log.add_start_event(process, event_counter, case, "pack A", env.now)
            yield env.process(process.pack_a())
            if process.event_log_flag: 
                duration = env.now - start
                log.add_end_event(process, event_counter, duration)
            if case_obj.agent: 
                process.flag = False
            with process.system.request() as request:
                yield request
    elif choice == 10:
        case_obj.state[9] += 1
        case_obj.current = 10
        with process.packer_b.request() as request:
            yield request
            if process.event_log_flag:
                event_counter = process.event_counter
                start = env.now
                log.add_start_event(process, event_counter, case, "pack B", env.now)
            yield env.process(process.pack_b())
            if process.event_log_flag: 
                log.add_end_event(process, event_counter, duration)
            if case_obj.agent: 
                process.flag = False

            with process.system.request() as request:
                yield request
    else:
        case_obj.state[10] += 1
        case_obj.current = 11
        with process.packer_c.request() as request:
            yield request
            if process.event_log_flag:
                event_counter = process.event_counter
                start = env.now
                log.add_start_event(process, event_counter, case, "pack C", env.now)
            yield env.process(process.pack_c())
            if process.event_log_flag: 
                duration = env.now - start
                log.add_end_event(process, event_counter, duration)
            if case_obj.agent: 
                process.flag = False
            with process.system.request() as request:
                yield request

    if process.case_id == case: case_obj.agent = True 

    # choose delivery
    choice = random.randint(12,14) if not case_obj.agent else process.next
    if choice == 12:
        case_obj.state[11] += 1
        case_obj.current = 12
        with process.delivery_service_a.request() as request:
            yield request
            if process.event_log_flag:
                event_counter = process.event_counter
                start = env.now
                log.add_start_event(process, event_counter, case, "attempt delivery A", env.now)
            yield env.process(process.attempt_delivery_a())
            if process.event_log_flag: 
                duration = env.now - start
                log.add_end_event(process, event_counter, duration)
            if case_obj.agent: 
                process.flag = False
            with process.system.request() as request:
                yield request
    elif choice == 13:
        case_obj.state[12] += 1
        case_obj.current = 13
        with process.delivery_service_b.request() as request:
            yield request
            if process.event_log_flag:
                event_counter = process.event_counter
                start = env.now
                log.add_start_event(process, event_counter, case, "attempt delivery B", env.now)
            yield env.process(process.attempt_delivery_b())
            if process.event_log_flag: 
                duration = env.now - start
                log.add_end_event(process, event_counter, duration)
            if case_obj.agent: 
                process.flag = False
            with process.system.request() as request:
                yield request
    else: 
        case_obj.state[13] += 1
        case_obj.current = 14
        with process.delivery_service_c.request() as request:
            yield request
            if process.event_log_flag:
                event_counter = process.event_counter
                start = env.now
                log.add_start_event(process, event_counter, case, "attempt delivery C", env.now)
            yield env.process(process.attempt_delivery_c())
            if process.event_log_flag: 
                duration = env.now - start
                log.add_end_event(process, event_counter, duration)
            if case_obj.agent: 
                process.flag = False
            with process.system.request() as request:
                yield request
    

    if process.case_id == case: case_obj.agent = True 

    # case completed
    case_obj.state[14] += 1
    case_obj.current = 15
    with process.system.request() as request:
        yield request
        if process.event_log_flag:
            event_counter = process.event_counter
            start = env.now
            log.add_start_event(process, event_counter, case, "order completed", env.now)
        yield env.process(process.order_completed())
        if process.event_log_flag: 
            duration = env.now - start
            log.add_end_event(process, event_counter, duration)


    # remove the case from the active cases since it's now done
    if case in process.active_cases:
        process.active_cases.remove(case)
    
    # if the case was controlled by the agent:
    if case_obj.agent: 
        for i in process.case_objects:
            # remove the cases which are currently doing the last activity from the active cases list to ensure the agent chooses only cases for which there are still next actions to be done
            if (i.current == 15) and (i.case_id in process.active_cases) and (i.case_id != case):
                process.active_cases.remove(i.case_id)
        # add the case to the done cases
        process.done_cases.add(process.case_id)
        process.flag = False 
    
def run_process(env, process):
    """ Runs a new process by generating new cases and executing them.

    Parameters
    ----------
    env : simpy.Environment
        environment for the simulation
    process : businessprocess.BusinessProcess
        the process which is being simulated
    """
    
    # the waiting orders
    for case in range(3):
        env.process(execute_case(env, case, process))

    # the new incoming orders
    while True:
        # allow only 300 active cases at a time
        while(len(process.active_cases) > 300):
            yield env.timeout(1)

        waittime = random.randint(10,15)
        if case % 20 == 0:
            waittime = 100
        yield env.timeout(waittime)  # Wait a bit before generating a new case

        case += 1
        env.process(execute_case(env, case, process))

def get_ressources(process):
    """ Get the numbers of the currently available resources.

    Parameters
    ----------
    process : businessprocess.BusinessProcess
        the process to which the case belongs  

    Returns
    -------
    list of int
        available ressouces
    """

    process_state = []

    # calculate the availbale resources for each resource in the process
    num_system = process.system.capacity - process.system.count
    process_state.append(num_system)

    num_order_taker = process.order_taker.capacity - process.order_taker.count 
    process_state.append(num_order_taker)

    num_stock_handler_a = process.stock_handler_a.capacity - process.stock_handler_a.count 
    process_state.append(num_stock_handler_a)

    num_stock_handler_b = process.stock_handler_b.capacity - process.stock_handler_b.count 
    process_state.append(num_stock_handler_b)

    num_stock_handler_c = process.stock_handler_c.capacity - process.stock_handler_c.count 
    process_state.append(num_stock_handler_c)

    num_manufacturer_a = process.manufacturer_a.capacity - process.manufacturer_a.count 
    process_state.append(num_manufacturer_a)

    num_manufacturer_b = process.manufacturer_b.capacity - process.manufacturer_b.count 
    process_state.append(num_manufacturer_b)

    num_packer_a = process.packer_a.capacity - process.packer_a.count 
    process_state.append(num_packer_a)

    num_packer_b = process.packer_b.capacity - process.packer_b.count 
    process_state.append(num_packer_b)

    num_packer_c = process.packer_c.capacity - process.packer_c.count 
    process_state.append(num_packer_c)

    num_delivery_service_a = process.delivery_service_a.capacity - process.delivery_service_a.count 
    process_state.append(num_delivery_service_a)

    num_delivery_service_b = process.delivery_service_b.capacity - process.delivery_service_b.count
    process_state.append(num_delivery_service_b) 

    num_delivery_service_c = process.delivery_service_c.capacity - process.delivery_service_c.count 
    process_state.append(num_delivery_service_c)

    return process_state

def get_current_state(process, case):
    """ Get the current state of the process and a specific case.

    Parameters
    ----------
    process : businessprocess.BusinessProcess
        the process to which the case belongs
    case : int
        case-id of the case which is being executed

    Returns
    -------
    list of int
        available ressouces
    list of int
        events which already happened in the case
    int
        current event of the case
    """

    process_state = get_ressources(process)

    # the state of the case chosen
    cur_case = case.state

    # the current event of the case chosen
    event  = case.current

    return process_state, cur_case, event
