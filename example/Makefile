# file: Makefile
# vim:fileencoding=utf-8:fdm=marker:ft=make
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2022-12-26T10:13:23+0100
# Last modified: 2022-12-26T10:16:43+0100
.PHONY: mesh disp stress core clean include

all: all.msh job.frd

# Run the pre-processor
all.msh: pre.fbd
	cgx -bg pre.fbd

auto-orient.nam: all.msh
	python ../auto-orient.py laminate.nam

sections.inp: auto-orient.nam
	awk '/SOLID/ {print $$2, $$3, $$4, $$5, "MATERIAL=Mqi"}' auto-orient.nam >sections.inp

# Run the solver
# Note: to take advantage of multiple cores,
# OMP_NUM_THREADS should be set in the environment.
job.frd: job.inp sections.inp
	ccx -i job
	rm -f job.log spooles.out *.12d *.cvg *.sta
	rm -f *Miss*.nam

# Different post-processor commands

# view the mesh
mesh: all.msh
	cgx -b view-mesh.fbd

# view displacements
disp: job.frd view-disp.fbd
	cgx -b view-disp.fbd

# view sets
sets: job.frd view-sets.fbd
	cgx -b view-sets.fbd

# view stress
stress: job.frd view-stress.fbd
	cgx -b view-stress.fbd


# Helpers
clean::
	rm -f *.equ *.sur *.nam *.msh *.log spooles.out *.12d *.cvg *.sta *.con
	rm -f sections.inp job.frd job.dat

include::
	@ls *.msh *.nam *.sur *.equ *.con|sed -e 's/^/\*INCLUDE, INPUT=/'
