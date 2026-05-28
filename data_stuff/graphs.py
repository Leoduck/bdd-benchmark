
import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
import analyser
import sys

#fancy style stuff TM
colors = ["#F5F600", "#C9F400", "#00E33A", "#00D154","#00B06D","#00857B","#00697D","#24517D","#2E3F7C","#3C1678","#440068","#3E0046"]
adiar_color = "#1F1F14"
buddy_color = "#F60000"
cudd_color = "#1000F6"
plt.rc('font',family='TeX Gyre Schola')

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
    sub_colors = ["#00D8F5", "#3D59F3", "#FF8000"]
    bdds = ["quadratic", "diamond", "memo"]
    sizes = [[10000, 30000, 50000],[10000, 30000, 50000], [3000, 6000, 10000] ]

    for b in range(len(bdds)) :
        for s in range(3) :
            results = special_cases_df.loc[special_cases_df["bdd"] == bdds[b]].loc[special_cases_df["n"] == sizes[b][s]]
            for o in range(len(orders)):
                jumps, yax = group_ns_sp_times_per_jump_amount(results, orders[o])
                axs[b][s].plot(jumps, yax, color=sub_colors[o], label=orders[o])
    
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
            ax.set_yscale("log")
            ax.set_ylim(10, 100000)
            ax.set_yticks([10,100,1000,10000,100000])
            

    #axis titles
    fig.supxlabel("Fraction of possible jumps")
    fig.supylabel("Speed-up with special cases")
    fig.tight_layout()

    #legend
    handles, labels = axs[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.55, 0.06), ncol=3)
    fig.subplots_adjust(bottom=0.20)
    plt.savefig('special.png')


def picotrav_scatter_normal(buddy_pico_df, adiar_pico_df) :
    buddy_pico_data = buddy_pico_df.loc[buddy_pico_df["approach"] == "NS"].rename(columns={"time (ms)" : "buddy time"})
    adiar_pico_data = adiar_pico_df.loc[adiar_pico_df["approach"] == "NS"].rename(columns={"time (ms)" : "adiar time"})
    cool_combo_table = buddy_pico_data.merge(adiar_pico_data, on=["circuit", "order"])[["circuit", "order", "buddy time", "adiar time"]].sort_values(["circuit", "order"])
    cool_combo_table["circuit"] = cool_combo_table["circuit"].str.removesuffix(".blif")
    cool_combo_table_no_NaNs = cool_combo_table.dropna(subset=["buddy time", "adiar time"]) #remove NaNs
    intermediate = cool_combo_table_no_NaNs.copy()
    epsilon = 1e-3
    intermediate["buddy time"] = intermediate["buddy time"].replace(0,epsilon)  #make 0 into very small value instead (for log axis)

    #scatter plot!
    circuit_names = intermediate["circuit"].unique()
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

def time_N_plots2(adiar_rep_df, buddy_rep_df, cudd_rep_df, bdd, size_pair) :
    adiar_data = adiar_rep_df.loc[adiar_rep_df["bdd"] == bdd].rename(columns={"time (ms)" : "adiar time"}).dropna(subset=["adiar time"]).sort_values(["bdd", "n"])
    buddy_data = buddy_rep_df.loc[buddy_rep_df["bdd"] == bdd].rename(columns={"time (ms)" : "buddy time"}).dropna(subset=["buddy time"]).sort_values(["bdd", "n"])
    cudd_data = cudd_rep_df.loc[cudd_rep_df["bdd"] == bdd].rename(columns={"time (ms)" : "cudd time"}).dropna(subset=["cudd time"]).sort_values(["bdd", "n"])
    fig, ax = plt.subplots()

    ax.plot(adiar_data["n"], adiar_data["adiar time"].replace(0,1e-3), label="Adiar", marker='o', color=adiar_color)
    ax.plot(buddy_data["n"], buddy_data["buddy time"].replace(0,1e-3), label="BuDDy", marker='^', color=buddy_color)
    ax.plot(cudd_data["n"], cudd_data["cudd time"].replace(0,1e-3), label="CuDD", marker='s', color=cudd_color)

    plt.annotate(f"{adiar_data["af_size"].tolist()[-1]/24/size_pair[0]} {size_pair[1]}",(adiar_data["n"].tolist()[-1], adiar_data["adiar time"].tolist()[-1]),textcoords="offset points",xytext=(0,10),ha='center', color=adiar_color)
    #plt.annotate("test",(buddy_data["n"].tolist()[-1], buddy_data["buddy time"].tolist()[-1]),textcoords="offset points",xytext=(0,10),ha='center', color=buddy_color)
    plt.annotate(f"{cudd_data["af_size"].tolist()[-1]/32/size_pair[0]} {size_pair[1]}",(cudd_data["n"].tolist()[-1], cudd_data["cudd time"].tolist()[-1]),textcoords="offset points",xytext=(0,-10),ha='center', color=cudd_color)
    
    ax.set_xlabel("Instance size N")
    ax.set_yscale("log")
    ax.set_ylabel("time (ms)")

    plt.grid()
    plt.legend()
    plt.savefig(f"time_chart_{bdd}.png")


def time_N_plots(buddy_rep_df, adiar_rep_df):
    #assuming a tables like [bdd N time ...] for buddy and adiar..?
    buddy_data = buddy_rep_df.rename(columns={"time (ms)" : "buddy time"}).sort_values(["bdd", "n"]) 
    adiar_data = adiar_rep_df.rename(columns={"time (ms)" : "adiar time"}).sort_values(["bdd", "n"])

    print(adiar_data)
    print("\n\n\n")
    print(buddy_data)
    bdds = adiar_data["bdd"].unique()
    print(bdds)

    #making 3 (maybe 4) plots - one for eack kind of bdd
    fig, ax = plt.subplots(3,1)
    for i, bdd in enumerate(bdds):
        #getting bdd specific data, cleaning up NaNs
        adiar_bdd_data = adiar_data.loc[adiar_data["bdd"] == bdd].dropna(subset=["adiar time"])
        buddy_bdd_data = buddy_data.loc[buddy_data["bdd"] == bdd].dropna(subset=["buddy time"])
        
        ax[i].plot(buddy_bdd_data["n"], buddy_bdd_data["buddy time"], label="BuDDy", marker='o')
        ax[i].plot(adiar_bdd_data["n"], adiar_bdd_data["adiar time"], label="Adiar", marker='o')

        ax[i].set_xlabel("Instance size N")
        ax[i].set_yscale("log")
        ax[i].set_ylabel("time (ms)")
        #ax[i].yaxis.get_major_formatter().set_scientific(False)
    plt.legend()
    plt.savefig("time_charts.png")

#buddy compose vs replace
def buddy_comp() :
    ns = [i*250 for i in range(1,13)]
    rep_times = [102, 737, 2395, 5939, 11251, 20475, 33529, 51757, 75718, 107554, 148859, 200196]
    compose_times = [11, 67, 133, 259, 263, 509, 513, 655, 964, 1240, 1609, 1829]
    fig, ax = plt.subplots()
    ax.plot(ns, rep_times, linestyle='-', marker='o', label="bdd_replace", color="#00D8F5")
    ax.plot(ns, compose_times, linestyle='-', marker='o', label="bdd_compose", color="#3D59F3")
    ax.set_xlabel("Instance size N")
    ax.set_ylabel("time (ms)")
    #ax.set_yscale("log")
    #ax.set_xscale("log")
    plt.legend()
    plt.grid()
    plt.savefig("buddy_comp.png")

def main() :
    #expect - given path for buddy and adiar
    args = sys.argv[1:]
    buddy_path = args[0] 
    adiar_path = args[1] 
    cudd_path = args[2]

    special_path = f"{adiar_path}/replace/bdd"
    adiar_pico_path = f"{adiar_path}/picotrav_replace/bdd"
    buddy_pico_path = f"{buddy_path}/picotrav_replace/bdd"
    adiar_scale_path = f"{adiar_path}/replace_scalable/bdd"
    buddy_scale_path = f"{buddy_path}/replace_scalable/bdd"
    cudd_scale_path = f"{cudd_path}/replace_scalable/bdd"

    #read data
    special_data , special_broken = analyser.read_all_data(special_path, analyser.Benchmark.SPECIAL)
    """adiar_pico_data , adiar_pico_broken = analyser.read_all_data(adiar_pico_path, analyser.Benchmark.PICO)
    buddy_pico_data , buddy_pico_broken = analyser.read_all_data(buddy_pico_path, analyser.Benchmark.PICO)"""
    buddy_scale_data, buddy_scale_broken = analyser.read_all_data(buddy_scale_path, analyser.Benchmark.SPECIAL)
    adiar_scale_data, adiar_scale_broken = analyser.read_all_data(adiar_scale_path, analyser.Benchmark.SPECIAL)
    cudd_scale_data, cudd_scale_broken = analyser.read_all_data(cudd_scale_path, analyser.Benchmark.SPECIAL)

    #build data frames..
    special_rows = analyser.extract_rep_special(special_data, special_broken)
    """adiar_pico_rows = analyser.extract_rep_pico(adiar_pico_data, adiar_pico_broken)
    buddy_pico_rows = analyser.extract_rep_pico(buddy_pico_data, buddy_pico_broken)"""
    buddy_scale_rows = analyser.extract_rep_special(buddy_scale_data, buddy_scale_broken)
    adiar_scale_rows = analyser.extract_rep_special(adiar_scale_data, adiar_scale_broken)
    cudd_scale_rows = analyser.extract_rep_special(cudd_scale_data, cudd_scale_broken)

    special_df = pd.DataFrame(special_rows ).sort_values(by=["bdd", "order", "n", "ns", "jumps"])
    """adiar_pico_df = pd.DataFrame(adiar_pico_rows).sort_values(by=["approach", "circuit", "order"])
    buddy_pico_df = pd.DataFrame(buddy_pico_rows).sort_values(by=["approach", "circuit", "order"])"""
    adiar_scalable_df = pd.DataFrame(adiar_scale_rows)
    buddy_scalable_df = pd.DataFrame(buddy_scale_rows)
    cudd_scalable_df = pd.DataFrame(cudd_scale_rows)

    #drawing graphs
    special_case_plots(special_df)
    """picotrav_scatter_normal(buddy_pico_df , adiar_pico_df)
    picotrav_scatter_slowdown(buddy_pico_df , adiar_pico_df)"""
    time_N_plots2(adiar_scalable_df, buddy_scalable_df, cudd_scalable_df, "quadratic", [1024, "KiB"])
    time_N_plots2(adiar_scalable_df, buddy_scalable_df, cudd_scalable_df, "diamond", [1048576, "MiB"])
    time_N_plots2(adiar_scalable_df, buddy_scalable_df, cudd_scalable_df, "memo", [1024, "KiB"])
    buddy_comp()

if __name__ == "__main__":
    main()