# -*- coding: utf-8 -*-
"""
Cognitive Control Task.
Authors: Makowski et al. (under review)
Copyright: The Neuropsydia Development Team
Site: https://github.com/DominiqueMakowski/CoCon.py
"""

import numpy as np
import pandas as pd
import neuropsydia as n
import datetime
import scipy

#==============================================================================
# Infos
#==============================================================================
authors = "Makowski et al. (under review)"
version = "1.0"

#==============================================================================
# Initialization
#==============================================================================
angle_to_orientation = {-90:"LEFT", 90:"RIGHT", 0:"DOWN", 180:"UP", "NA":"NA"}
# Colors contrasts
colors_ref = {"white": (255, 255, 255),
              "red": (255, 85, 54),
              "yellow": (255,235,59),
              "blue": (33,150,243)}
testmode = True


#==============================================================================
# Trial
#==============================================================================
def run_trials(cache, trials):

    prestim_interval = list(np.random.uniform(33.333333, 2000, len(trials)-1))
    prestim_interval.insert(0, 2000)


    for order, trial in enumerate(trials):
        n.refresh()
        trial["Order"] = order+1
        trial["Time_Trial_Onset"] = datetime.datetime.now()

        # Wait
        trial["Prestimulus_Interval"] = int(prestim_interval[order])
        if testmode is False:
            trial["Prestimulus_Interval"] = n.time.wait(int(prestim_interval[order]))

        # Diplay stuff
        n.image(trial["Global_Color"] + "_" + trial["Global_Shape"], size=8, extension = ".png", cache = cache, path = "./Stimuli/", rotate=trial["Global_Angle"])
        n.image(trial["Local_Color"] + "_" + trial["Local_Shape"], size=8, extension = ".png", cache = cache, path = "./Stimuli/", rotate=trial["Local_Angle"])

        n.refresh()
        trial["Time_Stimulus_Onset"] = datetime.datetime.now()

        if testmode is False:
            answer, RT = n.response(time_max = 1750, allow=["DOWN", "RIGHT", "LEFT"])
            if answer == "Time_Max_Exceeded":
                answer = "NA"
        else:
            answer = np.random.choice(["DOWN", "RIGHT", "LEFT", "NA"])
            RT = np.random.uniform(100, 1750)
        trial["Response"] = answer
        trial["RT"] = RT


        n.newpage('grey', auto_refresh=False)


    return(trials)


#==============================================================================
# Processing
#==============================================================================
def statistics(data):
    n.newpage("white")
    n.write("Veuillez patienter...", y=-9, color="blue")
    n.refresh()

    df = pd.DataFrame.from_dict(data)

    # Scores
    df["Response_Correct_Orientation"] = [angle_to_orientation[angle] for angle in df["Response_Correct"]]
    df["Correct"] = np.where(df["Response"]==df["Response_Correct_Orientation"], 1, 0)
    df["Color_Congruence"] = np.where(df["Local_Color"]==df["Global_Color"], True, False)

    # Response Type - STD
#    df = df.reset_index()
#    response_type = []
#    for row in range(len(df)):
#        if df["Correct"][row]==1 and df["Response_Correct_Orientation"][row]!="NA":
#            response_type.append("Hit")
#        if df["Correct"][row]==1 and df["Response_Correct_Orientation"][row]=="NA":
#            response_type.append("Correct_Rejection")
#        if df["Correct"][row]==0 and df["Response_Correct_Orientation"][row]!="NA":
#            response_type.append("Miss")
#        if df["Correct"][row]==0 and df["Response_Correct_Orientation"][row]=="NA":
#            response_type.append("False_Alarm")
#    df["Response_Type"] = response_type



    # Luminance and contrast
    luminance_global = []
    luminance_local = []
    contrast = []
    for row in range(len(df)):
        luminance_global.append(n.color_luminance(colors_ref[df["Global_Color"][row]]))
        luminance_local.append(n.color_luminance(colors_ref[df["Local_Color"][row]]))
        contrast.append(n.color_contrast(colors_ref[df["Global_Color"][row]], colors_ref[df["Local_Color"][row]]))
    df["Luminance_Global"] = luminance_global
    df["Luminance_Local"] = luminance_local
    df["Contrast"] = contrast

    if df["Condition_Conflict"].values[0] == False:
        dfs = [df.reindex()]
    else:
        dfs = [df[df["Conflict"]=="Congruent"].sort_values("Order").reindex(), df[df["Conflict"]=="Incongruent"].sort_values("Order").reindex()]

    for data in dfs:
        cumulative_average = []
        cumulative_sd = []
        cumulative_se = []
        for row in range(len(data)):
            global sliced
            sliced = data.loc[0:row]
            sliced = sliced[(sliced["Correct"]==1) & (sliced["Response_Correct"].map(str)!="NA")]["RT"]
            cumulative_average.append(sliced.mean())
            cumulative_sd.append(sliced.std())
            if len(sliced.dropna()) > 1:
                cumulative_se.append(scipy.stats.sem(sliced))
            else:
                cumulative_se.append(np.nan)
        data["Cumulative_Average"] = cumulative_average
        data['Cumulative_SD'] = cumulative_sd
        data['Cumulative_SE'] = cumulative_se
    df = pd.concat(dfs)
    df.sort_values("Order")
    df = df.replace("NA", np.nan)

    return(df)

#==============================================================================
# Sequence
#==============================================================================
def sequence(cache, response_selection="None", inhibition=False, conflict=False):



    # Sequence Preparation
    if response_selection == "None":
        trials = []
        for i in range(30):
            trial = {
"Condition_Response_Selection":response_selection,
"Condition_Inhibition":inhibition,
"Condition_Conflict":conflict,
"Global_Shape":"circle",
"Global_Color":np.random.choice(["red", "yellow", "blue", "white"]),
"Global_Angle":0,
"Local_Shape":"local",
"Local_Color":np.random.choice(["red", "yellow", "blue", "white"]),
"Local_Angle":np.random.choice([-90, 0, 90, 180]),
"Inhibition":False,
"Conflict":"Neutral",
"Response_Availability":True,
"Response_Correct":0
            }
            trials.append(trial)
    if response_selection == "Conditional":
        if conflict is False:
            if inhibition is False:
                trials = []
                correct_responses = {-90:-90, 0:0, 90:90, 180:"NA"}
                for i in range(30):
                    trial = {
"Condition_Response_Selection":response_selection,
"Condition_Inhibition":inhibition,
"Condition_Conflict":conflict,
"Global_Shape":"circle",
"Global_Color":np.random.choice(["red", "yellow", "blue", "white"]),
"Global_Angle":0,
"Local_Shape":"local",
"Local_Color":np.random.choice(["red", "yellow", "blue", "white"]),
"Local_Angle":np.random.choice([-90, 0, 90]),
"Inhibition":False,
"Conflict":"Neutral",
"Response_Availability":True
                    }
                    trial["Response_Correct"] = correct_responses[trial["Local_Angle"]]
                    trials.append(trial)
                for i in range(3):
                    trial = {
"Condition_Response_Selection":response_selection,
"Condition_Inhibition":inhibition,
"Condition_Conflict":conflict,
"Global_Shape":"circle",
"Global_Color":np.random.choice(["red", "yellow", "blue", "white"]),
"Global_Angle":0,
"Local_Shape":"local",
"Local_Color":np.random.choice(["red", "yellow", "blue", "white"]),
"Local_Angle":180,
"Inhibition":False,
"Conflict":"Neutral",
"Response_Availability":False,
"Response_Correct":"NA"
                    }
                    trials.append(trial)
                np.random.shuffle(trials)
            else:
                trials = []
                correct_responses = {-90:-90, 0:0, 90:90, 180:"NA"}
                for i in range(40):
                    trial = {
"Condition_Response_Selection":response_selection,
"Condition_Inhibition":inhibition,
"Condition_Conflict":conflict,
"Global_Shape":"circle",
"Global_Color":np.random.choice(["red", "yellow", "blue"]),
"Global_Angle":0,
"Local_Shape":"local",
"Local_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Angle":np.random.choice([-90, 0, 90]),
"Inhibition":False,
"Conflict":"Neutral",
"Response_Availability":True
                    }
                    trial["Response_Correct"] = correct_responses[trial["Local_Angle"]]
                    trials.append(trial)
                for i in range(3):
                    trial = {
"Condition_Response_Selection":response_selection,
"Condition_Inhibition":inhibition,
"Condition_Conflict":conflict,
"Global_Shape":"circle",
"Global_Color":np.random.choice(["red", "yellow", "blue"]),
"Global_Angle":0,
"Local_Shape":"local",
"Local_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Angle":180,
"Inhibition":False,
"Conflict":"Neutral",
"Response_Availability":False,
"Response_Correct":"NA"
                    }
                    trials.append(trial)
                for i in range(6):
                    trial = {
"Condition_Response_Selection":response_selection,
"Condition_Inhibition":inhibition,
"Condition_Conflict":conflict,
"Global_Shape":"circle",
"Global_Color":"white",
"Global_Angle":0,
"Local_Shape":"local",
"Local_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Angle":np.random.choice([-90, 0, 90]),
"Inhibition":True,
"Conflict":"Neutral",
"Response_Availability":True,
"Response_Correct":"NA"
                    }
                    trials.append(trial)
                for i in range(3):
                    trial = {
"Condition_Response_Selection":response_selection,
"Condition_Inhibition":inhibition,
"Condition_Conflict":conflict,
"Global_Shape":"circle",
"Global_Color":"white",
"Global_Angle":0,
"Local_Shape":"local",
"Local_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Angle":180,
"Inhibition":True,
"Conflict":"Neutral",
"Response_Availability":False,
"Response_Correct":"NA"
                    }
                    trials.append(trial)
                np.random.shuffle(trials)
        else:
            trials = []
            correct_responses = {-90:-90, 0:0, 90:90, 180:"NA"}
            for i in range(40):
                trial = {
"Condition_Response_Selection":response_selection,
"Condition_Inhibition":inhibition,
"Condition_Conflict":conflict,
"Global_Shape":"global",
"Global_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Shape":"local",
"Local_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Angle":np.random.choice([-90, 0, 90]),
"Inhibition":False,
"Conflict":"Incongruent",
"Response_Availability":True
                }
                trial["Response_Correct"] = correct_responses[trial["Local_Angle"]]
                if trial["Local_Angle"] in [-90, 0]:
                    trial["Global_Angle"] = trial["Local_Angle"] + 180
                else:
                    trial["Global_Angle"] = trial["Local_Angle"] - 180
                trials.append(trial)
            for i in range(3):
                trial = {
"Condition_Response_Selection":response_selection,
"Condition_Inhibition":inhibition,
"Condition_Conflict":conflict,
"Global_Shape":"global",
"Global_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Shape":"local",
"Local_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Angle":180,
"Inhibition":False,
"Conflict":"Incongruent",
"Response_Availability":False,
"Response_Correct":"NA"
                }
                if trial["Local_Angle"] in [-90, 0]:
                    trial["Global_Angle"] = trial["Local_Angle"] + 180
                else:
                    trial["Global_Angle"] = trial["Local_Angle"] - 180
                trials.append(trial)
            for i in range(6):
                trial = {
"Condition_Response_Selection":response_selection,
"Condition_Inhibition":inhibition,
"Condition_Conflict":conflict,
"Global_Shape":"global",
"Global_Color":"white",
"Local_Shape":"local",
"Local_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Angle":np.random.choice([-90, 0, 90]),
"Inhibition":True,
"Conflict":"Incongruent",
"Response_Availability":True,
"Response_Correct":"NA"
                }
                if trial["Local_Angle"] in [-90, 0]:
                    trial["Global_Angle"] = trial["Local_Angle"] + 180
                else:
                    trial["Global_Angle"] = trial["Local_Angle"] - 180
                trials.append(trial)
            for i in range(3):
                trial = {
"Condition_Response_Selection":response_selection,
"Condition_Inhibition":inhibition,
"Condition_Conflict":conflict,
"Global_Shape":"global",
"Global_Color":"white",
"Local_Shape":"local",
"Local_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Angle":180,
"Inhibition":True,
"Conflict":"Incongruent",
"Response_Availability":False,
"Response_Correct":"NA"
                }
                if trial["Local_Angle"] in [-90, 0]:
                    trial["Global_Angle"] = trial["Local_Angle"] + 180
                else:
                    trial["Global_Angle"] = trial["Local_Angle"] - 180
                trials.append(trial)
            np.random.shuffle(trials)
            for i in range(40):
                trial = {
"Condition_Response_Selection":response_selection,
"Condition_Inhibition":inhibition,
"Condition_Conflict":conflict,
"Global_Shape":"global",
"Global_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Shape":"local",
"Local_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Angle":np.random.choice([-90, 0, 90]),
"Inhibition":False,
"Conflict":"Congruent",
"Response_Availability":True
                }
                trial["Response_Correct"] = correct_responses[trial["Local_Angle"]]
                trial["Global_Angle"] = trial["Local_Angle"]
                trials.append(trial)
            for i in range(3):
                trial = {
"Condition_Response_Selection":response_selection,
"Condition_Inhibition":inhibition,
"Condition_Conflict":conflict,
"Global_Shape":"global",
"Global_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Shape":"local",
"Local_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Angle":180,
"Inhibition":False,
"Conflict":"Congruent",
"Response_Availability":False,
"Response_Correct":"NA"
                }
                trial["Global_Angle"] = trial["Local_Angle"]
                trials.append(trial)
            for i in range(6):
                trial = {
"Condition_Response_Selection":response_selection,
"Condition_Inhibition":inhibition,
"Condition_Conflict":conflict,
"Global_Shape":"global",
"Global_Color":"white",
"Local_Shape":"local",
"Local_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Angle":np.random.choice([-90, 0, 90]),
"Inhibition":True,
"Conflict":"Congruent",
"Response_Availability":True,
"Response_Correct":"NA"
                }
                trial["Global_Angle"] = trial["Local_Angle"]
                trials.append(trial)
            for i in range(3):
                trial = {
"Condition_Response_Selection":response_selection,
"Condition_Inhibition":inhibition,
"Condition_Conflict":conflict,
"Global_Shape":"global",
"Global_Color":"white",
"Local_Shape":"local",
"Local_Color":np.random.choice(["red", "yellow", "blue"]),
"Local_Angle":180,
"Inhibition":True,
"Conflict":"Congruent",
"Response_Availability":False,
"Response_Correct":"NA"
                }
                trial["Global_Angle"] = trial["Local_Angle"]
                trials.append(trial)
            np.random.shuffle(trials)



    # Instructions
    n.newpage("white")
    n.write("Instructions", style="bold", y=8, size=1.5)

    if inhibition is False:
        instr_angles = [-90 , 0, 90, 180]
        instr_glob_angles = [-90 , 0, -90, 0]
        instr_glob_color = ["blue", "yellow", "white", "red"]
        instr_loc_color = ["red", "blue", "red", "yellow"]
        instr_responses = ["arrow", "arrow", "arrow", "cross"]
    else:
        instr_angles = [-90 , 0, 90, 180, -90]
        instr_glob_angles = [-90 , 0, -90, 0, -90]
        instr_glob_color = ["blue", "yellow", "red", "blue", "white"]
        instr_loc_color = ["red", "red", "blue", "yellow", "red"]
        instr_responses = ["arrow", "arrow", "arrow", "cross", "cross"]
    if conflict is True:
        instr_shapes = "_global"
    else:
        instr_shapes = "_circle"
    if response_selection == "None":
        intr_resp_angles = [0, 0, 0, 0, 0]
        instr_responses = ["arrow", "arrow", "arrow", "arrow"]
    if response_selection == "Conditional":
        intr_resp_angles = [-90 , 0, 90, 0, 0]

    x = -7.5
    for pos, angle in enumerate(instr_angles):
        n.image(instr_glob_color[pos] + instr_shapes, size=6, y=1, x = x+pos*3.75, extension = ".png", path = "./Stimuli/", rotate=instr_glob_angles[pos])
        n.image(instr_loc_color[pos] + "_local", size=6, y=1, x = x+pos*3.75, extension = ".png", path = "./Stimuli/", rotate=angle)
        n.image(instr_responses[pos], size=2.75, y=-5.5, x = x+pos*3.75, extension = ".png", path = "./Stimuli/", rotate=intr_resp_angles[pos])

    n.refresh()
    n.write("Appuyez sur ENTRER pour commencer.", style="end")
    n.newpage('grey', auto_refresh=False)



    # Run trials
    data = run_trials(cache, trials)
    df = statistics(data)

    return(df)


#==============================================================================
# Processing
#==============================================================================
def processing(dfs):
    df = pd.concat(dfs)

    # Slice it
    base = df[(df['Condition_Response_Selection']=='None')].reset_index()
    base["Order"] = range(1, len(base)+1)
    respsel = df[(df['Condition_Response_Selection']=='Conditional') & (df['Condition_Inhibition']==False) & (df['Condition_Conflict']==False)].reset_index()
    respsel["Order"] = range(1, len(respsel)+1)
    inhib = df[(df['Condition_Response_Selection']=='Conditional') & (df['Condition_Inhibition']==True) & (df['Condition_Conflict']==False)].reset_index()
    inhib["Order"] = range(1, len(inhib)+1)
    cong = df[(df['Condition_Response_Selection']=='Conditional') & (df['Condition_Inhibition']==True) & (df['Condition_Conflict']==True) & (df['Conflict']=='Congruent')].reset_index()
    cong["Order"] = range(1, len(cong)+1)
    incong = df[(df['Condition_Response_Selection']=='Conditional') & (df['Condition_Inhibition']==True) & (df['Condition_Conflict']==True)  & (df['Conflict']=='Incongruent')].reset_index()
    incong["Order"] = range(1, len(incong)+1)


    # Speed: First computation with outliers
    rt_base = base[base["Correct"]==1]["RT"].mean()
    sd_base = base[base["Correct"]==1]["RT"].std()
    rt_respsel = respsel[(respsel["Correct"]==1) & (respsel["Response_Correct"].isnull()==False)]["RT"].mean()
    sd_respsel = respsel[(respsel["Correct"]==1) & (respsel["Response_Correct"].isnull()==False)]["RT"].std()
    rt_inhib = inhib[(inhib["Correct"]==1) & (inhib["Response_Correct"].isnull()==False)]["RT"].mean()
    sd_inhib = inhib[(inhib["Correct"]==1) & (inhib["Response_Correct"].isnull()==False)]["RT"].std()
    rt_cong = cong[(cong["Correct"]==1) & (cong["Response_Correct"].isnull()==False)]["RT"].mean()
    sd_cong = cong[(cong["Correct"]==1) & (cong["Response_Correct"].isnull()==False)]["RT"].std()
    rt_incong = incong[(incong["Correct"]==1) & (incong["Response_Correct"].isnull()==False)]["RT"].mean()
    sd_incong = incong[(incong["Correct"]==1) & (incong["Response_Correct"].isnull()==False)]["RT"].std()

    # Outliers detection
    base["Outliers"] = np.greater((base["RT"]), rt_base+sd_base*1.96) | np.less((base["RT"]), rt_base-sd_base*1.96)
    respsel["Outliers"] = np.greater((respsel["RT"]), rt_respsel+sd_respsel*1.96) | np.less((respsel["RT"]), rt_respsel-sd_respsel*1.96)
    inhib["Outliers"] = np.greater((inhib["RT"]), rt_inhib+sd_inhib*1.96) | np.less((inhib["RT"]), rt_inhib-sd_inhib*1.96)
    cong["Outliers"] = np.greater((cong["RT"]), rt_cong+sd_cong*1.96) | np.less((cong["RT"]), rt_cong-sd_cong*1.96)
    incong["Outliers"] = np.greater((incong["RT"]), rt_incong+sd_incong*1.96) | np.less((incong["RT"]), rt_incong-sd_incong*1.96)

    # Speed: Second computation without outliers
    rt_base = base[(base["Correct"]==1) & (base["Outliers"]==False)]["RT"].mean()
    sd_base = base[(base["Correct"]==1) & (base["Outliers"]==False)]["RT"].std()
    rt_respsel = respsel[(respsel["Correct"]==1) & (respsel["Response_Correct"].isnull()==False) & (base["Outliers"]==False)]["RT"].mean()
    sd_respsel = respsel[(respsel["Correct"]==1) & (respsel["Response_Correct"].isnull()==False) & (base["Outliers"]==False)]["RT"].std()
    rt_inhib = inhib[(inhib["Correct"]==1) & (inhib["Response_Correct"].isnull()==False) & (base["Outliers"]==False)]["RT"].mean()
    sd_inhib = inhib[(inhib["Correct"]==1) & (inhib["Response_Correct"].isnull()==False) & (base["Outliers"]==False)]["RT"].std()
    rt_cong = cong[(cong["Correct"]==1) & (cong["Response_Correct"].isnull()==False) & (base["Outliers"]==False)]["RT"].mean()
    sd_cong = cong[(cong["Correct"]==1) & (cong["Response_Correct"].isnull()==False) & (base["Outliers"]==False)]["RT"].std()
    rt_incong = incong[(incong["Correct"]==1) & (incong["Response_Correct"].isnull()==False) & (base["Outliers"]==False)]["RT"].mean()
    sd_incong = incong[(incong["Correct"]==1) & (incong["Response_Correct"].isnull()==False) & (base["Outliers"]==False)]["RT"].std()

    respsel_effect = rt_respsel - rt_base
    inhibt_effect = rt_inhib - rt_respsel
    cong_effect = rt_cong - rt_inhib
    incong_effect = rt_incong - rt_inhib

    df = pd.concat([base, respsel, inhib, cong, incong])

    df["Speed_Core"] = rt_base
    df["Speed_Core_Variability"] = sd_base
    df["Speed_Response_Selection_Effect"] = respsel_effect
    df["Speed_Inhibition_Effect"] = inhibt_effect
    df["Speed_Congruence_Effect"] = cong_effect
    df["Speed_Incongruence_Effect"] = incong_effect



    # Errors
    base_errors = list(base["Correct"]).count(0)
    respsel_errors_go = list(respsel[respsel["Response_Availability"]==True]["Correct"]).count(0)
    respsel_errors_nopos = list(respsel[respsel["Response_Availability"]==False]["Correct"]).count(0)

    neutral_errors_go = list(inhib[(inhib["Response_Availability"]==True) & (inhib["Inhibition"]==False)]["Correct"]).count(0)
    neutral_errors_nopos = list(inhib[(inhib["Response_Availability"]==False) & (inhib["Inhibition"]==False)]["Correct"]).count(0)
    neutral_errors_nogo = list(inhib[(inhib["Response_Availability"]==True) & (inhib["Inhibition"]==True)]["Correct"]).count(0)
    neutral_errors_double = list(inhib[(inhib["Response_Availability"]==False) & (inhib["Inhibition"]==True)]["Correct"]).count(0)

    cong_errors_go = list(cong[(cong["Response_Availability"]==True) & (cong["Inhibition"]==False)]["Correct"]).count(0)
    cong_errors_nopos = list(cong[(cong["Response_Availability"]==False) & (cong["Inhibition"]==False)]["Correct"]).count(0)
    cong_errors_nogo = list(cong[(cong["Response_Availability"]==True) & (cong["Inhibition"]==True)]["Correct"]).count(0)
    cong_errors_double = list(cong[(cong["Response_Availability"]==False) & (cong["Inhibition"]==True)]["Correct"]).count(0)

    incong_errors_go = list(incong[(incong["Response_Availability"]==True) & (incong["Inhibition"]==False)]["Correct"]).count(0)
    incong_errors_nopos = list(incong[(incong["Response_Availability"]==False) & (incong["Inhibition"]==False)]["Correct"]).count(0)
    incong_errors_nogo = list(incong[(incong["Response_Availability"]==True) & (incong["Inhibition"]==True)]["Correct"]).count(0)
    incong_errors_double = list(incong[(incong["Response_Availability"]==False) & (incong["Inhibition"]==True)]["Correct"]).count(0)

    errors_go = list(df[(df["Response_Availability"]==True) & (df["Inhibition"]==False) & (df["Condition_Response_Selection"]!="None")]["Correct"]).count(0)
    errors_nopos = list(df[(df["Response_Availability"]==False)]["Correct"]).count(0)
    errors_nogo = list(df[(df["Inhibition"]==True)]["Correct"]).count(0)
    errors_total = list(df[(df["Condition_Response_Selection"]!="None")]["Correct"]).count(0)

    df["Errors_Total"] = errors_total/len(df)


    df["Errors_Orientation"] = errors_go / len(list(df[(df["Response_Availability"]==True) & (df["Inhibition"]==False) & (df["Condition_Response_Selection"]!="None")]["Correct"]))


    df["Errors_Response_Selection"] = errors_nopos / len(list(df[(df["Response_Availability"]==False)]["Correct"]))

    df["Errors_Inhibition"] = errors_nogo  / len(list(df[(df["Inhibition"]==True)]["Correct"]))

    # IES: Inverse Efficiency Score
    IES_Neutral = rt_inhib/(1-neutral_errors_go/len(inhib[(inhib["Response_Availability"]==True) & (inhib["Inhibition"]==False)]))
    IES_Congruent = rt_cong/(1-cong_errors_go/len(cong[(cong["Response_Availability"]==True) & (cong["Inhibition"]==False)]))
    IES_Incongruent = rt_incong/(1-incong_errors_go/len(incong[(incong["Response_Availability"]==True) & (incong["Inhibition"]==False)]))


    df["IES_Neutral"] = IES_Neutral
    df["IES_Neutral_log"] = np.log(IES_Neutral)
    df["IES_Congruent"] = IES_Congruent
    df["IES_Congruent_log"] = np.log(IES_Congruent)
    df["IES_Incongruent"] = IES_Incongruent
    df["IES_Incongruent_log"] = np.log(IES_Incongruent)


    df = df.drop('index', axis=1)




    return(df)
#==============================================================================
# Procedure
#==============================================================================
def procedure():

    n.newpage("white")
    n.write("Veuillez patienter...", y=-9, color="blue")
    n.refresh()

    # Preload images in cache
    cache = {}
    for colour in ["white", "red", "yellow", "blue", "black"]:
        for focus in ["global", "local"]:
            for angle in [-90, 0, 90, 180]:
                cache = n.preload(colour + "_" + focus, size=8, extension = ".png", cache = cache, path = "./Stimuli/", rotate=angle)
                cache = n.preload(colour + "_circle", size=8, extension = ".png", cache = cache, path = "./Stimuli/", rotate=angle)

    dfs = []
    dfs.append(sequence(cache, response_selection="None", inhibition=False, conflict=False))
    dfs.append(sequence(cache, response_selection="Conditional", inhibition=False, conflict=False))
    dfs.append(sequence(cache, response_selection="Conditional", inhibition=True, conflict=False))
    dfs.append(sequence(cache, response_selection="Conditional", inhibition=True, conflict=True))

    df = processing(dfs)
    return(df)
#==============================================================================
# Run
#==============================================================================
n.start()
n.start_screen(name="CoCon", authors=authors)

experiment_start = datetime.datetime.now()



# Participant info
n.newpage()
participant_id = n.ask("Participant ID: ")



df = procedure()

# Save data
df["Participant_ID"] = participant_id
df["Experiment_Start"] = experiment_start
df["Experiment_End"] = datetime.datetime.now()
df["Version"] = version
df["Experiment_Duration"] = (datetime.datetime.now()-experiment_start).total_seconds()

n.save_data(df, filename="CoCon", path="./Data/", participant_id=participant_id, index=False)

n.end_screen(name="CoCon", authors=authors)
n.close()