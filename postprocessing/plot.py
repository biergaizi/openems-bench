import sys
import numpy as np
import itertools
import sqlite3
import matplotlib.pyplot as plt
from pylab import rcParams
rcParams['figure.figsize'] = (7, 8)

DB_FILE = "./data.db"

SIMULATION_ANNOT = {
    'Bent_Patch_Antenna.py': "56x238x63",
    'Bent_Patch_Antenna_nodump.py': "56x238x63",
    'CRLH_Extraction.py': "117x99x40",
    'CRLH_LeakyWaveAnt.m': "409x107x63",
    'CylindricalWave_CC.m': "257x1600x5",
    'Helical_Antenna.py': "83x83x178",
    'Helical_Antenna_PEConly.py': "83x83x178",
    'MSL_NotchFilter.py': "235x82x14",
    'RCS_Sphere.py': "83x83x83",
    'Rect_Waveguide.py': "27x12x132",
    'Rect_Waveguide_nodump.py': "27x12x132",
    'Simple_Patch_Antenna.py': "42x43x45",
    'StripLine2MSL.m': "147x103x35",
    'coupler.py': "227x86x37",
    'gcpw.py': "147x335x77",
    'gcpw_nopml.py': "147x335x77",
    'gcpw_nopml_nocondsheet.py': "147x335x77",
    'microstrip_sma_transition.py': "162x215x165",
    'rf_via.py': "178x189x61",
}

def select_distinct(cur, field):
    table = "benchmarks"
    return list(map(
        lambda x: x[field],
        cur.execute(
            'SELECT DISTINCT %s FROM %s' % (field, table)
        ).fetchall()
    ))

def list_targets():
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    machine_list = select_distinct(cur, "hostname")
    build_list = select_distinct(cur, "build")
    print("machine: ", end="")
    print("  ", *machine_list, sep="\n  ")

    print("\nbuild: ", end="")
    print("  ", *build_list, sep="\n  ")

    con.close()

def versus(target_list, normalize=False):
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Each item in target_list is a 2-element tuple, first element
    # is the machine name, second element is the build name, such as:
    #   [(machine_a, build_a), (machine_b, build_b), (machine_c, host_c)]
    #
    # For easy SQL parameter substitution, now we also create a flattened
    # version named target_list_mbmb, as in
    #   [machine_a, build_a, machine_b, build_b, machine_c, host_c]
    target_list_mbmb = list(itertools.chain(*target_list))

    # And also a flattened version named target_list_mmbb, as in
    #   [machine_a, machine_b, build_a, build_b]
    target_list_mmbb = (
        [target[0] for target in target_list] +
        [target[1] for target in target_list]
    )

    # Step 1:
    #
    # Find the union of common benchmarks shared between
    # all (machine, build) targets.

    sql = [
            "SELECT DISTINCT script FROM benchmarks "
            "WHERE hostname=? AND build=? "
    ] * len(target_list)

    # join multiple "SELECT" strings with keyword INTERSECT
    benchmark_list = list(map(
        lambda row: row["script"],
        cur.execute(
            " INTERSECT ".join(sql),
            target_list_mbmb
        )
    ))

    # Step 2:
    #
    # Find the highest speed in each benchmark (regardless of threads)
    # per branch per machine.
    hostname_params = " OR ".join(
        ["hostname=?"] * len(target_list)
    )

    build_params = " OR ".join(
        ["build=?"] * len(target_list)
    )

    # 2-target example
    # "SELECT hostname, script, build, trial, threads, max(speed) FROM benchmarks "
    # "WHERE (hostname=? OR hostname=?) AND (build=? OR build=?)"
    # "GROUP BY script, hostname, build "
    # "ORDER BY script;"
    speed_list = cur.execute(
        "SELECT hostname, script, build, trial, threads, max(speed) FROM benchmarks "
        "WHERE (%s) AND (%s)"
        "GROUP BY script, hostname, build "
        "ORDER BY script, hostname, build;" % (hostname_params, build_params),
        target_list_mmbb
    )

    # bench1, mach1, build1, speed1
    # bench1, mach2, build2, speed2
    # bench2, mach1, build1, speed3
    # bench2, mach2, build2, speed4

    speed_dict = {}

    for row in speed_list:
        script = speed_dict.get(row["script"], {})
        target = script.get((row["hostname"], row["build"]), {})
        target["threads"] = row["threads"]
        target["speed"] = row["max(speed)"]

        speed_dict[row["script"]] = script
        script[(row["hostname"], row["build"])] = target

    con.close()

    # plot

    # are we compare the same machine, or different machines?
    all_machine_list = [machine for machine, build in target_list]
    first_machine = target_list[0][0]

    if all_machine_list.count(first_machine) == len(target_list):
        # different builds on a single machine is compared
        same_machine = True
    else:
        same_machine = False

    # label the name of all scripts and number of cells in each benchmark script
    label_script_list = list(benchmark_list).copy()

    for idx, txt in enumerate(label_script_list):
        size = SIMULATION_ANNOT[txt]
        label_script_list[idx] = txt + "\n%s" % size
        x, y, z = size.split("x")
        cells = int(x) * int(y) * int(z) / 1e6
        label_script_list[idx] += "\n%.2f Mcells" % cells

    # label the speed of the number of threads used in each test,
    # and the speedup in percentage

    for benchmark in benchmark_list:
        # the first target is always the reference
        reference = speed_dict[benchmark][target_list[0]]
        reference["label"] = "%.2f\n%d threads" % (
            reference["speed"], reference["threads"]
        )

        for target in target_list[1:]:
            speedup = speed_dict[benchmark][target]["speed"] / reference["speed"]
            speed_dict[benchmark][target]["speedup"] = speedup
            speed_dict[benchmark][target]["label"] = "%.2f (%d%%)\n%d threads" % (
                speed_dict[benchmark][target]["speed"],
                speedup * 100,
                speed_dict[benchmark][target]["threads"]
            )

    if normalize:
        for benchmark in benchmark_list:
            reference = speed_dict[benchmark][target_list[0]]
            reference["speed"] = 100

            for target in target_list[1:]:
                speedup = speed_dict[benchmark][target]["speedup"]
                speed_dict[benchmark][target]["speed"] = 100 * speedup

    fig, ax = plt.subplots()

    if len(target_list) == 2:
        x = np.arange(len(benchmark_list))
        width = 0.4
        bar_position = [
            x - width / 2,
            x + width / 2,
        ]
    elif len(target_list) == 3:
        x = np.arange(len(benchmark_list)) * 2
        width = 0.6
        bar_position = [
            x - width,
            x,
            x + width,
        ]
    else:
        assert False, "Only three-way comparison is supported"

    all_speed = []
    for idx, target in enumerate(target_list):
        speed = []
        label = []
        for benchmark in benchmark_list:
            speed.append(
                speed_dict[benchmark][target]["speed"]
            )
            label.append(
                speed_dict[benchmark][target]["label"]
            )

        if same_machine:
            label_fmt = "%s" % target[1]
        else:
            label_fmt = "%s %s" % target

        group = ax.barh(
            bar_position[idx],
            speed,
            width,
            label=label_fmt
        )
        ax.bar_label(group, padding=3, labels=label, linespacing=0.85)

        all_speed += speed

    ax.invert_yaxis()

    if normalize:
        ax.set_xlabel('Relative Speed (%)')
    else:
        ax.set_xlabel('Speed (MC/s)')

    ax.set_yticks(x, label_script_list)
    ax.set_xlim(0, max(all_speed) * 1.4)

    if same_machine:
        # different builds on a single machine is compared
        ax.set_title(first_machine)

    ax.legend()
    fig.tight_layout()
    plt.show()

def usage():
    print("Usage: ")
    print("%s list" % sys.argv[0])
    print("%s vs [hostname1] [build1] [hostname2] [build2]" % sys.argv[0])
    print("%s vs [hostname1] [build1] [hostname2] [build2] [hostname3] [build3]" % sys.argv[0])
    exit(1)

if len(sys.argv) < 2:
    usage()

if sys.argv[1] == "list":
    list_targets()
elif sys.argv[1] == "vs":
    if len(sys.argv) == 6:
        versus([(sys.argv[2], sys.argv[3]), (sys.argv[4], sys.argv[5])])
    elif len(sys.argv) == 8:
        versus([(sys.argv[2], sys.argv[3]), (sys.argv[4], sys.argv[5]), (sys.argv[6], sys.argv[7])])
    else:
        usage()
elif sys.argv[1] == "vs-normalize":
    if len(sys.argv) == 6:
        versus([(sys.argv[2], sys.argv[3]), (sys.argv[4], sys.argv[5])], normalize=True)
    elif len(sys.argv) == 8:
        versus([(sys.argv[2], sys.argv[3]), (sys.argv[4], sys.argv[5]), (sys.argv[6], sys.argv[7])], normalize=True)
    else:
        usage()
else:
    print("unknown command", file=sys.stderr)
