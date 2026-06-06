
import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
import analyser
import sys

#fancy style stuff TM
colors = ["#F5F600", "#C9F400", "#00E33A", "#00D154","#00B06D","#00857B","#00697D","#24517D","#2E3F7C","#3C1678","#440068","#3E0046"]
colors_better = ["#332288", "#88CCEE", "#44AA99", "#117733",  "#999933", "#DDCC77", "#CC6677", "#882255", "#AA4499", "#EECC77", "#EE6677"]
col3 = ["#AE0060", "#00AA82", "#FF00AD", "#00FFD1", "#9F00CF", "#356DFD", "#00BCFC", "#FF91FE", "#F40020", "#FF5A21", "#FFCC1E"]
col_circ_map = {"adder" : col3[0], "arbiter" : col3[1], "cavlc" : col3[2], "ctrl" : col3[3], "dec" : col3[4], 
                "i2c" : col3[5], "int2float" : col3[6], "mem_ctrl" : col3[7], "router" : col3[8], "sin" : col3[9], "voter" : col3[10]}
colors_special = ["#00D8F5", "#3D59F3", "#FF8000"]
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
    bdds = ["quadratic", "diamond", "memo"]
    sizes = [[10000, 30000, 50000],[10000, 30000, 50000], [3000, 6000, 10000] ]

    for b in range(len(bdds)) :
        for s in range(3) :
            results = special_cases_df.loc[special_cases_df["bdd"] == bdds[b]].loc[special_cases_df["n"] == sizes[b][s]]
            for o in range(len(orders)):
                jumps, yax = group_ns_sp_times_per_jump_amount(results, orders[o])
                axs[b][s].plot(jumps, yax, color=colors_special[o], label=orders[o])
    
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
    buddy_pico_data = buddy_pico_df.loc[buddy_pico_df["approach"] == "NORMAL"].rename(columns={"time (ms)" : "buddy time"})
    adiar_pico_data = adiar_pico_df.loc[adiar_pico_df["approach"] == "NORMAL"].rename(columns={"time (ms)" : "adiar time"})
    cool_combo_table = buddy_pico_data.merge(adiar_pico_data, on=["circuit", "order"])[["circuit", "order", "buddy time", "adiar time"]].sort_values(["circuit", "order"])
    cool_combo_table["circuit"] = cool_combo_table["circuit"].str.removesuffix(".blif")
    cool_combo_table_no_NaNs = cool_combo_table.dropna(subset=["buddy time", "adiar time"]) #remove NaNs
    intermediate = cool_combo_table_no_NaNs.copy()
    epsilon = 1e-3
    intermediate["buddy time"] = intermediate["buddy time"].replace(0,epsilon)  #make 0 into very small value instead (for log axis)
    intermediate["adiar time"] = intermediate["adiar time"].replace(0,epsilon)  #make 0 into very small value instead (for log axis)

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



def picotrav_scatter_slowdown(other_pico_df, adiar_pico_df, other_name) :

    #attempting to save the timeout rows...
    lookup = (
    pd.concat([other_pico_df[["circuit", "before_sum"]],
               adiar_pico_df[["circuit", "before_sum"]]])
    .groupby("circuit")["before_sum"]
    .agg(lambda s: s.dropna().iloc[0] if not s.dropna().empty else pd.NA)
    )

    # Fill NaN before_sums in each dataframe
    other_pico_df["before_sum"] = other_pico_df["before_sum"].fillna(other_pico_df["circuit"].map(lookup))
    adiar_pico_df["before_sum"] = adiar_pico_df["before_sum"].fillna(adiar_pico_df["circuit"].map(lookup))

    #pico data for non-mixed approach , buddy and aidar
    other_pico_data = other_pico_df.loc[other_pico_df["approach"] == "NORMAL"].rename(columns={"time (ms)" : f"{other_name} time"})
    adiar_pico_data = adiar_pico_df.loc[adiar_pico_df["approach"] == "NORMAL"].rename(columns={"time (ms)" : "adiar time"}) #without mixed approach

    #combining into one table like [circuit order buddy_time adiar_time ]
    #adiar_buddy = other_pico_data.merge(adiar_pico_data, on=["circuit", "order", "after_sum", "before_sum", "identity_order"])[["circuit", "order", f"{other_name} time", "adiar time" , "after_sum", "before_sum","identity_order"]].sort_values(["circuit", "order"])
    adiar_buddy = other_pico_data.merge(adiar_pico_data, on=["circuit", "order", "before_sum", "identity_order"])[["circuit", "order", f"{other_name} time", "adiar time", "before_sum","identity_order"]].sort_values(["circuit", "order"])

    #cleanup circuit names
    adiar_buddy["circuit"] = adiar_buddy["circuit"].str.removesuffix(".blif")

    #remove any circuit where one thing was NaN
    adiar_buddy_nn = adiar_buddy.dropna(subset=[f"{other_name} time", "adiar time"]).copy() #remove NaNs
    adiar_buddy_nn = adiar_buddy_nn.fillna({"identity_order" : False})
    ab_nn = adiar_buddy_nn.copy()
    
    #compute slowdown for the y-axis
    ab_nn["slowdown"] = (ab_nn["adiar time"] +1) / (ab_nn[f"{other_name} time"] +1)
    
    
    #filter identity orders
    ab_nn_norm = ab_nn.loc[(ab_nn["identity_order"] == False)].copy()
    
    #tendency line more valid
    # Initial fit
    x = ab_nn_norm["before_sum"].to_numpy()
    y = ab_nn_norm["slowdown"].to_numpy()
    coeffs = np.polyfit(x, y, 1)
    trend_y = np.polyval(coeffs, x) #clean trendline

    # Calculate residuals and standard deviation
    residuals = np.abs(y - trend_y) # how far away points are from actual trend line (trend_y)
    std_dev = np.std(residuals) # stadard deviation of residuals

    # points that lie very far from standard deviation weighted less?
    weights =  np.exp(-(residuals / (3 * std_dev))**2)
    weights = np.clip(weights, 0.5, 1.0) #makign sure no weight is below 0.1 (so no points are completely ignored)

    #new weighted trenline (also takign into account log factor on axes)
    z = np.polyfit(np.log10(x), np.log10(y), 1, w=weights)
    p = np.poly1d(z)

    x_longer_line = np.arange(100, 100000000, 100000) #for plotting long line
    log10_y_fit = p(np.log10(x_longer_line))

    #scatter plot!"""
    circuit_names = ab_nn_norm["circuit"].unique()
    fig, ax = plt.subplots()

    for i, circuit in enumerate(circuit_names):
        ab_circuit_data_norm =  ab_nn_norm [ab_nn_norm ["circuit"] == circuit]
        time_outs = ab_circuit_data_norm.loc[(ab_circuit_data_norm["adiar time"] == 2880000.0) | (ab_circuit_data_norm[f"{other_name} time"] == 2880000.0)]
        actual = ab_circuit_data_norm.loc[(ab_circuit_data_norm["adiar time"] != 2880000.0) & (ab_circuit_data_norm[f"{other_name} time"] != 2880000.0)]

        #plots the data
        if (len(actual) > 0) :
            ax.scatter(round(actual["before_sum"]), actual["slowdown"], 
                    color=col_circ_map[circuit], label = f"{circuit} ({len(actual)})", alpha=0.5 )
        if (len(time_outs) > 0) :
            ax.scatter(round(time_outs["before_sum"]), time_outs["slowdown"], 
                    color=col_circ_map[circuit], label = f"{circuit} ({len(time_outs)})", alpha=0.5, marker = "x" )

    #making pretty
    ax.set_xlim(100, 100000000) 
    ax.set_ylim(0.1, 20000) 
    
    ax.set_xlabel("Size before reorder (#nodes)", fontsize=20)
    ax.set_ylabel(f"Adiar time / {other_name} time", fontsize=20)
    ax.set_yscale("log")
    ax.set_xscale("log")
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=14)
    

    plt.axvline(x = 10000, linestyle='dashed', color=adiar_color) # BDD size lines 10^4 node input size -> 24000 bytes = 24000/1024 KiB ~ 23,5 KiB 
    plt.annotate("23.5 KiB", xy=(11000, 3000), color=adiar_color, rotation = 90)
    plt.plot(x_longer_line, 10**log10_y_fit, color="#B0B2B4", linestyle='dashed') # tendency line
    plt.axhline(y=1, color='black', linestyle='-') #factor 1 line
    plt.grid()
    plt.savefig(f"scatter_slowdown_{other_name}.png", pad_inches=0.5,bbox_inches="tight", dpi=300)

##plots for scalable examples buddy vs adiar

def time_N_plots2(adiar_rep_df, buddy_rep_df, cudd_rep_df, bdd, size_pair) :
    plt.rcParams.update({'font.size': 14})
    adiar_data = adiar_rep_df.loc[adiar_rep_df["bdd"] == bdd].rename(columns={"time (ms)" : "adiar time"}).dropna(subset=["adiar time"]).sort_values(["bdd", "n"])
    buddy_data = buddy_rep_df.loc[buddy_rep_df["bdd"] == bdd].rename(columns={"time (ms)" : "buddy time"}).dropna(subset=["buddy time"]).sort_values(["bdd", "n"])
    cudd_data = cudd_rep_df.loc[cudd_rep_df["bdd"] == bdd].rename(columns={"time (ms)" : "cudd time"}).dropna(subset=["cudd time"]).sort_values(["bdd", "n"])
    fig, ax = plt.subplots()

    ax.plot(adiar_data["n"], adiar_data["adiar time"]+0.1, label="Adiar", marker='o', color=adiar_color)
    ax.plot(buddy_data["n"], buddy_data["buddy time"]+0.1, label="BuDDy", marker='^', color=buddy_color)
    ax.plot(cudd_data["n"], cudd_data["cudd time"]+0.1, label="CuDD", marker='s', color=cudd_color)

    place = 20 if bdd == "memo" else -45
    size = adiar_data["af_size"].tolist()[-2] if bdd == "diamond" else  cudd_data["af_size"].tolist()[-1]
    plt.annotate(f"{round(adiar_data["af_size"].tolist()[-1]*24/size_pair[0])} {size_pair[1]}",
                 (adiar_data["n"].tolist()[-1], adiar_data["adiar time"].tolist()[-1]),textcoords="offset points",xytext=(2,-45),ha='center', color=adiar_color, rotation = 90)
    plt.annotate(f"{round(buddy_data["af_size"].tolist()[-1]*24/size_pair[0])} {size_pair[1]}",
                 (buddy_data["n"].tolist()[-1], buddy_data["buddy time"].tolist()[-1]),textcoords="offset points",xytext=(2,-40),ha='center', color=buddy_color, rotation = 90)
    plt.annotate(f"{round(size*32/size_pair[0])} {size_pair[1]}",
                 (cudd_data["n"].tolist()[-1], cudd_data["cudd time"].tolist()[-1]),textcoords="offset points",xytext=(2,place),ha='center', color=cudd_color, rotation = 90)
    
    ax.set_xlabel("Instance size N", fontsize=20)
    ax.set_yscale("log")
    ax.set_ylabel("time (ms)", fontsize=20)
    ax.set_title(bdd.capitalize(), fontsize=30)
    
    plt.grid()
    plt.legend(fontsize=20)
    plt.savefig(f"time_chart_{bdd}.png")

#buddy compose vs replace
def buddy_comp() :
    ns = [i*250 for i in range(1,13)]
    rep_times = [102, 737, 2395, 5939, 11251, 20475, 33529, 51757, 75718, 107554, 148859, 200196]
    compose_times = [11, 67, 133, 259, 263, 509, 513, 655, 964, 1240, 1609, 1829]
    adiar_times = [401, 892, 1657, 2325, 3463, 4507, 5525, 6981, 8448, 10527, 12471, 14033]
    fig, ax = plt.subplots()
    ax.plot(ns, rep_times, linestyle='-', marker='s', label="bdd_replace", color="#00D8F5")
    ax.plot(ns, compose_times, linestyle='-', marker='s', label="bdd_compose", color="#3D59F3")
    ax.plot(ns, adiar_times, linestyle='-', marker='o', label="adiar", color="black")
    ax.set_xlabel("Instance size N", fontsize=20)
    ax.set_ylabel("Time (ms)", fontsize=20)
    fig.tight_layout()
    plt.legend()
    plt.grid()
    plt.savefig("buddy_comp.png")

def quad_transpose_ns_times(adiar_special_data) : 
    qd = adiar_special_data.loc[(adiar_special_data["bdd"] == "quadratic") & (adiar_special_data["order"] == "JUMP_DOWN") & (adiar_special_data["ns"] == 1)]
    fig, ax = plt.subplots()
    ax.plot(qd["n"], qd["time (ms)"], ".")
    ax.set_yscale("log")
    plt.grid()
    plt.savefig("quad_adiar_transpose.png")

def read_to_df(path, kind, order) :
    data, broken = analyser.read_all_data(path, kind)
    if (kind == analyser.Benchmark.PICO) :
        print(path)
        for b in broken :
            print(b)
    rows = analyser.extract_rep_special(data, broken) if (kind == analyser.Benchmark.SPECIAL) else analyser.extract_rep_pico(data, broken)
    df = pd.DataFrame(rows).sort_values(by=order)
    return df

def main() :
    #expect - given path for buddy and adiar
    args = sys.argv[1:]
    buddy_path = args[0] 
    adiar_path = args[1] 
    cudd_path = args[2]

    special_path = f"{adiar_path}/replace/bdd"
    adiar_pico_path = f"{adiar_path}/picotrav_replace/bdd"
    buddy_pico_path = f"{buddy_path}/picotrav_replace/bdd"
    cudd_pico_path = f"{cudd_path}/picotrav_replace/bdd"
    adiar_scale_path = f"{adiar_path}/replace_scalable/bdd"
    buddy_scale_path = f"{buddy_path}/replace_scalable/bdd"
    cudd_scale_path = f"{cudd_path}/replace_scalable/bdd"

    #special cases
    special_df = read_to_df(special_path, analyser.Benchmark.SPECIAL, ["bdd", "order", "n", "ns", "jumps"])
    #pico
    adiar_pico_df = read_to_df(adiar_pico_path, analyser.Benchmark.PICO, ["approach", "circuit", "order"])
    buddy_pico_df = read_to_df(buddy_pico_path, analyser.Benchmark.PICO, ["approach", "circuit", "order"])
    cudd_pico_df = read_to_df(cudd_pico_path, analyser.Benchmark.PICO, ["approach", "circuit", "order"])
    #scalable
    adiar_scalable_df = read_to_df(adiar_scale_path,  analyser.Benchmark.SPECIAL, ["bdd"])
    buddy_scalable_df = read_to_df(buddy_scale_path,  analyser.Benchmark.SPECIAL, ["bdd"])
    cudd_scalable_df = read_to_df(cudd_scale_path,  analyser.Benchmark.SPECIAL, ["bdd"])

    with pd.option_context(
    "display.max_rows", None, "display.max_columns", None, "display.width", 1000): 
        print(adiar_pico_df)
        print(cudd_pico_df)
        print(adiar_pico_df)

    #drawing graphs
    special_case_plots(special_df)
    picotrav_scatter_slowdown(buddy_pico_df , adiar_pico_df, "BuDDy")
    picotrav_scatter_slowdown(cudd_pico_df , adiar_pico_df, "CUDD")
    time_N_plots2(adiar_scalable_df, buddy_scalable_df, cudd_scalable_df, "quadratic", [1024, "KiB"])
    time_N_plots2(adiar_scalable_df, buddy_scalable_df, cudd_scalable_df, "diamond", [1048576, "MiB"])
    time_N_plots2(adiar_scalable_df, buddy_scalable_df, cudd_scalable_df, "memo", [1024, "KiB"])
    time_N_plots2(adiar_scalable_df, buddy_scalable_df, cudd_scalable_df, "diamond_full", [1024, "KiB"])
    buddy_comp()
    quad_transpose_ns_times(special_df)



    #transposition experiments 2.0 - run locally
    path = "../results2"
    res , broken = analyser.read_all_data(path, analyser.Benchmark.SPECIAL)
    print(f"there are no broken? {len(broken)}")
    rows = analyser.extract_rep_special(res, broken)
    df = pd.DataFrame(rows).sort_values(by=["package", "n"])
    dfa = df.loc[df["package"] == "Adiar"].reset_index(drop=True)
    dfc = df.loc[df["package"] == "CUDD"].reset_index(drop=True)
    fac = dfa["time (ms)"] / dfc["time (ms)"]

    fig, ax = plt.subplots(1,2)
    ax[0].plot(dfa["n"], dfa["time (ms)"], color="black")
    ax[0].plot(dfc["n"], dfc["time (ms)"], color="red")
    ax[0].set_ylim(1000, 1000000)
    ax[0].set_yscale("log")

    ax[1].plot(dfa["n"], fac)
    plt.savefig("q_trans.png")



    #table data
    #scalable average calc per benchmark
    """
    bdds = ["quadratic", "diamond", "memo"]
    for bdd in bdds :
        inst_adiar = adiar_scalable_df.loc[adiar_scalable_df["bdd"] == bdd].rename(columns={"time (ms)" : "adiar time"}).reset_index(drop=True)
        inst_buddy = buddy_scalable_df.loc[buddy_scalable_df["bdd"] == bdd].rename(columns={"time (ms)" : "buddy time"}).reset_index(drop=True)
        inst_cudd = cudd_scalable_df.loc[cudd_scalable_df["bdd"] == bdd].rename(columns={"time (ms)" : "cudd time"}).reset_index(drop=True)

        combined = pd.concat([
            inst_adiar[["bdd", "n", "adiar time"]],
            inst_buddy[["bdd", "n", "buddy time"]],
            inst_cudd[["bdd", "n", "cudd time"]]
        ])
        combined["n"] = combined["n"].astype(int)
        combined = combined.groupby("n", as_index=False).sum(min_count=1).sort_values("n")

        #factor columns
        combined["ab"] = (combined["adiar time"]+1) / (combined["buddy time"] +1)
        combined["ac"] = (combined["adiar time"]+1) / (combined["cudd time"] +1)
       
        print(f"{bdd} : avg slowdown ab: {combined["ab"].mean()}")
        print(f"{bdd} : avg slowdown ac: {combined["ac"].mean()}")
    print()
    # pico: avg slowdown per circuit
    circs = adiar_pico_df["circuit"].unique()
    for c in circs :
        inst_adiar = adiar_pico_df.loc[adiar_pico_df["circuit"] == c].rename(columns={"time (ms)" : "adiar time"}).reset_index(drop=True)
        inst_buddy = buddy_pico_df.loc[buddy_pico_df["circuit"] == c].rename(columns={"time (ms)" : "buddy time"}).reset_index(drop=True)
        inst_cudd = cudd_pico_df.loc[cudd_pico_df["circuit"] == c].rename(columns={"time (ms)" : "cudd time"}).reset_index(drop=True)

        combined = pd.concat([
            inst_adiar[["circuit", "order", "output gates", "adiar time"]],
            inst_buddy[["circuit", "order", "output gates","buddy time"]],
            inst_cudd[["circuit", "order", "output gates", "cudd time"]]
        ])
        # Keep one copy of output gates (same across all three, so just take first)
        output_gates = combined.groupby("order", as_index=False)["output gates"].first()

        # Sum only the time columns
        times = combined.groupby("order", as_index=False)[["adiar time", "buddy time", "cudd time"]].sum(min_count=1)

        combined = times.merge(output_gates, on="order")
        #combined = combined.groupby("order", as_index=False).sum(min_count=1)
        
        combined["ab"] = (combined["adiar time"]+1) / (combined["buddy time"] +1)
        combined["ac"] = (combined["adiar time"]+1) / (combined["cudd time"] +1)
        combined["time per output"] = (combined["adiar time"]) / (combined["output gates"])
        print(combined)
        print(f"{c} : avg slowdown ab: {combined["ab"].mean()}")
        print(f"{c} : avg slowdown ac: {combined["ac"].mean()}")
        print(f"{c} : per bdd time: {combined["time per output"].tolist()}")
    """

    

if __name__ == "__main__":
    main()