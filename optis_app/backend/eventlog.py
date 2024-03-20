"""Event Log Generator for our simulation model.

The module includes the following functions:

    * add_start_event(process, event_id, case_id, activity, start_timestamp) - add an event to the event log of a process simulation
    * add_end_event(process, event_id, end_timestamp) - add the final timestamp to an event in the event log of a process simulation
    * export_to_csv(process, file_path) - export an event log to .csv
    * export_to_xes(process, file_path) - export an event log to .xes
    * convert_to_dataframe(name) - convert an event log to a pandas dataframe
    * format_check(name) - check if the format of a csv/xes file is the same as the event logs we use in the simulation model
    * get_active_cases(name) - get the case-ids of all the active cases in an event log
    * show_active_cases(name) - get the case-ids and traces of all the active cases in an event log
    * get_state(case_id, name) - get the state of a single case form an event log
    * generate_event_log(time) - generate an event log from a process simulation
"""

import pandas as pd
import numpy as np
from collections import OrderedDict
import simpy
from pm4py.objects.log.obj import EventLog
from pm4py.objects.log.obj import Trace
from pm4py.objects.log.obj import Event
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.importer.xes import importer as xes_importer
import os
import datetime

import simplesimmodel as model
from businessprocess import BusinessProcess


def add_start_event(process, event_id, case_id, activity, start):
    """Add the start of an event to the event log of a process.

    Parameters
    ----------
    event_id : int
        the unique id of the event 
    case_id : int
        the unique case-id of a case 
    activity : str
        the name of the activity
    start : float
        the relative start time of the event
    """

    start_timestamp = current_time + datetime.timedelta(minutes = start)

    process.event_log.append(event_id)
    process.event_log[event_id] = {
        'CaseID': case_id,
        'Activity': activity,
        'StartTimestamp': start_timestamp.strftime('%Y-%m-%d %H:%M'),
        'EndTimestamp': " "
    }
    process.event_counter += 1

def add_end_event(process, event_id, duration):
    """Add the end of an event to the event log of a process.

    Parameters
    ----------
    event_id : int
        the unique id of the event 
    duartion : float
        the complete duration of the event
    """

    event = process.event_log[event_id]
    end_timestamp = current_time + datetime.timedelta(minutes = duration)
    event['EndTimestamp'] = end_timestamp.strftime('%Y-%m-%d %H:%M')

def export_to_csv(process, file_path):
    """Export the event log of a process simulation to .csv.

    Parameters
    ----------
    process : businessprocess.BusinessProcess
        the process which was simulated
    file_path : str
        where the .csv file should be saved
    """

    event_log_df = pd.DataFrame.from_dict(process.event_log)
    event_log_df.to_csv(file_path, index=False)

def export_to_xes(process, file_path):
    """Export the event log of a process simulation to .xes.

    Parameters
    ----------
    process : businessprocess.BusinessProcess
        the process which was simulated
    file_path : str
        where the .xes file should be saved
    """
    
    event_log = process.event_log

    # Create an empty event log object
    event_log_obj = EventLog()

    # Iterate over each event in the event log
    for event_data in event_log:
        # Create a new trace
        trace = Trace()

        # Create a new event
        event = Event()

        # Set the attributes of the event based on the dictionary values
        event['CaseID'] = event_data['CaseID']
        event['Activity'] = event_data['Activity']
        event['StartTimestamp'] = event_data['StartTimestamp']
        event['EndTimestamp'] = event_data['EndTimestamp']

        # Add the event to the trace
        trace.append(event)

        # Add the trace to the event log
        event_log_obj.append(trace)

    # Export the event log to XES format
    xes_exporter.apply(event_log_obj, file_path)

def convert_to_dataframe(name):
    """Convert the event log file of a process simulation to a pandas dataframe.

    Parameters
    ----------
    name : str
        name of the event log file

    Returns
    -------
    pandas.DataFrame
        the converted event log
    """
    
    # file_path = r"Frontend/upload/" + name #docker
    file_path = r"upload/" + name 
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.csv':
        event_log_df = pd.read_csv(file_path)
    elif file_extension == '.xes':
        # Read the XES file
        event_log = xes_importer.apply(file_path)

        column_order = ["CaseID", "Activity", "StartTimestamp", "EndTimestamp"]

        # Extract the event attributes and create a list of dictionaries
        event_data = []
        for trace in event_log:
            for event in trace:
                row = {col: event.get(col, "") for col in column_order}
                event_data.append(row)

        # Create a pandas DataFrame from the event data
        event_log_df = pd.DataFrame(event_data)
    else:
        print(f"Unsupported file type: {file_extension}")
        return None

    # print(event_log_df)
    return event_log_df

def format_check(name):
    """Check whether an event log has exactly the attributes and contents which an event log 
    generated from the simulation model should have.

    Parameters
    ----------
    name : str
        name of the event log file

    Returns
    -------
    bool
        whether the format is right or not
    """

    event_log = convert_to_dataframe(name)

    allowed_columns = {'CaseID', 'Activity', 'StartTimestamp', 'EndTimestamp'}
    allowed_activities = {'place order', 'arrange standard order', 'arrange custom order', 'pick from stock A', 'pick from stock B', 'pick from stock C', 'manufacture A', 'manufacture B', 'pack A', 'pack B', 'pack C', 'attempt delivery A', 'attempt delivery B', 'attempt delivery C', 'order completed'}

    # check if the attributes are the same
    for column_name in event_log.columns:
        if column_name not in allowed_columns:
            return False

    # check for each attribute if the content is allowed
    for index, event in event_log.iterrows():
        case_id = event['CaseID']
        if not isinstance(case_id, int):
            return False

        activity = event['Activity']
        if activity not in allowed_activities:
            return False
        
        res = True

        start = event['StartTimestamp']

        try:
            bool(datetime.datetime.strptime(start, '%Y-%m-%d %H:%M'))
        except ValueError:
            res = False
        if not res and not (start == " " or start == None):
            return False
        
        end = event['EndTimestamp']
      
        try:
            bool(datetime.datetime.strptime(end, '%Y-%m-%d %H:%M'))
        except ValueError:
            res = False
        if not res and not (end == " " or end == None):
            return False
        
    return True

def get_active_cases(name):
    """Get a list of the cases which are active in the event log.
    (Note: a case is "active" if there are at least 2 more activities until it's finished.)

    Parameters
    ----------
    name : str
        name of the event log file

    Returns
    -------
    list of int
        a list of the case-ids of the active cases
    """

    event_log_df = convert_to_dataframe(name)
    
    active_cases = event_log_df.groupby('CaseID').filter(lambda x: ('order completed' not in x['Activity'].values) and ('attempt delivery A' not in x['Activity'].values) and ('attempt delivery B' not in x['Activity'].values) and ('attempt delivery C' not in x['Activity'].values))['CaseID'].unique().tolist()
    # print(active_cases)
    return active_cases

def show_active_cases(name):
    """Get a list of the traces of the cases which are active in the event log.

    Parameters
    ----------
    name : str
        name of the event log file

    Returns
    -------
    list of tuple of (int, list of str)
    """

    caselist = get_active_cases(name)
    reslist = []
    for case in caselist:
        state = get_state(case, name)
        trace = []
        events = state['case']

        for i in range(len(events)):
            if events[i] == 1:
                trace.append(model.map_number_to_activity(i+1))     

        tup = (case, trace)
        reslist.append(tup)

    return reslist

def get_state(case_id, name):
    """Get the state of a case in an event log (Note: matches the state defined in environment)

    Parameters
    ----------
    case_id : int
        the case-id of a case in the event log
    name : str
        name of the event log file

    Returns
    -------
    collections.OrderedDict of {str : list of int, str : int, str : list of int}
        the state of the case
    """

    process = np.zeros(13, dtype=int)
    num_s = 1
    process[0] = num_s
    num_ot = 4
    process[1] = num_ot
    num_sh_a = 2
    process[2] = num_sh_a
    num_sh_b = 2
    process[3] = num_sh_b
    num_sh_c = 2
    process[4] = num_sh_c
    num_m_a = 4
    process[5] = num_m_a
    num_m_b = 10
    process[6] = num_m_b
    num_p_a = 2
    process[7] = num_p_a
    num_p_b = 3
    process[8] = num_p_b
    num_p_c = 3
    process[9] = num_p_c
    num_ds_a = 30
    process[10] = num_ds_a
    num_ds_b = 45
    process[11] = num_ds_b
    num_ds_c = 45
    process[12] = num_ds_c

    case = np.zeros(15, dtype=int)

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

    event_log = convert_to_dataframe(name)
    # Sort the event log by case ID and start timestamp
    event_log.sort_values(by=['CaseID', 'StartTimestamp'], inplace=True)

    # Group the event log by case ID and get the last activity for each case
    last_activities = event_log.groupby('CaseID').tail(1).reset_index()
   
    # Remap the activity names to numbers using the mapping dictionary
    last_activities['Activity'] = last_activities['Activity'].map(activity_mapping)

    # Filter the cases where the end timestamp of the last activity is None or empty
    unfinished_cases = last_activities[last_activities['EndTimestamp'].isnull()]['CaseID'].tolist()

    # Update the state of the ressources given all unfinished cases
    for i in unfinished_cases:
        activity = last_activities[last_activities['CaseID'] == i]['Activity'].values[0]
        if activity == 1 or activity == 15:
            process[0] -= 1
        elif activity == 2 or activity == 3:
            process[1] -= 1
        else:
            process[activity-2] -= 1

    # Get the state of the case for the given Case ID
    filtered_log = event_log[event_log['CaseID'] == case_id]
    activities = filtered_log['Activity'].map(activity_mapping).tolist()
    for i in activities:
        case[i-1] += 1

    # Get the last event for the given Case ID
    event = last_activities[last_activities['CaseID'] == case_id]['Activity'].values[0]

    state = OrderedDict()
    state['case'] = case
    state['event'] = event
    state['process'] = process

    state = OrderedDict()
    state['case'] = case
    state['event'] = event
    state['process'] = process

    # print(state)

    return state

def generate_event_log(start_timestamp, time):
    """Generate an event log from the simulation model and export it to .csv and .xes

    Parameters
    ----------
    start_timestamp : datetime
        the start date and time of the simulation
    time : int
        the time units for which the simulation is supposed to run
    """

    ressources = [] 
    num_s = 1
    ressources.append(num_s+1)
    num_ot = 4
    ressources.append(num_ot+1)
    num_sh_a = 2
    ressources.append(num_sh_a+1)
    num_sh_b = 2
    ressources.append(num_sh_b+1)
    num_sh_c = 2
    ressources.append(num_sh_c+1)
    num_m_a = 4
    ressources.append(num_m_a+1)
    num_m_b = 10
    ressources.append(num_m_b+1)
    num_p_a = 2
    ressources.append(num_p_a+1)
    num_p_b = 3
    ressources.append(num_p_b+1)
    num_p_c = 3
    ressources.append(num_p_c+1)
    num_ds_a = 25
    ressources.append(num_ds_a+1)
    num_ds_b = 40
    ressources.append(num_ds_b+1)
    num_ds_c = 45
    ressources.append(num_ds_c+1)      
    
    # generate event log - init env, process and let it run for the specified time
    env = simpy.Environment()
    business_process = BusinessProcess(env, ressources)
    business_process.event_log_flag = True
    global current_time
    current_time = start_timestamp
    env.process(model.run_process(env, business_process))
    env.run(until = time)
    # export to both formats
    # export_to_csv(business_process, r'Frontend/export/elog.csv') #docker
    # export_to_xes(business_process, r'Frontend/export/elog.xes') #docker
    export_to_csv(business_process, r'export/elog.csv') #local
    export_to_xes(business_process, r'export/elog.xes') #local

def get_case_information(case_id, name):
    """Generate an event log from the simulation model and export it to .csv and .xes

    Parameters
    ----------
    case_id : int
        the case-id of a case in the event log
    name : str
        name of the event log file
    
    Returns
    -------
    pandas.DataFrame
        a dataframe containing all the events that happened for a certain case
    """

    event_log = convert_to_dataframe(name)
    # Sort the event log by case ID and start timestamp
    event_log.sort_values(by=['CaseID', 'StartTimestamp'], inplace=True)
    filtered_event_log = event_log[event_log['CaseID'] == case_id]

    return filtered_event_log