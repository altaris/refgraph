"""
Entry point
"""
__docformat__ = "google"

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
import re
import sys

from pylatexenc.latexwalker import (
    LatexEnvironmentNode,
    LatexMacroNode,
    LatexNode,
    LatexWalker,
)
import click
import graphviz

try:
    # pylint: disable=redefined-builtin
    from rich import print
except ImportError:
    pass


REFERENCE_MACROS = ["cref", "eqref", "ref", "vref"]
MAIN_ENVIRONMENTS = [
    "assertion",
    "assertion*",
    "assertions",
    "assertions*",
    "axiom",
    "axiom*",
    "axioms",
    "axioms*",
    "conjecture",
    "conjecture*",
    "conjectures",
    "conjectures*",
    "convention",
    "convention*",
    "conventions",
    "conventions*",
    "corollaries",
    "corollaries*",
    "corollary",
    "corollary*",
    "definition",
    "definition*",
    "definitions",
    "definitions*",
    "example",
    "example*",
    "examples",
    "examples*",
    "exercise",
    "exercise*",
    "exercises",
    "exercises*",
    "lemma",
    "lemma*",
    "lemmas",
    "lemmas*",
    "notation",
    "notation*",
    "notations",
    "notations*",
    "properties",
    "properties*",
    "property",
    "property*",
    "proposition",
    "proposition*",
    "propositions",
    "propositions*",
    "question",
    "question*",
    "questions",
    "questions*",
    "remark",
    "remark*",
    "remarks",
    "remarks*",
    "reminder",
    "reminder*",
    "reminders",
    "reminders*",
    "scholia",
    "scholia*",
    "scholias",
    "scholias*",
    "terminologies",
    "terminologies*",
    "terminology",
    "terminology*",
    "theorem",
    "theorem*",
    "theorems",
    "theorems*",
]


@dataclass
class Reference:
    """
    A reference is given by the following data:
    * `from_` the label of the environment / section where the reference is
      located (aka the "parent" of the reference);
    * `to` the label being referenced.
    """

    from_: Optional[str]
    to: str


def get_references(
    nodes: List[LatexNode],
    label: Optional[str] = None,
) -> Tuple[Optional[str], List[Reference]]:
    """
    Produces a list of references (from/to pairs) from a list of `LatexNode`s.

    Args:
        nodes: List of `LatexNode`s
        label: Optional override for the overarching label for this list of
            nodes. In other words, any "orphan" \ref found in this list will be
            parented to this label.

    Returns:
        The found overarching label for this list of nodes, with the list of references.
    """
    local_references: List[str] = []
    all_references: List[Reference] = []
    last_label: Optional[str] = None
    for node in nodes:
        if isinstance(node, LatexMacroNode):
            if node.macroname == "label" and label is None:
                label = node.nodeargd.argnlist[0].nodelist[0].chars
            elif str(node.macroname).lower() in REFERENCE_MACROS:
                r = node.nodeargd.argnlist[0].nodelist[0].chars
                local_references += re.split(r",\s*", r)
        if isinstance(node, LatexEnvironmentNode):
            if node.environmentname in MAIN_ENVIRONMENTS:
                last_label, environment_references = get_references(
                    nodes=node.nodelist,
                )
            else:
                _, environment_references = get_references(
                    nodes=node.nodelist,
                    label=last_label,
                )
            all_references += environment_references
    all_references += [Reference(label, r) for r in set(local_references)]
    for r in all_references:
        if not r.from_:
            r.from_ = label
    return label, all_references


@click.command()
@click.argument(
    "FILES",
    nargs=-1,
    type=click.Path(
        dir_okay=False,
        exists=True,
        file_okay=True,
        path_type=Path,
        readable=True,
        resolve_path=True,
    ),
)
def main(files: Tuple[Path]):
    """Entrypoint."""
    if not files:
        print("ERROR: Must specify at least one source file.")
        sys.exit(-1)

    all_references: List[Reference] = []
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            walker = LatexWalker(f.read())
        nodelist, *_ = walker.get_latex_nodes(pos=0)
        _, references = get_references(nodelist)
        all_references += references

    graph = graphviz.Digraph()
    for r in all_references:
        if r.from_:
            graph.edge(r.from_.replace(":", "-"), r.to.replace(":", "-"))

    graph.render("graph.gv")


# pylint: disable=no-value-for-parameter
main()
