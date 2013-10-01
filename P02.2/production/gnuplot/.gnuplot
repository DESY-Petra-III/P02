# terminal
set term x11 enhanced

load "~/gnuplot/gnu_start"

# set grid
set grid

# to show the plot window automatically
if(maxn>0){
	load "~/gnuplot/gnu_plot"
	MAXY=GPVAL_DATA_Y_MAX
	MINY=GPVAL_DATA_Y_MIN
}else{
	plot [-1:1] [0:2] 1
}

