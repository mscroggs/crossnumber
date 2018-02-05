def print_all(grid, options):
    if len(options) == 0:
        if grid.test():
            print(grid)
    else:
        arg = options[0]
        for i in arg[1]:
            for a,b in zip(arg[0],i):
                grid.set_clue(a,b)
            if grid.test():
                print_all(grid, options[1:])
            for a in arg[0]:
                grid.unset_clue(a)

class Solver:
    def __init__(self, grid):
        self.grid = grid
        self.options = []
        self.clue_desc = {}

    def set_clue(self, clue, value, desc=None):
        self.grid.set_clue(clue, value)
        self.clue_desc[clue] = desc

    def set_clue_options(self, clues, options, descs=None):
        if isinstance(clues, str):
            self.options.append(([clues],[[i] for i in options]))
            self.clue_desc[clues] = descs
        else:
            if descs is None:
                descs = [None for i in clues]
            self.options.append((clues, options))
            for clue,desc in zip(clues,descs):
                self.clue_desc[clue] = desc


    def find_solutions(self):
        print_all(self.grid, self.options)

    def as_latex(self):
        out = self.grid.as_latex()
        out += "\n\n"
        out += "Across\n"
        out += "\\begin{tabular}{>{\\bfseries}r p{5.8cm} >{\\bfseries}r}\n"
        for i in range(len(self.grid.starts)):
            key = "a"+str(i)
            if key in self.grid.clues:
                out += str(i)+"&"
                try:
                    out += self.clue_desc[key]
                except:
                    pass
                out += "&(" + str(self.grid.clues[key]) + ")\\\\\n"
        out += "\\end{tabular}"

        out += "\n\n"
        out += "Down\n"
        out += "\\begin{tabular}{>{\\bfseries}r p{5.8cm} >{\\bfseries}r}\n"
        for i in range(len(self.grid.starts)):
            key = "d"+str(i)
            if key in self.grid.clues:
                out += str(i)+"&"
                try:
                    out += self.clue_desc[key]
                except:
                    pass
                out += "&(" + str(self.grid.clues[key]) + ")\\\\\n"
        out += "\\end{tabular}"

        return out
