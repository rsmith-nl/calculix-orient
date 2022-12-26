calculix-orient
###############

:date: 2022-12-22
:tags: CalculiX
:author: Roland Smith

.. Last modified: 2022-12-26T10:09:24+0100
.. vim:spelllang=en

This program examines a CalculiX mesh, and generates orientations for the
elements in given sets.

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

