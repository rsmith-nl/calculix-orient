#!/usr/bin/env python
"""Generate orientations and sets of elements that use them for a given
initial set of elements."""

import argparse
import logging
import math
import os
import sys

__version__ = "2022.12.22"


def main():
    """
    Entry point for calculix-orient.py.
    """
    args = setup()
    # Real work starts here.
    if not os.path.exists("all.msh"):
        logging.error("no “all.msh” file found; exiting")
        sys.exit(1)
    all_elements = read_allmsh()
    logging.info(f"read {len(all_elements)} elements from “all.msh”")
    elements = read_named_set(args.set, all_elements)
    logging.info(f"read {len(elements)} elements from set “{args.set}”")
    nlist = set_normals(elements)
    logging.info(f"“{args.set}” contains {len(nlist)} unique normals")
    result = []
    n = 1
    with open("auto-orient.nam", "wt") as outf:
        for normal, elnums in nlist:
            logging.debug(f"normal ({normal[0]}, {normal[1]}, {normal[2]})")
            factorx = dot(normal, (1.0, 0.0, 0.0))
            if math.isclose(factorx, 1.0):
                logging.warning("normal lies in global X")
                locx = (0.0, 0.0, -1.0)
                locy = (0.0, 1.0, 0.0)
            elif math.isclose(factorx, 0.0):
                logging.warning("normal is perpendicular to global X")
                locx = (1.0, 0.0, 0.0)
            else:
                locx = normalize((normal[0] + factorx, normal[1], normal[2]))
            factory = dot(normal, (0.0, 1.0, 0.0))
            if math.isclose(factory, 1.0):
                logging.warning("normal lies in global Y")
                locx = (1.0, 0.0, 0.0)
                locy = (0.0, 0.0, -1.0)
            elif math.isclose(factory, 0.0):
                logging.warning("normal is perpendicular to global Y")
                locy = (0.0, 1.0, 0.0)
            else:
                locy = normalize((normal[0], normal[1] + factory, normal[2]))
            result.append((locx, locy, elnums))
            outf.write(f"*ORIENTATION, NAME=aor{n}, SYSTEM=RECTANGULAR" + os.linesep)
            # We're using full precision here. Orientations are *very* sensitive
            outf.write(f"{locx[0]},{locx[1]},{locx[2]}, {locy[0]},{locy[1]},{locy[2]}")
            outf.write(os.linesep + os.linesep)
            outf.write(f"*ELSET,ELSET=Eaor{n}" + os.linesep)
            for number in elnums:
                outf.write(f"{number}," + os.linesep)
            outf.write(f"** *SOLID SECTION, ELSET=Eaor{n}, ORIENTATION=aor{n}, MATERIAL=?")
            outf.write(os.linesep + os.linesep)
            n += 1


def setup():
    """Program initialization"""
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
        "set",
        type=str,
        default="",
        help="filename of the set to look process",
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
    return args


def read_allmsh():
    """
    Read and return the elements from “all.msh”

        Arguments:
            none

        Returns:
            A dict of all the elements indexed by element number.
            Node numbers have been resolved to the actual nodes.
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
            elements: a dictionary of elements

        Returns:
            a list of 2-tuples of (normal vector, (relevant elements)).
    """
    ndict = {}
    for num, nodes in elements.items():
        normal = normalize(cross(sub(nodes[1], nodes[0]), sub(nodes[2], nodes[1])))
        found = False
        for n in ndict.keys():
            if isclose(normal, n):
                ndict[n].append(num)
                found = True
                break
        if not found:
            ndict[normal] = [num]
    return list(ndict.items())


def isclose(u, v, rel_tol=1e-3):
    """Determine if two vectors are close.

    Arguments:
        u: 3-tuple of numbers
        v: 3-tuple of numbers
        rel_tol: relative tolerance

    Returns:
        True is u anv v are equal, False otherwise
    """
    return all(math.isclose(u[j], v[j], rel_tol=rel_tol) for j in (0, 1, 2))


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
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


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
    return tuple(j / ln for j in v)


if __name__ == "__main__":
    main()
