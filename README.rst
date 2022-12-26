calculix-orient
###############

:date: 2022-12-22
:tags: CalculiX
:author: Roland Smith

.. Last modified: 2022-12-26T11:11:22+0100
.. vim:spelllang=en

This program examines a CalculiX mesh, and generates orientations for the
elements in given sets.

It it written in Python; it requires that Python 3.9 or later is installed on
your machine.

It was written to correctly assign orthotropic material properties
to elements that are not aligned with the global coordinate system.
For example in the case of fiber reinforced composite laminates.

.. PELICAN_END_SUMMARY

Assumptions
===========

This program makes the following assumptions:

* The mesh only contains C3D20(R) [he20(r)] elements.
* The long axis of the mesh is in the +X direction.
* The directory in which it is invoked contains only one simulation.
* The file ``all.msh`` contains *all* nodes and elements
* The files ``*.nam`` contain the definitions of sets.


Usage
=====

Run the script from a directory that has ``all.msh`` and the
``<setname>.nam`` file(s) that contains the set that you want to orient.
Run the file as follows::

    cd ~/project/directory
    auto-orient.py set1.nam set2.nam

where ``set1.nam`` and ``set2.nam`` are the names of files that define the sets that
have to be oriented.

This writes a file a file ``auto-orient.nam``.
Include this in your job input file.
It containts new element sets and orientations.

It also contains ``SOLID SECTION`` as comments.
Use those to replace the solid section for the original set.
Do not forget to set the material.
The author likes to do this automatically using e.g. ``awk``::

    awk '/SOLID/ {print $2, $3, $4, $5, "MATERIAL=Mqi"}' auto-orient.nam >sections.inp

The file ``sections.inp`` is then included in the job input file.

Example
=======

The subdirectory ``example`` contains an example of the use of this script in
a CalculiX workflow.

The subject of this simulation is an omega profile made from carbon fiber and
epoxy, in a quasi-isotropic layup.

The workflow (in a terminal emulator) is as follows:

1) Run the preprocessor: ``cgx -bg pre.fbd``
2) Run the auto-orient program: ``python auto-orient.py laminate.nam``
3) Create solid sections: ``awk '/SOLID/ {print $$2, $$3, $$4, $$5, "MATERIAL=Mqi"}' auto-orient.nam >sections.inp``
4) Run the solver: ``ccx -i job``
5) Clean up after a succesfull run: ``rm -f job.log spooles.out *.12d *.cvg *.sta *Miss*.nam``

.. note:: for ms-windows users. In the list above you should replace ``rm``
   with ``del``. If ``awk`` is not available, edit ``auto-orient.nam`` and
   copy the ``SOLID SECTION`` commands to ``sections.inp`` by hand, changing
   the material to ``Mqi``.

You can run one of the predefined ``view-*.fbd`` files to show you the
displacment, mesh, element sets or stress::

   cgx -b view-sets.fbd

For users of a UNIX-like OS, this workflow has automated using ``make``.
Both BSD make and GNU make should work.
The Makefile assumes that ``cgx``, ``python``, ``awk`` and ``ccx`` are installed
and can be found via the ``PATH`` environment variable.
