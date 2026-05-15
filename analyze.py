
import json
import os
import re
from dataclasses import dataclass
import pandas as pd
import plotly.graph_objects as go


#TODO
# read through all files extract JSON objects 
# grouping
## RQ1 - comparing to buddy
    # self made bdds:
        # quadratic (adiar)
        # diamond  (adiar)
        # memo (adiar)
        # quadratic (buddy)
        # diamond  (buddy)
        # memo (buddy)
    # picotrav
        # all circuits (adiar)
        # all circuits (buddy)

## RQ2 - comparing special cases
    #we have for each self made bdd a small, medium and large instance 
    #for eahc of these we do adj_swap, JD and JU 5 times with varying number of jumps/swaps
    # we also run each with nested sweepingfor comparison 



 
@dataclass
class ParsedFileName:
    n: int
    bdd: str
    order: str
    jumps: int
    nested_sweeping: bool


_PATTERN = re.compile(
r"""
    ^n_(?P<n>\d+)
    _t_(?P<t>[^_]+)
    _o_(?P<o>.+?)
    _j_(?P<j>\d+)
    (?:_r_(?P<r>\d+))?
    _?
    \.out$
    """,
    re.VERBOSE,
)


def parse_filename(filename: str) -> ParsedFileName:
    match = _PATTERN.match(filename)

    if not match:
        raise ValueError(f"Invalid filename format: {filename}")

    groups = match.groupdict()

    return ParsedFileName(
        n=int(groups["n"]),
        bdd=groups["t"],
        order=groups["o"],
        jumps=int(groups["j"]),
        nested_sweeping=groups["r"] is not None,
    )



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


p = r"adiar/replace/bdd"

data_list = []
data_info = []
for e in os.scandir(p):
    if e.is_file():
        test = parse_filename(e.path.split("/")[-1])
        #print(test)
        with open(e.path, "r") as f:
            text = f.read()
            try :
                data_block = extract_json_block(text)
                #print(data_block)
                data = json.loads(data_block)
                data_list.append(data)
                data_info.append(test)
            except :
                continue


def print_list(l) : 
    for e in l:
        print(e)
    print()

def specialize_time(data_list, infolist, instance, order, ns) :
    res = []
    for i in range(len(data_list)) :
         if infolist[i].bdd == instance and infolist[i].order == order and (infolist[i].nested_sweeping == ns) :
            target = data_list[i]["benchmark"]["construction"]["replace"]
            res.append([infolist[i],target["size (nodes)"], target['time (ms)']])
    res_sorted = sorted(res, key=lambda x: (x[0].n, x[0].jumps))
    return res_sorted


#all the special case data 
quad_as = specialize_time(data_list, data_info, "quadratic", "ADJ_SWAP", False)
quad_as_ns = specialize_time(data_list, data_info, "quadratic", "ADJ_SWAP", True)

quad_JD = specialize_time(data_list, data_info, "quadratic", "JUMP_DOWN", False)
quad_JD_ns = specialize_time(data_list, data_info, "quadratic", "JUMP_DOWN", True)

quad_JU = specialize_time(data_list, data_info, "quadratic", "JUMP_UP", False)
quad_JU_ns = specialize_time(data_list, data_info, "quadratic", "JUMP_UP", True)


diamond_as = specialize_time(data_list, data_info, "diamond", "ADJ_SWAP", False)
diamond_as_ns = specialize_time(data_list, data_info, "diamond", "ADJ_SWAP", True)

diamond_JD = specialize_time(data_list, data_info, "diamond", "JUMP_DOWN", False)
diamond_JD_ns = specialize_time(data_list, data_info, "diamond", "JUMP_DOWN", True)

diamond_JU = specialize_time(data_list, data_info, "diamond", "JUMP_UP", False)
diamond_JU_ns = specialize_time(data_list, data_info, "diamond", "JUMP_UP", True)


memo_as = specialize_time(data_list, data_info, "memo", "ADJ_SWAP", False)
memo_as_ns = specialize_time(data_list, data_info, "memo", "ADJ_SWAP", True)

memo_JD = specialize_time(data_list, data_info, "memo", "JUMP_DOWN", False)
memo_JD_ns = specialize_time(data_list, data_info, "memo", "JUMP_DOWN", True)

memo_JU = specialize_time(data_list, data_info, "memo", "JUMP_UP", False)
memo_JU_ns = specialize_time(data_list, data_info, "memo", "JUMP_UP", True)

##making cool graphs TM

# --- 1. Consolidate Data ---
# This replaces your manual 'quad_as', 'memo_JD' lists with one clean DataFrame
rows = []
for i in range(len(data_list)):
    target = data_list[i]["benchmark"]["construction"]["replace"]
    rows.append({
        "n": data_info[i].n,
        "bdd": data_info[i].bdd,
        "order": data_info[i].order,
        "jumps": data_info[i].jumps,
        "ns": data_info[i].nested_sweeping,
        "time_ms": target['time (ms)'],
        "nodes_before": data_list[i]["benchmark"]["construction"]["intermediate results"]["final size (nodes)"],
        "nodes_after": target["size (nodes)"],
        "category": f"{data_info[i].bdd} | {data_info[i].order} | NS:{data_info[i].nested_sweeping}"
    })

df = pd.DataFrame(rows).sort_values(by=['bdd', 'order', 'n', 'ns', 'jumps' ])

with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 1000):
    print(df)

# --- 2. Build the Figure ---
fig = go.Figure()
categories = df['category'].unique()
metrics = ["time_ms", "nodes", "jumps", "n"]

# Add one trace per category
for i, cat in enumerate(categories):
    curr_df = df[df['category'] == cat]
    fig.add_trace(
        go.Scatter(
            x=curr_df["time_ms"], 
            y=curr_df["nodes"],
            mode='lines+markers',
            name=cat,
            visible=(i == 0), # Only first is visible initially
            hovertemplate="<b>%{fullData.name}</b><br>X: %{x}<br>Y: %{y}<extra></extra>"
        )
    )

# --- 3. Create Interaction Menus ---

# Dropdown 1: Select Category (Visibility)
cat_buttons = []
for i, cat in enumerate(categories):
    viz = [False] * len(categories)
    viz[i] = True
    cat_buttons.append(dict(label=cat, method="update", args=[{"visible": viz}]))

# Dropdown 2: Select X-Axis Metric
x_buttons = []
for m in metrics:
    x_buttons.append(dict(
        label=f"X: {m}",
        method="restyle",
        args=[{"x": [df[df['category'] == c][m].values for c in categories]}]
    ))

# Dropdown 3: Select Y-Axis Metric
y_buttons = []
for m in metrics:
    y_buttons.append(dict(
        label=f"Y: {m}",
        method="restyle",
        args=[{"y": [df[df['category'] == c][m].values for c in categories]}]
    ))

# --- 4. Final Layout ---
fig.update_layout(
    updatemenus=[
        dict(buttons=cat_buttons, direction="down", x=0.0, y=1.15, showactive=True, xanchor="left"),
        dict(buttons=x_buttons, direction="down", x=0.35, y=1.15, showactive=True, xanchor="left"),
        dict(buttons=y_buttons, direction="down", x=0.6, y=1.15, showactive=True, xanchor="left")
    ],
    annotations=[
        dict(text="Subset:", x=0.0, y=1.22, xref="paper", yref="paper", showarrow=False),
        dict(text="X Axis:", x=0.35, y=1.22, xref="paper", yref="paper", showarrow=False),
        dict(text="Y Axis:", x=0.6, y=1.22, xref="paper", yref="paper", showarrow=False)
    ],
    xaxis_title="Value",
    yaxis_title="Value",
    template="plotly_white",
    margin=dict(t=150) # Make space for menus
)

# fig.show()
