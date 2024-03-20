"""Petri-Net Generator

The module includes the following functions:

    * generate_petri_net() - generates a petri-net represenation of the business process
    * process_petri_net(): saves the process's petri-net as a png so that it can be used as a static image
    * decorate_petri_net(case, name) - exports a .png of a petri-net with the case trace colored  
    * decorate_petri_net_with_rec(case, rec, name) - exports a .png of a petri-net with the case trace and the recommendation colored
"""

import pm4py
import pandas as pd

import eventlog
import simplesimmodel as simmodel


def generate_petri_net():
    """Generates a petri-net represenation of the business process from a static event log.

    Returns
    -------
    PetriNet
        the net
    Marking
        the initial marking
    Marking
        the final marking
    """

    # we use an existing event log to create a petri net for our process
    # dataframe = pd.read_csv(r'Frontend/static/eventlog.csv', sep=',') #docker
    dataframe = pd.read_csv(r'static/eventlog.csv', sep=',') #local
    dataframe['StartTimestamp'] = pd.to_datetime(dataframe['StartTimestamp'])
    
    # Sort the event log by case ID and start timestamp, and get only finished cases
    dataframe.sort_values(by=['CaseID', 'StartTimestamp'], inplace=True)
    dataframe = dataframe.head(900)
    
    # format and convert to a pm4py event log
    dataframe = pm4py.format_dataframe(dataframe, case_id='CaseID', activity_key='Activity', timestamp_key='StartTimestamp')
    event_log = pm4py.convert_to_event_log(dataframe)

    # discover the petri-net 
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(event_log)
    
    # print(net)
    # pm4py.view_petri_net(net, initial_marking, final_marking)

    return net, initial_marking, final_marking 

def process_petri_net():
    """Function which we use to create the business process's petri-net and save it as a png so we can use it as a static image
    """
    net, initial_marking, final_marking  = generate_petri_net()
    decoration = {}
    for p in net.places:
        decoration.update({p: {}})
        decoration[p].update({"color":"white"})
    for t in net.transitions:
        decoration.update({t: {}})
        decoration[t].update({"color":"white"})
    pm4py.save_vis_petri_net(net, initial_marking, final_marking, bgcolor = "#E6F1FA", decorations = decoration, file_path = r"static/process_net.png") #local

def decorate_petri_net(case, name):
    """Exports a .png of a petri-net with the trace of the case colored.

    Parameters
    ----------
    case : int
        case-id of a case in the event log
    name : str
        name of the event log file
    """
    
    # we generate a petri-net and find the state of the case (more specifically the trace)
    net, initial_marking, final_marking = generate_petri_net()
    state = eventlog.get_state(case, name)
    events = state['case']
    
    # we map each activity that appears in the trace from a number to the anme of the activity
    event_names = []
    for i in range(len(events)):
        if events[i] == 1:
            event_names.append(simmodel.map_number_to_activity(i+1))

    decoration = {}

    # we assign color to each transition with an activity name from the ones we extracted form the trace
    for t in net.transitions:
        if str(t.label) in event_names:    
            decoration.update({t: {}})
            decoration[t].update({"color":"#0072BC"})
            decoration[t].update({"label":t.label})
        else:
            decoration.update({t: {}})
            decoration[t].update({"color":"white"})
            decoration[t].update({"label":t.label})
    
    for p in net.places:
        decoration.update({p: {}})
        decoration[p].update({"color":"white"})


    # pm4py.view_petri_net(net, initial_marking, final_marking, decorations = decoration)
    print("made petrinet")
    # pm4py.save_vis_petri_net(net, initial_marking, final_marking, decorations = decoration, file_path = r"Frontend/static/preview_net.png") #docker
    pm4py.save_vis_petri_net(net, initial_marking, final_marking, bgcolor = "#E6F1FA", decorations = decoration, file_path = r"static/preview_net.png") #local

def decorate_petri_net_with_rec(case, rec, name):
    """Exports a .png of a petri-net in which the trace of the case is colored in one color and the recommended activity in another.

    Parameters
    ----------
    case : int
        case-id of a case in the event log
    rec : int
        the recommended activity
    name : str
        name of the event log file
    """

    net, initial_marking, final_marking = generate_petri_net()
    state = eventlog.get_state(case, name)
    events = state['case']
    
    event_names = []
    for i in range(len(events)):
        if events[i] == 1:
            event_names.append(simmodel.map_number_to_activity(i+1))

    decoration = {}
    rec_name =simmodel.map_number_to_activity(rec)

    for t in net.transitions:
        # print(str(t.label))
        if str(t.label) in event_names:    
            decoration.update({t: {}})
            decoration[t].update({"color":"#0072BC"})
            decoration[t].update({"label":t.label})
        elif str(t.label) == rec_name:
            decoration.update({t: {}})
            decoration[t].update({"color":"#00bc4b"})
            decoration[t].update({"label":t.label})
        else:
            decoration.update({t: {}})
            decoration[t].update({"color":"white"})
            decoration[t].update({"label":t.label})

    for p in net.places:
        decoration.update({p: {}})
        decoration[p].update({"color":"white"})

    # pm4py.view_petri_net(net, initial_marking, final_marking, decorations = decoration)
    # pm4py.save_vis_petri_net(net, initial_marking, final_marking, decorations = decoration, file_path = r"Frontend/static/net.png") #docker
    pm4py.save_vis_petri_net(net, initial_marking, final_marking, bgcolor = "#E6F1FA", decorations = decoration, file_path = r"static/net.png") #local
    return rec_name

# decorate_petri_net(646, 7, "eventlog.csv")
process_petri_net()



