# =========================================================================== #
# User Inputs
# =========================================================================== #
import os
from enum import Enum
yes_choices = ['yes', 'y']
no_choices = ['no', 'n']

# =========================================================================== #
# BDD Packages and their supported Diagrams.
# =========================================================================== #

dd_t = Enum('dd_t', ['bdd', 'bcdd', 'zdd'])

dd_choice = []
for dd in dd_t:
    if input(f"Include '{dd.name.upper()}' benchmarks? (yes/No): ").lower() in yes_choices:
        dd_choice.append(dd)

if not dd_choice:
    print("\n  At least one kind of Decision Diagram should be included!")
    exit(1)

package_t = Enum('package_t', ['adiar', 'buddy',
                 'cal', 'cudd', 'libbdd', 'oxidd', 'sylvan'])

package_dd = {
    package_t.adiar: [dd_t.bdd, dd_t.zdd],
    package_t.buddy: [dd_t.bdd],
    package_t.cal: [dd_t.bcdd],
    package_t.cudd: [dd_t.bcdd, dd_t.zdd],
    package_t.libbdd: [dd_t.bdd],
    package_t.oxidd: [dd_t.bdd, dd_t.bcdd, dd_t.zdd],
    package_t.sylvan: [dd_t.bcdd]
}

print("")

package_choice = []

for p in package_t:
    if any(dd in package_dd[p] for dd in dd_choice):
        if input(f"Include '{p.name}' package? (yes/No): ").lower() in yes_choices:
            package_choice.append(p)

if not package_choice:
    print("\n  At least one Library should be included!")
    exit(1)

bdd_packages = []
if dd_t.bdd in dd_choice:
    bdd_packages = [p for p in package_choice if dd_t.bdd in package_dd[p]]

bcdd_packages = []
if dd_t.bcdd in dd_choice:
    bcdd_packages = [p for p in package_choice if dd_t.bcdd in package_dd[p]]

zdd_packages = []
if dd_t.zdd in dd_choice:
    zdd_packages = [p for p in package_choice if dd_t.zdd in package_dd[p]]

print("\nPackages")
print("  BDD: ", [p.name for p in bdd_packages])
print("  BCDD:", [p.name for p in bcdd_packages])
print("  ZDD: ", [p.name for p in zdd_packages])

# =========================================================================== #
# Benchmark Instances
# =========================================================================== #

# --------------------------------------------------------------------------- #


def mcnet__args(path, merge):
    assert (os.path.exists(f"../../{path}"))
    return f"-f ../{path} -a reach -a dead -a scc -o sloan{' -s async' if merge else ''}"


# --------------------------------------------------------------------------- #
# For the Picotrav benchmarks, we need to obtain the 'depth' and 'size'
# optimised circuit for each of the given spec circuits.
# --------------------------------------------------------------------------- #

epfl_spec_t = Enum('epfl_spec_t',    ['arithmetic', 'random_control'])
epfl_opt_t = Enum('epfl_opt_t',     ['depth', 'size'])
picotrav_opt_t = Enum('picotrav_opt_t', [
                      'DF', 'INPUT', 'LEVEL', 'LEVEL_DF', 'RANDOM', 'FUJITA', 'FANIN', 'FANIN_DF', 'ZIP'])


def picotrav__spec(spec_t, circuit_name):
    return f"../epfl/{spec_t.name}/{circuit_name}.blif"


def picotrav__opt(opt_t, circuit_name):
    circuit_file = [f for f
                    in os.listdir(f"../../epfl/best_results/{opt_t.name}")
                    if f.startswith(circuit_name)][0]
    return f"../epfl/best_results/{opt_t.name}/{circuit_file}"


def picotrav__args(spec_t, opt_t, circuit_name, picotrav_opt, mix_case = "NS"):
    # -f {picotrav__opt(opt_t, circuit_name)}"
    return f"-o {picotrav_opt.name} -f {picotrav__spec(spec_t, circuit_name)} -a {mix_case}"

# --------------------------------------------------------------------------- #


def qbf__args(circuit_name):
    # All of Irfansha Shaik's circuits seem to be output in a depth-first order.
    return f"-o df -f ../SAT2023_GDDL/QBF_instances/{circuit_name}.qcir"


# --------------------------------------------------------------------------- #
relprod_dir_t = Enum('relprod_dir_t', ['NEXT', 'PREV'])


def relnext__args(path, magnitude, dir_t):
    return f"-r ../mcnet/mcc/{path}/relation.bdd -s ../mcnet/mcc/{path}/states_{magnitude}.bdd -o {dir_t.name}"


# special cases
"""
    "replace": {
            dd_t.bdd: [
                [ [ 0, 0, 30], "-n 10 -t diamond -o ADJ_SWAP  -j 10" ],
                [ [ 0, 0, 30], "-n 10 -t diamond -o JUMP_DOWN -j 10" ],
                [ [ 0, 0, 30], "-n 10 -t diamond -o JUMP_UP   -j 10" ],
                ]
            },
"""


small_instance = [10000, 10000, 3000]
mid_instance = [30000, 30000, 6000]
large_instance = [50000, 50000, 10000]
names = ["quadratic", "diamond", "memo"]
test = [small_instance, mid_instance, large_instance]
times = [[0, 0, 5], [0, 0, 5], [0, 0, 5]]
times_ns = [[0, 0, 10], [0, 0, 20], [0, 1, 0]]
step = 10 #more smooth graphs this way even if many more files.. 
r = "-r 1"
m = {}
l = []
for i in range(len(names)):
    # loop over instance
    inst = names[i]
    for j in range(len(test)):
        # loop over size
        n = test[j][i]  # for both 0 would be small instance of quad
        actual_n = 0
        if (inst == "quadratic" or inst == "diamond"):
            actual_n = n*2
        else:
            actual_n = n*2 + 2
        max_jumps = actual_n//3   # // is floor division
        max_swaps = actual_n//2
        for k in range(1, step+1):  # should be 1 to step
            number_jumps = max_jumps//step * k
            number_swaps = max_swaps//step * k
            s = f"-n {n} -t {inst} -o ADJ_SWAP -j {number_swaps} "
            jd = f"-n {n} -t {inst} -o JUMP_DOWN -j {number_jumps} "
            ju = f"-n {n} -t {inst} -o JUMP_UP -j {number_jumps} "

            sn = f"-n {n} -t {inst} -o ADJ_SWAP -j {number_swaps} {r}"
            jdn = f"-n {n} -t {inst} -o JUMP_DOWN -j {number_jumps} {r}"
            jun = f"-n {n} -t {inst} -o JUMP_UP -j {number_jumps} {r}"
            l.append([times[j], s])
            l.append([times[j], jd])
            l.append([times[j], ju])
            l.append([times_ns[j], sn])
            l.append([times_ns[j], jdn])
            l.append([times_ns[j], jun])
m.update({dd_t.bdd: l})

# ---- picotrav job-list ----

arithmetic_benchmarks = ["adder", "sin"]
random_control_benchmarks = ["arbiter", "cavlc", "ctrl", "dec",
                             "i2c", "int2float", "mem_ctrl", "priority", "router", "voter"]
nested_sweeping_mixes = ["NS", "AS_NS", "JD_NS"]

orderings = [
    picotrav_opt_t.LEVEL_DF,
    picotrav_opt_t.INPUT,
    picotrav_opt_t.FANIN,
    picotrav_opt_t.FUJITA,
    picotrav_opt_t.ZIP,
    picotrav_opt_t.RANDOM,
]

pico_replace_list = (
    [
        [[2, 0, 0], picotrav__args(
            epfl_spec_t.arithmetic, epfl_opt_t.size, bench, ordering, mix)]
        for bench in arithmetic_benchmarks
        for ordering in orderings
        for mix in nested_sweeping_mixes
    ] + [
        [[2, 0, 0], picotrav__args(
            epfl_spec_t.random_control, epfl_opt_t.size, bench, ordering, mix)]
        for bench in random_benchmarks
        for ordering in orderings
        for mix in nested_sweeping_mixes
    ]
)

picotrav_rep_jobs = {dd_t.bdd: pico_replace_list}

# --------------------------------------------------------------------------- #
# Since we are testing BDD packages over such a wide spectrum, we have some
# instances that require several days of computaiton time (closing into the 15
# days time limit of the q48 nodes). Yet, the SLURM scheduler does (for good
# reason) not give high priority to jobs with a 15 days time limit. Hence, for
# every instance we should try and schedule it with a time limit that reflects
# the actual computation time(ish).
#
# The following is a list of all instances including their timings.
# --------------------------------------------------------------------------- #
BENCHMARKS = {
    # Benchmark Name
    #    dd_t
    #        Time Limit, Benchmark Arguments
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  #
    #        [DD,HH,MM], "-? ..."
    # ------------------------------------------------------------------------ #

    # ------------------------------------------------------------------------ #
    "picotrav_replace": picotrav_rep_jobs,

    "replace": m,

    "memo_replace": {
        dd_t.bdd: [
            [[0, 0, 30], "-n 10"],
            [[0, 0, 30], "-n 100"],
            [[0, 0, 30], "-n 500"],
            [[0, 0, 30], "-n 1000"],
            [[0, 0, 30], "-n 10000"],
            [[0, 0, 30], "-n 20000"],
            [[0, 2,  0], "-n 40000"],
            [[0, 2,  0], "-n 60000"],
        ]
    },
    "diamond_replace": {
        dd_t.bdd: [
            [[0, 0, 30], "-n 10"],
            [[0, 0, 30], "-n 20"],
            [[0, 0, 30], "-n 30"],
            [[0, 2,  0], "-n 32"],
            [[0, 2,  0], "-n 34"],
            [[1, 0,  0], "-n 36"],
            [[1, 0,  0], "-n 38"],
            [[1, 0,  0], "-n 40"],
            [[1, 0,  0], "-n 42"],
            [[1, 0,  0], "-n 44"],
            [[3, 0, 30], "-n 50"],
        ]
    },
    "replace_quadratic": {
        dd_t.bdd: [
            # [ [ 0, 0, 20], "-n 2000" ],
            # [ [ 0, 0, 20], "-n 4000" ],
            # [ [ 0, 0, 20], "-n 5000" ],
            [[0, 2, 20], "-n 10000"],
            [[0, 2, 20], "-n 20000"],
            [[1, 0,  0], "-n 30000"],
            [[1, 0,  0], "-n 40000"],
            [[2, 0, 20], "-n 50000"],
            [[2, 0, 20], "-n 60000"],
            [[3, 0, 20], "-n 70000"],
            [[4, 0, 20], "-n 80000"],
        ]
    },
    # "replace_quadratic_1": {
    #     dd_t.bdd: [
    #         [ [ 0, 0, 20], "-n 100" ],
    #         [ [ 0, 0, 20], "-n 500" ],
    #         [ [ 0, 0, 20], "-n 1000" ],
    #         [ [ 0, 0, 20], "-n 1500" ],
    #         [ [ 0, 0, 20], "-n 2000" ],
    #         [ [ 0, 0, 20], "-n 3000" ],
    #         [ [ 0, 0, 20], "-n 4000" ],
    #         [ [ 0, 0, 20], "-n 5000" ],
    #     ]
    # },
}

# Copy BDD timings to BCDD timiings
for b in BENCHMARKS.keys():
    if dd_t.bdd in BENCHMARKS[b].keys():
        BENCHMARKS[b][dd_t.bcdd] = BENCHMARKS[b][dd_t.bdd]

print("")

benchmark_choice = []
for b in BENCHMARKS.keys():
    if any(dd in BENCHMARKS[b].keys() for dd in dd_choice):
        if input(f"Include '{b}' Benchmark? (yes/No): ").lower() in yes_choices:
            benchmark_choice.append(b)

bdd_benchmarks = [b for b in benchmark_choice if dd_t.bdd in BENCHMARKS[b].keys(
)] if dd_t.bdd in dd_choice else []
bcdd_benchmarks = [b for b in benchmark_choice if dd_t.bcdd in BENCHMARKS[b].keys(
)] if dd_t.bcdd in dd_choice else []
zdd_benchmarks = [b for b in benchmark_choice if dd_t.zdd in BENCHMARKS[b].keys(
)] if dd_t.zdd in dd_choice else []

print("\nBenchmarks")
print("  BDD: ", bdd_benchmarks)
print("  BCDD:", bcdd_benchmarks)
print("  ZDD: ", zdd_benchmarks)

print("")

# --------------------------------------------------------------------------- #
# To get these benchmarks to not flood the SLURM manager, we need to group them
# together by their time limit (creating an array of jobs for each time limit).
# --------------------------------------------------------------------------- #

partitions = {
    # Mem, CPU
    "q20":    [128, "ivybridge",      15],
    "q20fat": [128, "ivybridge",      15],
    "q24":    [256, "haswell",        28],
    "q28":    [256, "broadwell",      15],
    "q36":    [384, "skylake",        15],
    "q40":    [384, "cascadelake",    15],
    "q48":    [384, "cascadelake",    15],
    "q64":    [512, "icelake-server", 15],
}

partition = "q48"
partition_choice = input("Grendel Node (default: 'q48'): ")
if partition_choice:
    if not partition_choice in partitions.keys():
        print(f"Partition '{partition_choice}' is unknown")
        exit(-1)
    partition = partition_choice

try:
    time_factor = float(input("Time Limit Factor (default: 1.0): "))
except:
    time_factor = 1.0


def time_limit_scale(t):
    hours_to_mins = 60
    days_to_mins = 24 * hours_to_mins

    max_time = partitions[partition][2] * days_to_mins

    total_minutes = t[0] * days_to_mins + t[1] * hours_to_mins + t[2]
    scaled_minutes = min(time_factor * total_minutes, max_time)
    return [
        int(scaled_minutes / days_to_mins),
        int((scaled_minutes % days_to_mins) / hours_to_mins),
        int(scaled_minutes % hours_to_mins)
    ]


def time_limit_str(t):
    minutes = t[2]
    if minutes < 10:
        minutes = f"0{minutes}"

    hours = t[1]
    if hours < 10:
        hours = f"0{hours}"

    days = t[0]
    if days < 10:
        days = f"0{days}"

    return f"{days}-{hours}:{minutes}:{0}{0}"


grouped_instances = {}

for benchmark in BENCHMARKS:
    if benchmark not in benchmark_choice:
        continue

    for dd in BENCHMARKS[benchmark]:
        if dd not in dd_choice:
            continue

        instances = BENCHMARKS[benchmark][dd]
        for instance in instances:
            for p in package_t:
                if p not in package_choice:
                    continue

                if dd in package_dd[p]:
                    time_key = time_limit_str(time_limit_scale(instance[0]))
                    grouped_instances.setdefault(time_key, []).append(
                        [p, benchmark, dd, instance[1]])

print("")

# --------------------------------------------------------------------------- #
# For each benchmark, we need to derive a unique name. This is used for the
# executable and output file.
# --------------------------------------------------------------------------- #


def executable(package, benchmark, dd):
    return f"{package.name}_{benchmark}_{dd.name}"


def benchmark_uid(package, benchmark, dd, args):
    # Remove prefixes
    args_suffix = args.replace('../', '').replace('-', '')
    # Remove parts of AEON benchmarks
    args_suffix = args_suffix.replace('__[biomodels]', '').replace(
        '__[cellcollective]', '').replace('__[ginsim]', '')
    # Replace special characters with '_'
    args_suffix = args_suffix.replace(
        '.', '_').replace(' ', '_').replace('/', '_')
    # Take the last 128 characters to guarantee a limit on length of file names
    args_suffix = args_suffix[-128:]

    return [package.name, benchmark, dd.name, args_suffix]


def output_path(package, benchmark, dd, args):
    b = benchmark_uid(package, benchmark, dd, args)
    return f"out/{b[0]}/{b[1]}/{b[2]}/{b[3]}.out"

# =========================================================================== #
# Script Strings
# =========================================================================== #


MODULE_LOAD = '''module load gcc/13.2.0
module load rust/1.77.1
module load cmake/3.23.5 autoconf/2.71 automake/1.16.1
module load boost/1.68.0'''

ENV_SETUP = '''export CC=/comm/swstack/core/gcc/10.1.0/bin/gcc
export CXX=/comm/swstack/core/gcc/10.1.0/bin/c++
export LC_ALL=C'''


def sbatch_str(jobname, time, is_exclusive):
    return f'''#SBATCH --job-name={jobname}
#SBATCH --partition={partition}
#SBATCH --mem={"0" if is_exclusive else "16G"}
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time={time}
#SBATCH --mail-type=END,FAIL,REQUEUE''' + ("\n#SBATCH --exclusive" if is_exclusive else "")
# SBATCH --mail-user=202109103@post.au.dk


def benchmark_awk_str(i):
    # $1  = output file path
    d1 = output_path(i[0], i[1], i[2], i[3])

    # $2  = executable
    d2 = executable(i[0], i[1], i[2])

    # $3+ = arguments
    ds = i[3]

    return f"{d1} {d2} {ds}"


SLURM_ARRAY_ID = "$SLURM_ARRAY_TASK_ID"
SLURM_JOB_ID = "$SLURM_JOB_ID"
SLURM_ORIGIN = "$SLURM_SUBMIT_DIR"


def benchmark_str(time, benchmarks):
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    parent_dir_name = os.path.basename(parent_dir)

    slurm_job_prefix = parent_dir_name
    slurm_job_suffix = time.replace(':', '-')

    # Array file to be read with AWK
    awk_content = '\n'.join(list(map(benchmark_awk_str, benchmarks)))
    awk_name = slurm_job_suffix + ".awk"

    # SLURM Shell Script
    awk_array_idx = f"NR == '{SLURM_ARRAY_ID}'"

    args_length = max(map(lambda b: len(b[3].split()), benchmarks))
    awk_args = '" "$' + \
        '" "$'.join(map(lambda b: str(b), range(3, args_length+3)))

    memory = partitions[partition][0]
    memory = int(memory - memory/10) * 1024

    slurm_content = f'''#!/bin/bash
{sbatch_str(f"{slurm_job_prefix}__{slurm_job_suffix}", time, True)}
#SBATCH --array=1-{len(benchmarks)}

awk '{awk_array_idx} {{ system("touch {SLURM_ORIGIN}/"$1) }}' {SLURM_ORIGIN}/slurm/{awk_name}

awk '{awk_array_idx} {{ system("echo -e \\"\\n=========  Started  `date`  ==========\\n\\" | tee -a {SLURM_ORIGIN}/"$1) }}' {SLURM_ORIGIN}/slurm/{awk_name}

awk '{awk_array_idx} {{ system("{SLURM_ORIGIN}/build/src/"$2 {awk_args} " -M {memory} -T /scratch/{SLURM_JOB_ID} 2>&1 | tee -a {SLURM_ORIGIN}/"$1) }}' {SLURM_ORIGIN}/slurm/{awk_name}

awk '{awk_array_idx} {{ system("echo -e \\"\\nexit code: \\"$? | tee -a {SLURM_ORIGIN}/"$1) }}' {SLURM_ORIGIN}/slurm/{awk_name}

awk '{awk_array_idx} {{ system("echo -e \\"\\n=========  Finished `date`  ==========\\n\\" | tee -a {SLURM_ORIGIN}/"$1) }}' {SLURM_ORIGIN}/slurm/{awk_name}

rm -rf /scratch/{SLURM_JOB_ID}/*

awk '{awk_array_idx} {{ system("echo -e \\"\\n=========  Clean-up `date`  ==========\\n\\" | tee -a {SLURM_ORIGIN}/"$1) }}' {SLURM_ORIGIN}/slurm/{awk_name}
'''
    slurm_name = slurm_job_suffix + ".sh"

    # Return name and both file's content
    return [[slurm_name, slurm_content], [awk_name, awk_content]]


CMAKE_STATS = "BDD_BENCHMARK_STATS"
CMAKE_GRENDEL_FLAG = "BDD_BENCHMARK_GRENDEL"


def build_str(stats):
    cpu = partitions[partition][1]

    prefix = f'''#!/bin/bash
echo -e "\\n=========  Started `date`  ==========\\n"

{MODULE_LOAD}
{ENV_SETUP}

# Build
echo "Build"
mkdir -p ./build && cd ./build
cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_C_FLAGS="-march={cpu}" -D CMAKE_CXX_FLAGS="-march={cpu}" -D {CMAKE_GRENDEL_FLAG}=ON -D {CMAKE_STATS}={"ON" if stats else "OFF"} ..
'''

    bdd_build = ""
    if bdd_benchmarks:
        assert (bdd_packages)
        bdd_build = f'''
echo ""
echo "Build BDD Benchmarks"
for package in {' '.join([p.name for p in bdd_packages])} ; do
                for benchmark in {' '.join([b for b in bdd_benchmarks])} ; do
                        mkdir -p ../out/$package ; \\
                        mkdir -p ../out/$package/$benchmark ; \\
                        mkdir -p ../out/$package/$benchmark/bdd ; \\
                        make $package'_'$benchmark'_bdd' ;
                done ;
done
'''

    bcdd_build = ""
    if bcdd_benchmarks:
        assert (bcdd_packages)
        bcdd_build = f'''
echo ""
echo "Build BCDD Benchmarks"
for package in {' '.join([p.name for p in bcdd_packages])} ; do
                for benchmark in {' '.join([b for b in bcdd_benchmarks])} ; do
                        mkdir -p ../out/$package ; \\
                        mkdir -p ../out/$package/$benchmark ; \\
                        mkdir -p ../out/$package/$benchmark/bcdd ; \\
                        make $package'_'$benchmark'_bcdd' ;
                done ;
done
'''

    zdd_build = ""
    if zdd_benchmarks:
        assert (zdd_packages)
        zdd_build = f'''
echo ""
echo "Build ZDD Benchmarks"
for package in {' '.join([p.name for p in zdd_packages])} ; do
                for benchmark in {' '.join([b for b in zdd_benchmarks])} ; do
                        mkdir -p ../out/$package ; \\
                        mkdir -p ../out/$package/$benchmark ; \\
                        mkdir -p ../out/$package/$benchmark/zdd ; \\
                        make $package'_'$benchmark'_zdd' ;
                done ;
done
'''

    suffix = f'''
echo -e "\\n========= Finished `date` ==========\\n"
'''

    return prefix + bdd_build + bcdd_build + zdd_build + suffix

# =========================================================================== #
# Run Script Strings and Save to Disk
# =========================================================================== #


with open("build.sh", "w") as file:
    file.write(
        build_str(input(f"Include Statistics? (yes/No): ").lower() in yes_choices))

for (t, b) in grouped_instances.items():
    for [filename, content] in benchmark_str(t, b):
        with open(filename, "w") as file:
            file.write(content)

print("\nScripts")
print("  Time Limits:      ", len(grouped_instances.keys()))
print("  Minimum Array:    ", min(
    map(lambda x: len(x[1]), grouped_instances.items())))
print("  Maximum Array:    ", max(
    map(lambda x: len(x[1]), grouped_instances.items())))
print("  Total Benchmarks: ", sum(
    map(lambda x: len(x[1]), grouped_instances.items())))
