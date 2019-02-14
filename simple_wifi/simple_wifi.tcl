if {$argc != 2} {
	puts "Usage:-\n\tns simple_wifi.tcl <number-of-nodes> <output-file>"
	exit 0
}

set val(chan)			Channel/WirelessChannel
set val(prop)			Propagation/TwoRayGround
set val(netif)			Phy/WirelessPhy
set val(mac)			Mac/802_11
set val(ifq)			Queue/DropTail/PriQueue
set val(ifqlen)			65536
set val(ll)				LL
set val(ant)			Antenna/OmniAntenna
set val(rp)				DSDV

set val(simtime)		20.0
set val(buff_time)		0.1
set val(sidex)			200
set val(sidey)			200
set val(area_nn)		[lindex $argv 0]
set val(row)			1
set val(col)			1
set val(maxx)			[expr {$val(sidex) * $val(col)}]
set val(maxy)			[expr {$val(sidey) * $val(row)}]
set val(nn)				[expr {$val(area_nn) * $val(row) * $val(col)}]
set val(outfile)		[lindex $argv 1]


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
set trace_fh [open "$argv0.tr" w]
$ns_ trace-all $trace_fh
set outfile_fh [open $val(outfile) w]


proc finish {} {
	global ns_ trace_fh argv0 outfile_fh;# namtrace_fh
	$ns_ flush-trace
	# close $namtrace_fh
	close $trace_fh
	close $outfile_fh
	# exec nam "$argv0.nam" &
	exit 0
}

proc count_bytes {} {
	global sink_ val outfile_fh
	set bytes 0

	for {set i 1} {$i < $val(nn)} {incr i} {
		set bytes [expr {[$sink_($i) set bytes_] + $bytes}]
	}

	puts $outfile_fh "$bytes"
}

for {set r 0} {$r < $val(row)} {incr r} {
	for {set c 0} {$c < $val(col)} {incr c} {
		set basex [expr {$c * $val(sidex)}]
		set basey [expr {$r * $val(sidey)}]
		set node_index [expr {($r * $val(col) + $c) * $val(area_nn)}]
		set file_name "scene_$r$c"
		puts "working on $file_name\t $basex \t $basey \t $node_index"

		exec python3 spawn_nodes.py -n $val(area_nn) -x $val(sidex) \
		 	 -y $val(sidey) -p 0 -M 20 -t $val(simtime) -d $file_name -X $basex -Y $basey -i $node_index

		source $file_name

		file delete $file_name
	}
}

$ns_ at $val(simtime) "count_bytes"
$ns_ at [expr {$val(simtime) + $val(buff_time)}] "finish"
$ns_ run
