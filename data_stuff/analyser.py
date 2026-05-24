import json
import os
import re
import pandas as pd
from enum import Enum

class Benchmark(Enum):
    SPECIAL = 1
    PICO = 2
    QUAD = 3
    DIAMOND = 4
    MEMO = 5

def extract_json_block(text: str) -> str:
    # Extract JSON object from text.
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
                return text[start : i + 1]

    raise ValueError("Unbalanced JSON braces")

def parse_filename(filename: str , benchmark):
    if (benchmark == Benchmark.SPECIAL) :
        """
        Extracts order and circuit from filename:
        o_LEVEL_DF_f_epfl_arithmetic_adder_blif.out -> ('LEVEL_DF', 'epfl_arithmetic_adder_blif')
        """
        # Matches everything between o_ and _f_ as 'order'
        # Matches everything after _f_ and before .out as 'circuit'
        match = re.search(r"n_(.+)_t_(.+)_o_(.+)_j_(.+)\.out", filename)
        if match:
            return match.group(1), match.group(2), match.group(3), match.group(4), 1
        return "unknown", filename, "Unknown", "Unknown", "Unknown"
    if (benchmark == Benchmark.PICO) :
        """
        Extracts order and circuit from filename:
        o_LEVEL_DF_f_epfl_arithmetic_adder_blif.out -> ('LEVEL_DF', 'epfl_arithmetic_adder_blif')
        """
        # Matches everything between o_ and _f_ as 'order'
        # Matches everything after _f_ and before .out as 'circuit'
        match = re.search(r"o_(.+)_f_(.+)_a_(.+)\.out", filename)
        if match:
            order = match.group(1).lower()
            approach = match.group(3)
            full_circuit = match.group(2)

            # This regex looks at the end of the circuit string.
            # It captures either 'mem_ctrl' or just 'ctrl' right before '_blif'
            tail_match = re.search(r"((?:mem_)?ctrl)_blif$", full_circuit)

            if tail_match:
                circuit_name = tail_match.group(1) + ".blif"
            else:
                # Fallback: if it's another circuit entirely (like adder), just grab its last descriptor
                parts = full_circuit.split("_")
                # If it's 'epfl_arithmetic_adder_blif', parts[-2] is 'adder'
                circuit_name = (
                    f"{parts[-2]}.blif" if parts[-1] == "blif" else f"{parts[-1]}.blif"
                )
            return order, circuit_name, approach
        return "Unknown", filename, "Unknown"


def read_all_data(path, benchmark) :
    data_list = []
    broken_list = []
    for e in os.scandir(path):
        if e.is_file():
            with open(e.path, "r") as f:
                if (benchmark == Benchmark.SPECIAL) :
                    n_b, t_b, o_b, j_b, r_b = parse_filename(e.name, benchmark)
                elif (benchmark == Benchmark.PICO) :
                    order_backup, circuit_backup, approach_b = parse_filename(e.name , benchmark)
                text = f.read()
                try:
                    data_block = extract_json_block(text)
                    data = json.loads(data_block)
                    data_list.append(data)
                except Exception as e:
                    if (benchmark == Benchmark.SPECIAL) :
                        broken_list.append(
                            {"n": n_b, "bdd": t_b, "order": o_b, "jumps": j_b, "ns": r_b}
                        )
                    elif (benchmark == Benchmark.PICO) :
                        broken_list.append(
                            {
                                "circuit": circuit_backup,
                                "order": order_backup,
                                "approach": approach_b,
                            }
                        )
                    continue
    return data_list , broken_list


def extract_rep_special(data_list, extra_data):
    rows = []
    for i in range(len(data_list)):
        package = data_list[i]["bdd package"]
        benchmark = data_list[i]["benchmark"]
        specs = benchmark["specs"]
        construction = benchmark["construction"]
        intermediate = construction["intermediate results"]
        replace = construction["replace"]
        # resources = data_list[i]["resource usage"]
        rows.append(
            {
                "n": specs["n"],
                "bdd": specs["bdd type"],
                "order": specs["order"],
                "jumps": specs["segments"],
                "time (ms)": replace["time (ms)"],
                "ns": specs["nested_sweeping"],
                "bf_size": intermediate["final size (nodes)"],
                "af_size": replace["size (nodes)"],
            }
        )
    return rows + extra_data

def extract_rep_pico(data_list, extra_data) : 
    rows = []
    for i in range(len(data_list)):
        package = data_list[i]["bdd package"]
        benchmark = data_list[i]["benchmark"]
        construction = benchmark["construction"]
        final_diagrams_const = construction["final_diagrams"]
        replace = benchmark["bdd_replace(f)"]
        final_diagrams_rep = replace["final_diagrams"]
        rows.append(
            {
                "circuit": construction["path"].split("/")[-1],
                "order": benchmark["order"],
                "approach": benchmark["nested_mix"],
                "time (ms)": replace["time (ms)"],
                "total (ms)": benchmark["total time (ms)"],
                "before_max": final_diagrams_const["sizemax (nodes)"],
                "before_sum": final_diagrams_const["sizesum (nodes)"],
                "after_max": final_diagrams_rep["sizemax (nodes)"],
                "after_sum": final_diagrams_rep["sizesum (nodes)"],
            }
        )
    return rows + extra_data


