calculix-orient
###############

:date: 2022-12-22
:tags: CalculiX
:author: Roland Smith

.. Last modified: 2022-12-24T15:35:21+0100
.. vim:spelllang=en

This program examines a CalculiX mesh, and generates orientations for the
elements in a given set.

It was originally written to “wrap” orthotropoc material properties around
radii. For example in the case of composites.

.. PELICAN_END_SUMMARY

Assumptions
===========

This program makes the following assumptions:

* The long axis of the mesh is in the +X direction.
* The directory in which it is invoked contains only one simulation.
* The file ``all.msh`` contains all nodes and elements
* The files ``*.nam`` contain the definitions of sets.
* It only processes C3D20(R) elements.

Usage
=====

Run the script from a directory that has ``all.msh`` and the
``<setname>.nam`` file(s) that contains the set that you want to orient.

This writes a file a file ``auto-orient.nam``.
Include this in your job input file.
It containts new element sets and orientations.

It also contains ``SOLID SECTION`` as comments.
Use those to replace the solid section for the original set.
Do not forget to set the material.


Calculations
============

Example: ``~/calculix/sandwich-box-tie-rounded/``.
Radius elements: set ``Elrad``.

Element 1321::

    1321,  7524,  7525,  7526,  7527,  7528,  7529,  7530,  7531,  7532,  7533,
           7534,  7535,  7540,  7541,  7542,  7543,  7536,  7537,  7538,  7539

Element 1321 is on the +Y axis, and lies against the vertical wall.

We are interested in the cross-product between two vectors:

1) 2nd node - 1st node
2) 3rd node - 2nd node

In this case: (7525 - 7524)x(7526 - 7525).

Nodes::

    7524,0.000000000000e+00,2.000000000000e-01,1.000000000000e-02
    7525,0.000000000000e+00,1.970710678119e-01,2.928932188135e-03
    7526,6.250000000000e-02,1.970710678119e-01,2.928932188135e-03

.. code-block:: python

    In [3]: v7524 = (0.000000000000e+00,2.000000000000e-01,1.000000000000e-02)
    Out[3]: (0.0, 0.2, 0.01)

    In [4]: v7525 = (0.000000000000e+00,1.970710678119e-01,2.928932188135e-03)
    Out[4]: (0.0, 0.1970710678119, 0.002928932188135)

    In [5]: v7526 = (6.250000000000e-02,1.970710678119e-01,2.928932188135e-03)
    Out[5]: (0.0625, 0.1970710678119, 0.002928932188135)

    In [7]: c = cross(sub(v7525, v7524), sub(v7526, v7525))
    Out[7]: (0.0, -0.0004419417382415625, 0.0001830582617562502)

    In [10]: normalize(c)
    Out[10]: (0.0, -0.9238795325128724, 0.3826834323612618)

    In [12]: normalize(sub(v7525, v7524))
    Out[12]: (0.0, -0.3826834323612618, -0.9238795325128724)

    In [13]: normalize(sub(v7526, v7525))
    Out[13]: (1.0, 0.0, 0.0)
