import os


min_aps = 1
max_aps = 15
run_count = 20
outfile = "avg_byte_count"
results = "plot"
out_fh = open(results, "w")

for i in range(min_aps, max_aps + 1):
    bytes = 0

    for j in range(run_count):
        command = "ns apartment_wifi.tcl " + str(i) + " " + outfile
        os.system(command)
        in_fh = open(outfile, "r")
        bytes += float(in_fh.readline())
        in_fh.close()

    avg_bytes = bytes / run_count
    out_fh.write(str(i) + " " + str(avg_bytes) + "\n")

out_fh.close()
os.remove(outfile)

os.system("xgraph " + results + " &")
