
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from analyzebuddypico import df as pico_buddy_df
from analyzepico import df as pico_adiar_df
from analyze import df as special_cases_df


@dataclass
class ArrayCollection:
    adiar_array : list
    buddy_array : list
    cudd_array : list

font = {"fontname" : "Century Schoolbook", "size" : 20} #axis titles
font2 = {"fontname" : "Century Schoolbook", "size" : 12} #annotations

"""
narray_quad = getN("quad")
narray_diamond = getN("diamond")
narray_memo = getN("memo")
n_arrays = [narray_quad, narray_diamond, narray_memo]
time_arrays_quad = getTimes("quad")
time_arrays_diamond = getTimes("diamond")
time_arrays_memo = getTimes("memo")
"""

def time_Nsize_graphs(n_arrays, time_arrays_quad, time_arrays_diamond, time_arrays_memo) :
    #setting up fig
    fig, axs = plt.subplots(1, 3)

    #quad_fig
    axs[0].set_title("Quadratic")
    axs[0].scatter(n_arrays[0], time_arrays_quad.adiar_time_array, label="Adiar")
    axs[0].scatter(n_arrays[0], time_arrays_quad.buddy_time_array, label="BuDDy")
    axs[0].scatter(n_arrays[0], time_arrays_quad.cudd_time_array, label="CuDD")

    #diamond_fig
    axs[1].set_title("Diamond")
    axs[1].scatter(n_arrays[1], time_arrays_diamond.adiar_time_array, label="Adiar")
    axs[1].scatter(n_arrays[1], time_arrays_diamond.buddy_time_array, label="BuDDy")
    axs[1].scatter(n_arrays[1], time_arrays_diamond.cudd_time_array, label="CuDD")

    #memo_fig
    axs[2].set_title("Memoization")
    axs[2].scatter(n_arrays[2], time_arrays_memo.adiar_time_array, label="Adiar")
    axs[2].scatter(n_arrays[2], time_arrays_memo.buddy_time_array, label="BuDDy")
    axs[2].scatter(n_arrays[2], time_arrays_memo.cudd_time_array, label="CuDD")

    fig.show()


def picotrav_scatter_plots(all_buddy_times, all_adiar_times, circuit_names) :
    #assumed: given args are lists of lists, each inner list is times for one circuit and is sorted lexicographically by order
    fig, axs = plt.subplots(1,1)

    fig.suptitle("Picotrav results")
    #on y axis we want buddy_times / adiar_times 
    #on x axis just adiar times maybe?

    cmap = plt.get_cmap("Accent")
    for circuit_list_index in range(len(all_buddy_times)):
        y_axis_vals = []
        buddy_circuit_list = all_buddy_times[circuit_list_index]
        adiar_circuit_list = all_adiar_times[circuit_list_index]
        for c in range(len(buddy_circuit_list)) :
            #TODO : make shapes instead of colors
            
            y_axis_vals.append(buddy_circuit_list[c]/adiar_circuit_list[c] if adiar_circuit_list[c] != 0.0 else 0)
            axs.scatter(adiar_circuit_list, buddy_circuit_list, color=cmap(c), label= circuit_names[c])

    plt.show()


## building scatter plot?
circuit_names = pico_buddy_df.get("circuit").unique().tolist()
print(circuit_names)

all_buddy_times = []
all_adiar_times = []
for name in circuit_names :
    bt = pico_buddy_df.loc[pico_buddy_df["circuit"] == name].get("time (ms)").tolist()
    at = pico_buddy_df.loc[pico_buddy_df["circuit"] == name].get("time (ms)").tolist()
    print("here??", bt)
    all_buddy_times.append(bt)
    all_adiar_times.append(at)

print(circuit_names[0], all_buddy_times[0])
print(circuit_names[0], all_adiar_times[0])

picotrav_scatter_plots(all_buddy_times, all_adiar_times, circuit_names)