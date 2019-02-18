if {$argc != 3} {
	puts "Usage:-\n\tns $argv0 <number-of-APs> <output-file> <ID>"
	exit 0
}

set val(max_row)			5
set val(max_col)			10
set val(AP_count)			[lindex $argv 0]
set val(outfile)			[lindex $argv 1]
set val(ID)					[lindex $argv 2]

if {$val(AP_count) > [expr {$val(max_row) * $val(max_col)}]} {
	puts "No support for these many APs. Consider increasing max_row and/or max_col."
	exit 0
} elseif {$val(AP_count) < 1} {
	puts "Number of APs should be at least 1"
	exit 0
}

set val(chan)				Channel/WirelessChannel
set val(prop)				Propagation/TwoRayGround
set val(netif)				Phy/WirelessPhy
set val(mac)				Mac/802_11
set val(ifq)				Queue/DropTail/PriQueue
set val(ifqlen)				65536
set val(ll)					LL
set val(ant)				Antenna/OmniAntenna
set val(rp)					DSDV

set val(simtime)			20.0
set val(buff_time)			0.01
set val(sidex)				25
set val(sidey)				25

set val(cols)				[expr {int(ceil(double($val(AP_count)) / $val(max_row)))}]
if {$val(AP_count) < $val(max_row)} {
	set val(rows) $val(AP_count)
} else {
	set val(rows) [expr {int($val(max_row))}]
}

set val(overlap)			5
set val(maxx)				[expr {$val(sidex) * $val(cols) - $val(overlap) * ($val(cols) - 1)}]
set val(maxy)				[expr {$val(sidey) * $val(rows) - $val(overlap) * ($val(rows) - 1)}]
set val(min_nn_per_wifi)	11
set val(max_nn_per_wifi)	26

# initialisations
set val(nn)					0
set val(rand_range)			[expr {$val(max_nn_per_wifi) - $val(min_nn_per_wifi) + 1}]

set netSizes(0) 0
# randomly deciding number of nodes per wifi.
for {set i 1} {$i <= $val(AP_count)} {incr i} {
	set netSizes($i) [expr {int(rand()* $val(rand_range)) + $val(min_nn_per_wifi)}]
	set val(nn) [expr {$val(nn) + $netSizes($i)}]
}

# puts "AP count: $val(AP_count)\t\tDimensions: $val(rows)x$val(cols)\t\tNode count: $val(nn)"
# puts "Actual dimensions: $val(maxx) x $val(maxy)"

set ns_ [new Simulator]
set topo [new Topography]
$topo load_flatgrid $val(maxx) $val(maxy)
create-god $val(nn)
set chan_1 [new $val(chan)]

$ns_ node-config	-adhocRouting $val(rp) \
					-llType $val(ll) \
					-macType $val(mac) \
					-ifqType $val(ifq) \
					-ifqLen $val(ifqlen) \
					-antType $val(ant) \
					-propType $val(prop) \
					-phyType $val(netif) \
					-topoInstance $topo \
					-channel $chan_1 \
					-agentTrace ON \
					-routerTrace OFF \
					-macTrace OFF \
					-movementTrace OFF


# set namtrace_fh [open "$argv0.nam" w]
# $ns_ namtrace-all-wireless $namtrace_fh $val(maxx) $val(maxy)
set trace_fh [open "$val(outfile).tr" w]
$ns_ trace-all $trace_fh
set outfile_fh [open $val(outfile) w]


proc calc_throughput {} {
	global sink_ val netSizes outfile_fh
	set bytes_received 0
	set netSizesPos 0
	set next_AP_index 0

	for {set i 0} {$i < $val(nn)} {incr i} {
		if {$i == $next_AP_index} {
			incr netSizesPos
			set next_AP_index [expr {$next_AP_index + $netSizes($netSizesPos)}]
		} else {
			set bytes_received [expr {$bytes_received + [$sink_($i) set bytes_]}]
		}
	}

	set avg_bytes_received [expr {double($bytes_received) / $val(AP_count)}]
	set throughput [expr {double($avg_bytes_received) / $val(simtime)}]

	puts $outfile_fh $throughput
}


proc finish {} {
	global ns_ trace_fh argv0 outfile_fh;# namtrace_fh
	$ns_ flush-trace
	# close $namtrace_fh
	close $trace_fh
	close $outfile_fh
	# exec nam "$argv0.nam" &
	exit 0
}


set effectivex	[expr {$val(sidex) - $val(overlap)}]
set effectivey	[expr {$val(sidey) - $val(overlap)}]
set ap 1
set node_index 0

# puts "\nScene\t\t basex \t basey \t index \t netSize"

for {set c 0} {$c < $val(cols)} {incr c} {
	for {set r 0} {$r < $val(rows)} {incr r} {
		if {$ap > $val(AP_count)} {
			break
		}

		set basex [expr {$c * $effectivex}]
		set basey [expr {$r * $effectivey}]
 		set file_name "scene_$val(ID)_$r$c"
 		# puts "$file_name\t $basex \t $basey \t $node_index \t $netSizes($ap)"

		exec python3 spawn_nodes.py -n $netSizes($ap) -x $val(sidex) -y $val(sidey) -p 0 -M 20 \
			 -t $val(simtime) -d $file_name -X $basex -Y $basey -i $node_index

		source	$file_name

		file delete $file_name
 		set node_index [expr {$node_index + $netSizes($ap)}]
		incr ap
	}
}


$ns_ at $val(simtime) "calc_throughput"
$ns_ at [expr {$val(simtime) + $val(buff_time)}] "finish"
$ns_ run
