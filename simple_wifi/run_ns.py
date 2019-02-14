import os


min_nodes = 2
max_nodes = 11
run_count = 20
outfile = "byte_count"
results = "plot"


out_fh = open(results, "w")
for i in range(min_nodes, max_nodes + 1):
    bytes = 0

    for j in range(run_count):
        command = "ns simple_wifi.tcl " + str(i) + " " + outfile
        os.system(command)
        in_fh = open(outfile, "r")
        bytes += int(in_fh.readline())
        in_fh.close()

    avg_bytes = bytes / run_count
    out_fh.write(str(i - 1) + " " + str(avg_bytes) + "\n")

out_fh.close()
os.remove(outfile)

os.system("xgraph " + results + " &")
