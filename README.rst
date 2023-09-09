calculix-orient
###############

:date: 2022-12-22
:tags: CalculiX
:author: Roland Smith

.. Last modified: 2023-09-09T10:30:12+0200
.. vim:spelllang=en

This program examines a CalculiX mesh, and generates orientations for the
elements in given sets.

It it written in Python; it requires that Python 3.9 or later is installed on
your machine.

It was written to correctly assign orthotropic material properties to elements
that are not aligned with the global coordinate system in the case of fiber
reinforced composite laminates.

Composite laminates are *generally* thin layers.
So this program finds the largest face of the element and sets the normal
perpendicular to it.

It gathers all the unique normal vectors in the sets given on the command-line, and
creates orientations for them, with the help of a “base” vector, which is the
global x-axis by default.

The new orientations are created as follows.

* The cross-product of the a normal and the base vector is taken. This becomes
  the new local Y-axis.
* Next, the cross-product of this local Y-axis and the normal is taken. This
  becomes the new local X-axis.

For every unique normal vector, a new ``*ELSET`` and ``*ORIENTATION`` is created.
Then a ``*SOLID SECTION`` referencing both.
The names of the orientations contain a prefix that is randomly generated for
each run. This is done so that the orientations created in multiple
invocations do not conflict.


.. PELICAN_END_SUMMARY

Assumptions
===========

This program makes the following assumptions:

* The brick elements are thinner in one direction then the others.
* The directory in which it is invoked contains only one simulation.
* The file ``all.msh`` contains *all* nodes and elements
* The files ``*.nam`` contain the definitions of sets.
* Each call generates orientations with a random four byte hexadecimal prefix.
  It is assumed that this prefix is not repeated with repeated invocations of
  the program.

It has the following restrictions:

* It only works with C3D20(R) [he20(r)] brick elements.
* Every ``*.nam`` can contain only *one* set of elements.
* It can be called multiple times for the same input problem, with different
  base vectors, but each set should only be oriented *once*.


Usage
=====

Run the script from a directory that has ``all.msh`` and the
``<setname>.nam`` file(s) that contains the set that you want to orient.
Run the file as follows::

    cd ~/project/directory
    auto-orient.py set1.nam set2.nam

where ``set1.nam`` and ``set2.nam`` are the names of files that define the sets that
have to be oriented.

This writes two files; ``auto-orient.nam`` and ``auto-orient.inp``
Include these in your job input file.
The first file containts new element sets and orientations, while the second
contains the ``SOLID SECTION`` commands.
In the ``SOLID SECTION`` commands, the ``MATERIAL`` is set to ``M<setname>``.

By default, ``auto-orient`` aligns the orientation with the x-axis.
If you want to change this, use the ``--base`` option like this::

    auto-orient.py --base 0,0,1 set1.nam set2.nam

Example
=======

The subdirectory ``example`` contains an example of the use of this script in
a CalculiX workflow.

The subject of this simulation is an omega profile made from carbon fiber and
epoxy, in a quasi-isotropic layup.
This geometry should have several many different orientations, depending on how fine the
mesh is.
Note that the stresses in this example are not accurate! The material
properties of the laminate are synthesized into a single value.
For accurate stresses, the mesh should be built up out of separate layers.


The workflow (in a terminal emulator) is as follows:

1) Run the preprocessor: ``cgx -bg pre.fbd``
2) Run the auto-orient program: ``python auto-orient.py laminate.nam``
3) Run the solver: ``ccx -i job``
4) Clean up after a succesfull run: ``rm -f job.log spooles.out *.12d *.cvg *.sta *Miss*.nam``

.. note:: for ms-windows users. In the list above you should replace ``rm``
   with ``del``. Also, ``python`` is assumed to by Python 3.9 or later.

You can run one of the predefined ``view-*.fbd`` files to show you the
displacment, mesh, element sets or strain::

   cgx -b view-sets.fbd

For users of a UNIX-like OS, this workflow has automated using ``make``.
Both BSD make and GNU make should work.
The Makefile assumes that ``cgx``, ``python3`` and ``ccx`` are installed
and can be found via the ``PATH`` environment variable.
