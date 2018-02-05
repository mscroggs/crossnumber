def print_all(grid, *args):
    if len(args) == 0:
        if grid.test():
            print(grid)
    else:
        arg = args[0]
        for i in arg[1]:
            for a,b in zip(arg[0],i):
                grid.set_clue(a,b)
            if grid.test():
                print_all(grid, *args[1:])
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
            self.options.append(([clues],[[i] for i in options],[descs]))
        else:
            if descs is None:
                descs = [None for i in clues]
            self.options.append((clues, options, descs))

    def find_solutions(self):
        print_all(self.grid, *self.options)

    def as_latex(self):
        return self.grid.as_latex()
