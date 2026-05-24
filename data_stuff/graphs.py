
import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
import analyser
import sys


def group_ns_sp_times_per_jump_amount(instance, order) :
    #should group for each amount of jumps made in instance x with order , the ns times and special case times
    subset = instance.loc[instance["order"] == order, ["jumps", "ns", "time (ms)"]]
    #changing table to be [ jumps | ns time | sp time ]
    pivoted = subset.pivot_table(
        index="jumps",
        columns="ns",
        values="time (ms)",
        aggfunc="first"
    )
    pivoted = pivoted.rename(columns={False: "time", True: "ns_time"})
    max_time = pivoted.max().max() #dummy value for missing cases - set to the maximal existing time (kinda cheating maybe?)
    pivoted = pivoted.fillna(max_time) # fill all NaN with max_time value

    #normalized jumps (donno if we want this but just testing)
    max_jumps = pivoted.index.max()
    norm_jumps = (pivoted.index / max_jumps).tolist()
    #clean jumps
    clean_jumps = pivoted.index.tolist() # if we wanna plot those instead..

    #time fraction
    #ensurign that we dont divide by 0 (not that i think we have any 0's in the data but still)
    #pivoted["time"] = pivoted["time"].replace(0, 1e-6) #replace with really small number

    y_axis = (pivoted["ns_time"] / pivoted["time"]).tolist()
    return norm_jumps, y_axis

#for axis stuff
def round_up(x):
    if x <= 0:
        return 1
    magnitude = 10 ** math.floor(math.log10(x))
    return math.ceil(x / magnitude) * magnitude

def special_case_plots(special_cases_df) :
    fig, axs = plt.subplots(3,3)
    
    orders = ["ADJ_SWAP", "JUMP_DOWN", "JUMP_UP"]
    colors = ["blue", "green", "red"]
    bdds = ["quadratic", "diamond", "memo"]
    sizes = [[10000, 30000, 50000],[10000, 30000, 50000], [3000, 6000, 10000] ]

    for b in range(len(bdds)) :
        for s in range(3) :
            results = special_cases_df.loc[special_cases_df["bdd"] == bdds[b]].loc[special_cases_df["n"] == sizes[b][s]]
            for o in range(len(orders)):
                jumps, yax = group_ns_sp_times_per_jump_amount(results, orders[o])
                axs[b][s].plot(jumps, yax, color=colors[o], label=orders[o])
    
    #making pretty:
    #layout
    col_titles = ["Small", "Medium", "Large"]
    row_titles = ["Quadratic", "Diamond", "Memo"]

    for j in range(3):
        axs[0, j].set_title(col_titles[j])
        axs[j, 0].set_ylabel(row_titles[j])

    #shared y-axis per row (kinda cooked for diamond but rest are good)
    for i in range(3):
        for j in range(3):
            axs[i, j].sharey(axs[i, 0])
    
    #enforcing 3 vals per y-axis
    for i in range(3):
        row_axes = axs[i]

        # collect data from row
        row_y = []
        for ax in row_axes:
            for line in ax.get_lines():
                row_y.extend(line.get_ydata())

        ymax = round_up(max(row_y))
        ymax = ymax + 500 if i == 2 else ymax

        for ax in row_axes:
            ax.set_ylim(0, ymax)
            ax.set_yticks([0, ymax/2, ymax])

    #axis titles
    fig.supxlabel("fraction of total jumps")
    fig.supylabel("speed-up with special cases")
    fig.suptitle("Special case running times")
    fig.tight_layout()

    #legend
    handles, labels = axs[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.55, 0.06), ncol=3)
    fig.subplots_adjust(bottom=0.20)
    plt.savefig('test.png')


def picotrav_scatter_normal(buddy_pico_df, adiar_pico_df) :
    buddy_pico_data = buddy_pico_df.loc[buddy_pico_df["approach"] == "NS"].rename(columns={"time (ms)" : "buddy time"})
    adiar_pico_data = adiar_pico_df.loc[adiar_pico_df["approach"] == "NS"].rename(columns={"time (ms)" : "adiar time"})
    cool_combo_table = buddy_pico_data.merge(adiar_pico_data, on=["circuit", "order"])[["circuit", "order", "buddy time", "adiar time"]].sort_values(["circuit", "order"])
    cool_combo_table["circuit"] = cool_combo_table["circuit"].str.removesuffix(".blif")
    cool_combo_table_no_NaNs = cool_combo_table.dropna(subset=["buddy time", "adiar time"]) #remove NaNs
    intermediate = cool_combo_table_no_NaNs.copy()
    epsilon = 1e-3
    intermediate["buddy time"] = intermediate["buddy time"].replace(0,epsilon)  #make 0 into very small value instead

    #scatter plot!
    circuit_names = intermediate["circuit"].unique()
    colors = plt.cm.tab20.colors
    fig, ax = plt.subplots()

    for i, circuit in enumerate(circuit_names):
        circuit_data =  intermediate[intermediate["circuit"] == circuit]

        #plots the data
        ax.scatter(circuit_data["adiar time"], circuit_data["buddy time"], color=colors[i % len(colors)], label = circuit) 

        #middle line
        max_plot_val = max(intermediate["buddy time"].max() , intermediate["adiar time"].max())
        ax.plot([epsilon,max_plot_val], [epsilon,max_plot_val] , color="black") 

        #making pretty
        ax.set_xlim(epsilon, max_plot_val) 
        ax.set_ylim(epsilon, max_plot_val) 
        
        ax.set_xlabel("adiar time")
        ax.set_ylabel("buddy time")
        ax.set_yscale("log")
        ax.set_xscale("log")
        ax.legend()
        plt.savefig("scatter_normal.png")



def picotrav_scatter_slowdown(buddy_pico_df, adiar_pico_df) :
    #pico data for non-mixed approach , buddy and aidar
    buddy_pico_data = buddy_pico_df.loc[buddy_pico_df["approach"] == "NS"].rename(columns={"time (ms)" : "buddy time"})
    adiar_pico_data = adiar_pico_df.loc[adiar_pico_df["approach"] == "NS"].rename(columns={"time (ms)" : "adiar time"}) #without mixed approach

    #combining into one table like [circuit order buddy_time adiar_time]
    cool_combo_table = buddy_pico_data.merge(adiar_pico_data, on=["circuit", "order", "after_sum"])[["circuit", "order", "buddy time", "adiar time" , "after_sum"]].sort_values(["circuit", "order"])
    
    #cleanup 
    cool_combo_table["circuit"] = cool_combo_table["circuit"].str.removesuffix(".blif")
    cool_combo_table_no_NaNs = cool_combo_table.dropna(subset=["buddy time", "adiar time"]) #remove NaNs

    intermediate = cool_combo_table_no_NaNs.copy()
    epsilon = 1e-3
    intermediate["buddy time"] = intermediate["buddy time"].replace(0,epsilon)  #make 0 into very small value instead

    #compute slowdown for the y-axis
    intermediate["slowdown"] = intermediate["adiar time"] / intermediate["buddy time"]

    #scatter plot!
    circuit_names = intermediate["circuit"].unique()
    colors = plt.cm.tab20.colors
    fig, ax = plt.subplots()

    for i, circuit in enumerate(circuit_names):
        circuit_data =  intermediate[intermediate["circuit"] == circuit]

        #plots the data
        ax.scatter(circuit_data["after_sum"], circuit_data["slowdown"], color=colors[i % len(colors)], label = circuit) #plot with after_sum on bottom
        #ax.scatter(circuit_data["adiar_time"], circuit_data["slowdown"], color=colors[i % len(colors)], label = circuit) #plot with adiar time on bottom

        #middle line
        max_plot_val = max(intermediate["slowdown"].max() , intermediate["adiar time"].max())
        plt.axhline(y=0.5, color='black', linestyle='-') #for slowdown scatter

        #making pretty
        ax.set_xlim(0.1, max_plot_val) 
        ax.set_ylim(0.1, max_plot_val) 
        
        ax.set_xlabel("size after reorder")
        ax.set_ylabel("adiar time / buddy time")
        ax.set_yscale("log")
        ax.set_xscale("log")
        ax.legend()
        plt.savefig("scatter_slowdown.png")

##plots for scalable examples buddy vs adiar
## we do have data for this right??


def main() :
    #expect - given path for buddy and adiar
    args = sys.argv[1:]
    buddy_path = args[0] 
    adiar_path = args[1] 

    special_path = f"{adiar_path}/replace/bdd"
    adiar_pico_path = f"{adiar_path}/picotrav_replace/bdd"
    buddy_pico_path = f"{buddy_path}/picotrav_replace/bdd"

    #read data
    special_data , special_broken = analyser.read_all_data(special_path, analyser.Benchmark.SPECIAL)
    adiar_pico_data , adiar_pico_broken = analyser.read_all_data(adiar_pico_path, analyser.Benchmark.PICO)
    buddy_pico_data , buddy_pico_broken = analyser.read_all_data(buddy_pico_path, analyser.Benchmark.PICO)

    #build data frames..
    special_rows = analyser.extract_rep_special(special_data, special_broken)
    adiar_pico_rows = analyser.extract_rep_pico(adiar_pico_data, adiar_pico_broken)
    buddy_pico_rows = analyser.extract_rep_pico(buddy_pico_data, buddy_pico_broken)

    special_df = pd.DataFrame(special_rows ).sort_values(by=["bdd", "order", "n", "ns", "jumps"])
    adiar_pico_df = pd.DataFrame(adiar_pico_rows).sort_values(by=["approach", "circuit", "order"])
    buddy_pico_df = pd.DataFrame(buddy_pico_rows).sort_values(by=["approach", "circuit", "order"])

    #drawing graphs
    special_case_plots(special_df)
    picotrav_scatter_normal(buddy_pico_df , adiar_pico_df)
    picotrav_scatter_slowdown(buddy_pico_df , adiar_pico_df)

if __name__ == "__main__":
    main()