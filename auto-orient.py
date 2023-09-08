#!/usr/bin/env python
# file: auto-orient.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2022 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2022-12-22T22:45:41+0100
# Last modified: 2023-09-08T21:52:47+0200
"""Generate orientations and sets of elements that use them for given
initial sets of elements."""

import argparse
import logging
import math
import os
import sys

__version__ = "2023.09.08"


def main():
    """
    Entry point for auto-orient.py
    """
    args = setup()
    if not os.path.exists("all.msh"):
        logging.error("no “all.msh” file found; exiting")
        sys.exit(1)
    all_elements = read_allmsh()
    logging.info(f"read {len(all_elements)} elements from “all.msh”")
    elements = {}
    for setname in args.set:
        if setname.endswith(".nam"):
            setname = setname[:-4]
        elements[setname] = read_named_set(setname, all_elements)
        logging.info(f"read {len(elements[setname])} elements from set “{setname}”")
    nlist = set_normals(elements)
    logging.info(f"the given set(s) contain {len(nlist)} unique normals")
    n = 1
    with open("auto-orient.nam", "wt") as outnam, open(
        "auto-orient.inp", "wt"
    ) as outinp:
        for normal, elnums in nlist:
            logging.debug(f"normal ({normal[0]}, {normal[1]}, {normal[2]})")
            write_orientation(normal, n, outnam, args.base)
            write_elsets(n, elnums, elements, outnam, outinp)
            n += 1


def setup():
    """
    Program initialization

    Returns:
        a namespace populated with the supplied arguments.
    """
    # Process command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
    parser.add_argument(
        "-b",
        "--base",
        default="1.0,0.0,0.0",
        help="x,y,z direction vector; should not contain spaces"
    )
    parser.add_argument(
        "set",
        default="",
        nargs="*",
        help="filenames of the sets to process",
    )
    argv = sys.argv[1:]
    args = parser.parse_args(argv)
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    logging.debug(f"command-line arguments: {argv}")
    logging.debug(f"processed arguments: {args}")
    # convert the base vector
    try:
        base = tuple(float(j) for j in args.base.split(","))
        args.base = normalize(base)
    except ValueError as e:
        logging.error(f"invalid base vector {args.base}: {e}")
        sys.exit(6)
    if isinstance(args.set, str):
        if not args.set:
            logging.error("no set given; exiting")
            sys.exit(5)
        args.set = [args.set]
    return args


def read_allmsh():
    """
    Read and return the elements from “all.msh”

    Returns:
        A dict of all the elements indexed by element number.
        An element is a tuple of nodes.
        (Node numbers have been resolved to the actual nodes.)
    """
    with open("all.msh") as f:
        lines = [ln.strip() for ln in f.readlines()]
    cmds = [(num, ln) for num, ln in enumerate(lines) if ln.startswith("*")]
    if not cmds[0][1].startswith("*NODE") or cmds[0][0] != 0:
        logging.error("missing *NODE card in all.msh")
        sys.exit(1)
    if not cmds[1][1].startswith("*ELEMENT"):
        logging.error("missing *ELEMENT card in all.msh")
        sys.exit(1)
    elitems = cmds[1][1].split()
    if "C3D20" not in elitems[1]:
        logging.error("this program only works with C3D20(R) elements.")
        sys.exit(2)
    ns, ne = cmds[0][0] + 1, cmds[1][0]
    es = ne + 1

    def to_node(items):
        return (int(items[0]), tuple(float(j) for j in items[1:]))

    nodes = dict([to_node(ln.strip().split(",")) for ln in lines[ns:ne]])

    starts = (ln for ln in lines[es:] if ln.endswith(","))
    ends = (ln for ln in lines[es:] if not ln.endswith(","))

    def to_element(s, e):
        items = tuple(int(j) for j in s.split(",")[:-1]) + tuple(
            int(j) for j in e.split(",")
        )
        return (items[0], tuple(nodes[k] for k in items[1:]))

    elements = dict([to_element(s, e) for s, e in zip(starts, ends)])
    return elements


def read_named_set(setname, elements):
    """
    Read a named set of elements

    Arguments:
        setname: name of the set to read.
        elements: dictionary of elements, indexed by element number.

    Returns:
        A dictionary of the elements in the named set.
    """
    if not setname.endswith(".nam"):
        setname += ".nam"
    with open(setname) as f:
        lines = [ln.strip() for ln in f.readlines()]
    cmd = [num for num, ln in enumerate(lines) if ln.startswith("*ELSET")]
    if not cmd:
        logging.error(f"no element set found in {setname}")
        sys.exit(3)
    if len(cmd) > 1:
        logging.error(f"multiple element sets found in {setname}")
        sys.exit(4)
    es = cmd[0] + 1
    indices = [int(ln[:-1]) for ln in lines[es:]]
    return {k: elements[k] for k in indices}


def set_normals(elements):
    """
    Determine the unique normals of the elements in the set.

    Arguments:
        elements: a dict of elements, keyed by set name.

    Returns:
        A list of 2-tuples. Each tuple consists of a normal vector (3-tuple of float)
        and a tuple of element numbers that have this normal vector.
    """
    ndict = {}
    for j in elements.values():
        for num, nodes in j.items():
            # A hex element has three basic vectors.
            bases = [
                sub(nodes[4], nodes[0]),
                sub(nodes[1], nodes[0]),
                sub(nodes[3], nodes[0]),
            ]
            bases.sort(key=lambda v: -sum(j * j for j in v))
            # The normal is perpendicular to the two longest bases.
            normal = normalize(cross(bases[0], bases[1]))
            # Make normals +z
            if normal[2] < 0:
                normal = (-normal[0], -normal[1], -normal[2])
            found = False
            for n in ndict.keys():
                if isclose(normal, n):
                    ndict[n].append(num)
                    found = True
                    break
            if not found:
                ndict[normal] = [num]
    return list(ndict.items())


def isclose(u, v):
    """
    Determine if two vectors are close.
    It is assumed that the vectors are both normalized (scaled to length = 1).

    Arguments:
        u: 3-tuple of numbers
        v: 3-tuple of numbers

    Returns:
        True if u and v are equal, False otherwise
    """
    angle = math.degrees(math.acos(dot(u, v)))
    if -1 < angle < 1:
        return True
    elif 179 < angle < 181:
        return True
    return False


def cross(u, v):
    """
    Create the cross-product of two vectors

    Arguments:
        u: 3-tuple of numbers
        v: 3-tuple of numbers

    Returns:
        The cross-product between the vectors.
    """
    return (
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    )


def dot(u, v):
    """
    Create the dot-product of two vectors

    Arguments:
        u: 3-tuple of numbers
        v: 3-tuple of numbers

    Returns:
        The dot-product between the vectors.
    """
    rv = u[0] * v[0] + u[1] * v[1] + u[2] * v[2]
    if rv > 1.0:
        rv = 1.0
    elif rv < -1.0:
        rv = -1.0
    return rv


def sub(u, v):
    """
    Create the difference between two vectors.

    Arguments:
        u: 3-tuple of numbers
        v: 3-tuple of numbers

    Returns:
        The cross-product between the vectors.
    """
    return (
        u[0] - v[0],
        u[1] - v[1],
        u[2] - v[2],
    )


def normalize(v):
    """
    Scale the vector to lentgh 1.

    Arguments:
        v: tuple of numbers

    Returns:
        The scaled tuple.
    """
    ln = sum(j * j for j in v) ** 0.5
    return tuple(round(j / ln, 9) for j in v)


def write_orientation(normal, n, outnam, base=(1.0, 0.0, 0.0)):
    """
    Write *ORIENTATION card to the open file <outnam>.
    The cross-product of the normal and the base vector is the local y-axis.
    The cross-product of the local y-axis and the normal is the local x-axis.

    Arguments:
        normal: normal vector; 3-tuple of numbers
        n: number of the oriëntation
        outnam: file to write to
        base: 3D vector to align the x-axis of the element to.
    """

    factorx = dot(normal, base)
    if math.isclose(factorx, 1.0):
        logging.warning("normal lies in global X")
        locx = (0.0, 0.0, -1.0)
        locy = (0.0, 1.0, 0.0)
    else:
        locy = cross(normal, base)
        locx = cross(locy, normal)
    outnam.write(os.linesep)
    outnam.write(
        f"** normal: {normal[0]:.4f} {normal[1]:.4f} {normal[2]:.4f}" + os.linesep
    )
    outnam.write(f"*ORIENTATION, NAME=aor{n}, SYSTEM=RECTANGULAR" + os.linesep)
    # We're using full precision here. Orientations are *very* sensitive
    outnam.write(f"{locx[0]},{locx[1]},{locx[2]}, {locy[0]},{locy[1]},{locy[2]}")
    outnam.write(os.linesep + os.linesep)


def write_elsets(n, elnums, elements, outnam, outinp):
    for setname, elist in elements.items():
        active = set(elnums) & set(elist)
        if active:
            outnam.write(os.linesep)
            outnam.write(f"*ELSET,ELSET=Eaor{n}-{setname}" + os.linesep)
            for number in active:
                outnam.write(f"{number}," + os.linesep)
            outinp.write(f"*SOLID SECTION, ELSET=Eaor{n}-{setname}, ")
            outinp.write(f"ORIENTATION=aor{n}, MATERIAL=M{setname}")
            outinp.write(os.linesep)


if __name__ == "__main__":
    main()
