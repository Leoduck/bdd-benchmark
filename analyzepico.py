
import json
import os
import re
import pandas as pd
import plotly.graph_objects as go


def extract_json_block(text):
    #Extract JSON object from text.

    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON start found")

    brace_count = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                return text[start:i + 1]

    raise ValueError("Unbalanced JSON braces")

def parse_filename(filename):
    """
    Extracts order and circuit from filename: 
    o_LEVEL_DF_f_epfl_arithmetic_adder_blif.out -> ('LEVEL_DF', 'epfl_arithmetic_adder_blif')
    """
    # Matches everything between o_ and _f_ as 'order'
    # Matches everything after _f_ and before .out as 'circuit'
    match = re.search(r"o_(.+)_f_(.+)\.out", filename)
    if match:
        return match.group(1).lower(), match.group(2).split("_")[-2] + ".blif"
    return "Unknown", filename

p_adiar = r"adiar/picotrav_replace/bdd"
p_buddy = r"buddy/picotrav_replace/bdd"

data_list_adiar = []
data_broken_adiar = []
data_list_buddy = []
data_broken_buddy = []
for e in os.scandir(p_adiar):
    if e.is_file():
        with open(e.path, "r") as f:
            order_backup, circuit_backup = parse_filename(e.name)
            text = f.read()
            try :
                data_block = extract_json_block(text)
                data = json.loads(data_block)
                data_list_adiar.append(data)
            except Exception as e :
                data_broken_adiar.append({"circuit": circuit_backup,
                                          "order": order_backup, } )
                continue

for e in os.scandir(p_buddy):
    if e.is_file():
        with open(e.path, "r") as f:
            text = f.read()
            try :
                data_block = extract_json_block(text)
                data = json.loads(data_block)
                data_list_buddy.append(data)
            except Exception as e :
                continue

def print_list(l) : 
    for e in l:
        print(e)
    print()

##making cool graphs TM

# --- 1. Consolidate Data ---
# This replaces your manual 'quad_as', 'memo_JD' lists with one clean DataFrame
rows = []
for i in range(len(data_list_adiar)):
    package = data_list_adiar[i]["bdd package"]
    benchmark = data_list_adiar[i]["benchmark"]
    construction = benchmark["construction"]
    final_diagrams_const = construction["final_diagrams"]
    replace = benchmark["bdd_replace(f)"]
    final_diagrams_rep = replace["final_diagrams"]
    # resources = data_list[i]["resource usage"]
    rows.append({
        "circuit": construction["path"].split("/")[-1],
        "order": benchmark["Replacement to order"],
        "time (ms)": replace["time (ms)"],
        "total (ms)": benchmark["total time (ms)"],
        "before_max": final_diagrams_const["sizemax (nodes)"],
        "before_sum": final_diagrams_const["sizesum (nodes)"],
        "after_max": final_diagrams_rep["sizemax (nodes)"],
        "after_sum": final_diagrams_rep["sizesum (nodes)"],
    })
rows = rows + data_broken_adiar

df = pd.DataFrame(rows).sort_values(by=['circuit', 'order'])

with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 1000):
    print(df)



