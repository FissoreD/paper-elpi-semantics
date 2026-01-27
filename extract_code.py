import os, sys, re

OPEN_COMMENT = "(*"
END_COMMENT = "*)"
OUT_DIR = "tex_code"
EXTENTION = "v"
MINT_TAG = "coqcode"

def get_file_cnt(lines):
    res = []
    try:
        indexBegin = lines.index(f"{OPEN_COMMENT}BEGIN{END_COMMENT}\n")
        indexEnd = lines.index(f"{OPEN_COMMENT}END{END_COMMENT}\n")
        res = lines[indexBegin+1:indexEnd]
    finally:
        return res

def clean_line(l):
    # COMMENT
    l = re.sub(fr"^ *{re.escape(OPEN_COMMENT)}.*\n","",l)
    
    l = l.replace("successT", "success")
    l = l.replace("failedT", "failed")
    return l

def print_tex(lines, fout, raw = False):
    if lines == []: return
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    fout = f"{OUT_DIR}/{fout}"
    with open(fout, "w") as f:
        if not raw:
            f.write(f"\\begin{{{MINT_TAG}}}\n")
        for l in lines:
            l = clean_line(l)
            f.write(l)
        if not raw:
            f.write(f"\\end{{{MINT_TAG}}}\n")

def mk_fname(fname):
    return fname.split("/")[-1][:-(len(EXTENTION))] + "tex"

def get_snippets(lines):
    snips = {}
    cursnips = []
    curnames = []
    # invariant the length of cursnips and curnames is the same
    for l in lines:
        m = re.match(rf"^ *{re.escape(OPEN_COMMENT)}SNIP: *(.*) *{re.escape(END_COMMENT)}$",l)
        if m is not None:
            # entering a new snip
            name = m.group(1).strip()
            curnames.append(name)
            # if we open again a closed snippet we add the content to the previous snip
            cursnips.append(cursnips[name] if name in cursnips else [])
        else:
            m = re.match(rf"^ *{re.escape(OPEN_COMMENT)}ENDSNIP",l)
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

def read_file(fname):
    with open(fname) as f:
        lines = f.readlines()
        # print_tex(get_file_cnt(lines), mk_fname(fname))
        snippets = get_snippets(lines)
        for (fname,lines) in snippets.items():
            print_tex(lines, fname + ".tex")
            # print_tex(lines, fname + "_raw.tex", True)

        
if __name__ == "__main__":
    fname = sys.argv[1]
    # print(sys.argv)
    read_file(fname)