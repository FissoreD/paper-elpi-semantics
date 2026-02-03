import os, sys, re

# OPEN_COMMENT = "(*"
# END_COMMENT = "*)"
# OUT_DIR = "tex_code"
# EXTENTION = "v"
# MINT_TAG = "coqcode"
# OPEN_TAG = "SNIP:"
# CLOSE_TAG = "ENDSNIP"

def clean_line_global(l):
    l = l.replace("successT", "success")
    l = l.replace("failedT", "failed")
    l = l.replace("Sigma", "~$\\Sigma$~")
    # l = l.replace("tree", "~$\\tau$~")
    l = l.replace("empty", "~$\\epsilon$~")
    l = l.replace("fvS", "~$\\mathcal{F}_{\\!\\!\\nu}$~")
    l = l.replace("bool", "~$\\mathbb{B}$~")
    l = l.replace("program", "~$\\mathbb{P}$~")
    l = l.replace("<->", "~$\\leftrightarrow$~")
    l = l.replace("->", "~$\\to$~")
    l = l.replace("=>", "~$\\Rightarrow$~")
    l = l.replace(":=", "~$\\coloneq$~")
    l = l.replace("step_tag", "tag") # FIXME
    return l

def latexify(expr):
    expr = expr.replace("->", r"\to")
    expr = expr.replace("_", r"\_")
    expr = expr.replace("(", r"(")
    expr = expr.replace(")", r")")
    return expr.strip()

class C:
    def __init__(self,oc,ec,od,ext,ot,ct):
        self.OPEN_COMMENT = oc
        self.END_COMMENT = ec
        self.OUT_DIR = od
        self.EXTENSION = ext
        self.OPEN_TAG = ot
        self.CLOSE_TAG = ct

    def get_file_cnt(self,lines):
        res = []
        try:
            indexBegin = lines.index(f"{self.OPEN_COMMENT}BEGIN{self.END_COMMENT}\n")
            indexEnd = lines.index(f"{self.fOPEN_COMMENT}END{self.END_COMMENT}\n")
            res = lines[indexBegin+1:indexEnd]
        finally:
            return res

    def clean_line(self,l):
        # COMMENT
        l = re.sub(fr"^ *{re.escape(self.OPEN_COMMENT)}.*\n","",l)
        return clean_line_global(l)
        

    def mk_fname(self,fname):
        return fname.split("/")[-1][:-(len(self.EXTENTION))] + "tex"

    def get_snippets(self, lines):
        snips = {}
        cursnips = []
        curnames = []
        # invariant the length of cursnips and curnames is the same
        for l in lines:
            m = re.match(rf"^ *{re.escape(self.OPEN_COMMENT)}{self.OPEN_TAG} *(.*) *{re.escape(self.END_COMMENT)}$",l)
            if m is not None:
                # entering a new snip
                name = m.group(1).strip()
                curnames.append(name)
                # if we open again a closed snippet we add the content to the previous snip
                cursnips.append(cursnips[name] if name in cursnips else [])
            else:
                m = re.match(rf"^ *{re.escape(self.OPEN_COMMENT)}{self.CLOSE_TAG}",l)
                if m is None:
                    # we are not exiting, we add the new line l to all current snips
                    # note that if cursnips is the empty list nothing is done
                    for x in cursnips:
                        x.append(l)
                else:
                    # we are exiting a snippet, by default we close the 
                    if len(cursnips)>0:
                        snips[curnames.pop()] = cursnips.pop()
        return snips

    def read_file(self,fname):
        with open(fname) as f:
            lines = f.readlines()
            # print_tex(get_file_cnt(lines), mk_fname(fname))
            snippets = self.get_snippets(lines)
            for (fname,lines) in snippets.items():
                self.print_tex(lines, fname + ".tex")
                # print_tex(lines, fname + "_raw.tex", True)

    def print_tex(lines, fout, raw = False):
        raise Exception("TO BE IMPLEMENTED IN CHILD")

    def write(self,fout,cnt):
        if not os.path.exists(self.OUT_DIR):
            os.makedirs(self.OUT_DIR)
        fout = f"{self.OUT_DIR}/{fout}"
        with open(fout, "w") as f:
            f.write(cnt)

class snip(C):
    def __init__(self,mintag):
        super(snip,self).__init__("(*","*)","tex_code","v","SNIP:","ENDSNIP")
        self.MINT_TAG = mintag

    def print_tex(self,lines, fout, raw = False):
        if lines == []: return
        cnt = ""
        if not raw:
            cnt += (f"\\begin{{{self.MINT_TAG}}}\n")
        for l in lines:
            cnt += self.clean_line(l)
        if not raw:
            cnt += f"\\end{{{self.MINT_TAG}}}\n"
        super().write(fout,cnt)

def latexify(expr):
    expr = expr.replace("->", r"\to")
    expr = expr.replace("_", r"\_")
    expr = expr.replace("(", r"(")
    expr = expr.replace(")", r")")
    return expr.strip()

def flatten(xss):
    return [x for xs in xss for x in xs]

# Returns the bussproof representation of an inductive:
# it does not work for:
# inductive with hypothesis containing arrows
# mutual recursive inductives
class bussproof(C):
    def __init__(self):
        super(bussproof,self).__init__("(*","*)","tex_code","v","prooftree:","endprooftree")

    def print_bp(self,name,hyps,concl):
        lines = ["\\begin{prooftree}"]
        for s in hyps:
            lines.append(f"  \\AxiomC{{$${latexify(s)}$$}}")

        n = len(hyps)
        if n == 0:
            n = 1
            lines.append(f"  \\AxiomC{{}}")

        lines.append(f"  \\RightLabel{{\\textsc{{{latexify(name)}}}}}")

        L = ["Unary","Binary","Trinary"]

        if n > len(L):
            raise ValueError("Too many premises for bussproofs")
        else:
            tag = L[n-1]

        lines.append(f"  \\{tag}InfC{{$${latexify(concl)}$$}}")

        lines.append("\\end{prooftree}")
        return "\n".join(lines)

    def clean_line(self, l):
        l = l.replace("\n","")
        l = l.replace("&", "\&")
        l = l.strip()
        return l
    
    def split_hyps(self,hyps):
        hyps = hyps.split("->")
        hyps = [self.clean_line(i) for i in hyps]
        return hyps

    def parse_inductive (self,l):
        l = l.split(":",1)
        cname = l[0].split(maxsplit=1)[0]
        hyps = flatten([self.split_hyps(i) for i in l[1:]])
        return self.print_bp(cname, hyps[:-1],hyps[-1])

    # each constructor should be on a new line
    def print_tex(self,lines, fout, raw = False):
        for (i,e) in enumerate(lines):
            lines[i] = super().clean_line(e)
            
        lines = "".join(lines)
        lines = lines.split("|")
        cnt = ""
        for i in lines[1:]:
            cnt += "\n"+self.parse_inductive(i)
        super().write(fout,cnt)

if __name__ == "__main__":
    fname = sys.argv[1]
    bussproof().read_file(fname)
    snip("coqcode").read_file(fname)