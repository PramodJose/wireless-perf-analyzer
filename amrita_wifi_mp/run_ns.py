import os
from multiprocessing import Pool
tcl_script = "amrita_wifi_mp.tcl"


def calc_delay(file_name):
    avg_delay = 0
    sent_time = list()
    pkts_recvd = 0

    with open(file_name, "r") as in_fh:
        for line in in_fh:
            splitted_line = line.split()

            if len(splitted_line) < 6 or splitted_line[3] != "AGT":
                continue
            flow_id = int(splitted_line[5])
            time = float(splitted_line[1])

            if line.startswith("s "):
                if(len(sent_time)) <= flow_id:
                    sent_time.extend( [-1] * (flow_id + 1 - len(sent_time)))

                sent_time[flow_id] = time

            elif line.startswith("r "):
                if sent_time[flow_id] == -1:
                    print("There is some error. Please check")
                    exit(1)

                pkts_recvd += 1
                avg_delay += time - sent_time[flow_id]
                sent_time[flow_id] = -1

    avg_delay /= pkts_recvd
    os.remove(file_name)
    return avg_delay


def simulation_instance(command):
    os.system(command)

    file_name = command.split()[3]
    in_fh = open(file_name, "r")
    throughput = float(in_fh.readline())
    in_fh.close()
    os.remove(file_name)
    delay = calc_delay(file_name + ".tr")

    return throughput, delay


if __name__ == "__main__":
    min_aps = 1
    max_aps = 50
    run_count = 20
    outfile = "avg_byte_count"
    results_thr = "plot_throughout"
    results_delay = "plot_delay"
    out_thr_fh = open(results_thr, "w")
    out_del_fh = open(results_delay, "w")

    for i in range(min_aps, max_aps + 1):
        print("Working on AP count", i)
        throughput = 0
        delay = 0
        commands = []

        for j in range(run_count):
            command = "ns " + tcl_script + " " + str(i) + " " + outfile + str(j) + " " + str(j) + " > /dev/null 2>&1"
            commands.append(command)

        p = Pool()
        result_list = p.map(simulation_instance, commands)
        p.close()
        p.join()

        for j in range(run_count):
            throughput += result_list[j][0]
            delay += result_list[j][1]

        avg_throughput = throughput / run_count
        avg_delay = delay / run_count
        out_thr_fh.write(str(i) + " " + str(avg_throughput) + "\n")
        out_del_fh.write(str(i) + " " + str(avg_delay) + "\n")

    out_thr_fh.close()
    out_del_fh.close()

    print("The throughput graph is " + results_thr)
    print("..and the avg delay graph is " + results_delay)
