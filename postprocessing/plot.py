import numpy as np
import sqlite3
import matplotlib.pyplot as plt

DB_FILE = "./data.db"

def select_distinct(cur, field):
    table = "benchmarks"
    return list(map(
        lambda x: x[field],
        cur.execute(
            'SELECT DISTINCT %s FROM %s' % (field, table)
        ).fetchall()
    ))

con = sqlite3.connect(DB_FILE)
con.row_factory = sqlite3.Row
cur = con.cursor()

machine_list = select_distinct(cur, "hostname")
threads_list = select_distinct(cur, "threads")

x_benchmark = set()
y_upstream = []
y_upstream_thread = []
y_patched = []
y_patched_thread = []
for machine in machine_list:
    benchmark_list = list(map(
        lambda x: x['script'],
        cur.execute(
            "SELECT DISTINCT script FROM benchmarks "
            "WHERE hostname=? AND user='upstream' "
            "INTERSECT "
            "SELECT DISTINCT script FROM benchmarks "
            "WHERE hostname=? AND user='hack';",
            (machine, machine)
        ).fetchall()
    ))
    x_benchmark = benchmark_list
    print(x_benchmark)

    row_list = cur.execute(
        "SELECT script, user, trial, threads, max(speed) FROM benchmarks "
        "WHERE hostname=? "
        "GROUP BY script, user; ",
        (machine,)
    )

    for row in row_list:
        if row["script"] not in x_benchmark:
            continue

        if row["user"] == "upstream":
            y_upstream_thread.append(row["threads"])
            y_upstream.append(row["max(speed)"])
        elif row["user"] == "hack":
            y_patched_thread.append(row["threads"])
            y_patched.append(row["max(speed)"])
        else:
            assert False

con.commit()
con.close()

# plot
print(x_benchmark)
print(y_upstream)
print(y_patched)

y_upstream_label = []
for i in range(len(y_upstream)):
    y_upstream_label += ["%.2f\n%d threads" % (y_upstream[i], y_upstream_thread[i])]

y_patched_label = []
for i in range(len(y_upstream)):
    speedup = (y_patched[i] / y_upstream[i]) * 100
    y_patched_label += ["%.2f (%d%%)\n%d threads" % (y_patched[i], speedup, y_patched_thread[i])]

x = np.arange(len(x_benchmark))
width = 0.4

fig, ax = plt.subplots()
group_upstream = ax.barh(x - width / 2, y_upstream, width, label='Upstream')
group_patched = ax.barh(x + width / 2, y_patched, width, label='Patched')
ax.invert_yaxis()
ax.set_xlabel('Speed (MC/s)')
ax.bar_label(group_upstream, padding=3, labels=y_upstream_label, linespacing=0.85)
ax.bar_label(group_patched, padding=3, labels=y_patched_label, linespacing=0.85)
ax.set_yticks(x, x_benchmark)
ax.set_xlim(0, max(y_patched) * 1.4)
ax.legend(loc='lower right')
fig.tight_layout()
plt.show()
