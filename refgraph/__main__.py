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

    def __hash__(self) -> int:
        return hash(str(self.from_) + "\\" + self.to)

    def add_edge_to_graph(self, graph: graphviz.Digraph) -> None:
        """Adds this reference as an edge to a graph."""
        if not self.from_:
            return
        a = str(hash(self.from_))
        b = str(hash(self.to))
        graph.node(a, self.from_)
        graph.node(b, self.to)
        graph.edge(a, b)


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
    references: List[Reference] = []
    last_label: Optional[str] = None
    for node in nodes:
        if isinstance(node, LatexMacroNode):
            if node.macroname == "label" and label is None:
                label = node.nodeargd.argnlist[0].nodelist[0].chars
            elif str(node.macroname).lower() in REFERENCE_MACROS:
                r = node.nodeargd.argnlist[0].nodelist[0].chars
                references += [
                    Reference(None, l) for l in re.split(r",\s*", r)
                ]
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
            references += environment_references
    for r in references:
        if not r.from_:
            r.from_ = label
    return label, references


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
@click.option(
    "-o",
    "--output-directory",
    default=Path("."),
    required=False,
    type=click.Path(
        exists=True,
        file_okay=False,
        path_type=Path,
        resolve_path=True,
        writable=True,
    ),
)
def main(files: Tuple[Path], output_directory: Path):
    """Entrypoint."""
    if not files:
        print("ERROR: Must specify at least one source file.")
        sys.exit(-1)

    all_references: List[Reference] = []
    for file_path in files:
        print(f"Reading file {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            walker = LatexWalker(f.read())
        nodelist, *_ = walker.get_latex_nodes(pos=0)
        _, references = get_references(nodelist)
        all_references += references

    graph = graphviz.Digraph()
    graph.attr("node", shape="box")
    for r in set(all_references):
        r.add_edge_to_graph(graph)

    print(f"Rendering graph to {str(output_directory)}")
    graph.render(output_directory / "graph.gv")


# pylint: disable=no-value-for-parameter
main()
