
import json
import os
import re
from dataclasses import dataclass
import pandas as pd




 
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


p = r"outrepspecial/adiar/replace/bdd"

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
    })

df = pd.DataFrame(rows).sort_values(by=['bdd', 'order', 'n', 'ns', 'jumps' ])

with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 1000):
    print(df)

# --- 2. Build the Figure ---
