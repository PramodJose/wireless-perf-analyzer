from optparse import OptionParser
import os


def parse_options():
    parser = OptionParser()

    parser.add_option("-n", "--num-nodes", help="number of nodes around an AP", action="store", type="int",
                      dest="num_nodes", metavar="<number of nodes>")
    parser.add_option("-x", "--maxx", help="Max x-coordinate of the simulation area", action="store",
                      dest="maxx", metavar="<max x-coordinate>")
    parser.add_option("-y", "--maxy", help="Max y-coordinate of the simulation area", action="store",
                      dest="maxy", metavar="<max y-coordinate>")
    parser.add_option("-p", "--pause-time", help="Pause time of each node", action="store",
                      dest="pause_time", metavar="<pause time>")
    parser.add_option("-M", "--max-speed", help="Max speed attainable by a node", action="store",
                      dest="max_speed", metavar="<max speed>")
    parser.add_option("-t", "--time", help="Simulation time", action="store",
                      dest="sim_time", metavar="<simulation time>")
    parser.add_option("-d", "--destination", help="output file name", action="store",
                      dest="outfile", metavar="<output file name>")
    parser.add_option("-X", "--offx", help="Offset x-coordinate", action="store", type="int",
                      dest="offx", metavar="<Offset x-coordinate>")
    parser.add_option("-Y", "--offy", help="Offset y-coordinate", action="store", type="int",
                      dest="offy", metavar="<Offset y-coordinate>")
    parser.add_option("-i", "--offi", help="Offset index", action="store", type="int",
                      dest="off_index", metavar="Node offset index")

    (options, _) = parser.parse_args()
    return options


def process_node(line, options, special=False):
    i = 0
    while line[i] != '(':
        i += 1
    i += 1                  # place i after the '('

    mod_line = line[:i]     # copy till '(' (including that character)
    start = i               # remember where the node index starts
    while line[i] !=')':
        i += 1

    node_index = int(line[start:i]) + options.off_index     # i is where the node index ends
    mod_line += str(node_index)

    start = i                                           # i is currently poiting at ')'; remember the position
    i += 1                                              # move i to the next position; it's a space.

    if not special:
        spaces_till_coord = 3           # constant; denotes the number of spaces from the ')' to the co-ordinate
        spaces_count = 0

        while spaces_count != spaces_till_coord:
            if line[i] == ' ':
                spaces_count += 1
            i += 1

        mod_line += line[start:i]       # i now points to the beginning of the co-ordinate;
                                        # copies till the space before the co-ordinate (incl space).
        numbers = line[i:].split('.')   # split on the basis of '.'
        axis = line[i - 3]

        if axis == 'X':
            mod_line += str(int(numbers[0]) + options.offx)
        elif axis == 'Y':
            mod_line += str(int(numbers[0]) + options.offy)
        else:
            mod_line += numbers[0]

        mod_line += "." + numbers[1]

    else:
        spaces_till_coord = 2           # constant; denotes the number of spaces from the ')' to the co-ordinate
        spaces_count = 0

        while spaces_count != spaces_till_coord:
            if line[i] == ' ':
                spaces_count += 1
            i += 1

        mod_line += line[start:i]  # i now points to the beginning of the co-ordinate;
        # copies till the space before the co-ordinate (incl space).

        # "$node_(0) setdest 976.685360109097 64.887869171024 13.026815166133"
        numbers = line[i:].split('.')  # split on the basis of '.'
        # '976', '685360109097 64', '887869171024 13, '026815166133'

        mod_line += str(int(numbers[0]) + options.offx) + "." + numbers[1].split()[0] + " "
        mod_line += str(int(numbers[1].split()[1]) + options.offy) + "."
        mod_line += numbers[2] + "." + numbers[3]

    return mod_line


def process_god(line, options):
    spaces_to_first_change = 2      # constant; denotes the number of spaces after which
                                    # the node index to modify is present

    i = 0
    spaces_count = 0
    while spaces_count != spaces_to_first_change:
        if line[i] == ' ':
            spaces_count += 1
        i += 1
    mod_line = line[:i]     # copies till the space

    numbers = line[i:].split()
    mod_line += str(int(numbers[0]) + options.off_index) + " "
    mod_line += str(int(numbers[1]) + options.off_index) + " "
    mod_line += numbers[2] + "\n"

    return mod_line


def process_ns(line, options):
    i = 0
    while line[i] != "\"":
        i += 1
    i += 1      # skip past the " char

    mod_line = line[:i]
    line = line[i:]
    if line.startswith("$node_("):
        mod_line += process_node(line, options, True)
    elif line.startswith("$god_"):
        mod_line += process_god(line, options)
    else:
        mod_line = mod_line + line

    return mod_line


def transform_file(out_fh, options):
    with open(options.outfile + "_", "r") as in_fh:
        for line in in_fh:
            modified_line = ""

            if line.startswith("$node_("):
                modified_line = process_node(line, options)
            elif line.startswith("$god_"):
                modified_line = process_god(line, options)
            elif line.startswith("$ns_"):
                modified_line = process_ns(line, options)
            else:
                modified_line = line

            out_fh.write(modified_line)


if __name__ == "__main__":
    options = parse_options()

    command = "setdest -v 1 -n " + str(options.num_nodes - 1) + " -p " + options.pause_time + \
              " -M " + options.max_speed + " -t " + options.sim_time + " -x " + options.maxx + \
              " -y " + options.maxy + " > " + options.outfile + "_"
    # the intermediate file has an underscore at the end; which we will delete at the very end.

    os.system(command)

    out_fh = open(options.outfile, "w")
    options.off_index += 1
    transform_file(out_fh, options)
    os.remove(options.outfile + "_")        # delete the intermediate file.

    # logic for spawning the AP and the initial_node_pos for all nodes
    center_x = int(options.maxx) // 2 + options.offx
    center_y = int(options.maxy) // 2 + options.offy
    options.off_index -= 1

    out_fh.write("\n# Creating the Access Point..\n")
    out_fh.write("$node_(" + str(options.off_index) + ") set X_ " + str(center_x) + "\n")
    out_fh.write("$node_(" + str(options.off_index) + ") set Y_ " + str(center_y) + "\n")

    out_fh.write("\n# Setting initial positions of the nodes; i.e. displaying them on nam\n")
    for i in range(options.num_nodes):
        out_fh.write("$ns_ initial_node_pos $node_(" + str(options.off_index + i) + ") 20\n")
        
    out_fh.close()

