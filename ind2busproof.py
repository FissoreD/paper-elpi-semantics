import re
from textwrap import indent

INDUCTIVE_RE = re.compile(r"Inductive\s+(\w+)\s*:(.*?)Prop\s*:=", re.S)
CONSTRUCTOR_RE = re.compile(r"\|\s*(\w+)\s*:(.*?)(?=\n\s*\||\Z)", re.S)

def latexify(expr):
    expr = expr.replace("->", r"\to")
    expr = expr.replace("_", r"\_")
    expr = expr.replace("(", r"(")
    expr = expr.replace(")", r")")
    return expr.strip()

def parse_constructor(body, inductive_name):
    # Remove forall
    body = re.sub(r"forall.*?,", "", body, flags=re.S)

    parts = [p.strip() for p in body.split("->")]
    conclusion = parts[-1]
    premises = parts[:-1]

    inductive_premises = []
    side_conditions = []

    for p in premises:
        if p.startswith(inductive_name):
            inductive_premises.append(p)
        else:
            side_conditions.append(p)

    return side_conditions, inductive_premises, conclusion

def build_prooftree(name, sides, recs, concl):
    lines = ["\\begin{prooftree}"]

    for s in sides + recs:
        lines.append(f"  \\AxiomC{{$${latexify(s)}$$}}")

    n = len(sides) + len(recs)
    if n == 0:
        lines.append(f"  \\AxiomC{{}}")
        lines.append(f"  \\RightLabel{{\\textsc{{{latexify(name)}}}}}")
        lines.append(f"  \\UnaryInfC{{$${latexify(concl)}$$}}")
    elif n == 1:
        lines.append(f"  \\UnaryInfC{{$${latexify(concl)}$$}}")
    elif n == 2:
        lines.append(f"  \\BinaryInfC{{$${latexify(concl)}$$}}")
    elif n == 3:
        lines.append(f"  \\TrinaryInfC{{$${latexify(concl)}$$}}")
    else:
        raise ValueError("Too many premises for bussproofs")

    lines.append("\\end{prooftree}")
    return "\n".join(lines)

def coq_to_bussproof(coq_text):
    inductive_name = coq_text
    print(inductive_name)
    constructors = CONSTRUCTOR_RE.findall(coq_text)

    print ("CONSTRUCTORSS ARE", constructors)

    # proofs = []
    # for cname, body in constructors:
    #     sides, recs, concl = parse_constructor(body, inductive_name)
    #     proofs.append(build_prooftree(cname, sides, recs, concl))

    # return "\n\n".join(proofs)


if __name__ == "__main__":
    import sys
    coq_input = sys.stdin.read()
    print(coq_to_bussproof(coq_input))