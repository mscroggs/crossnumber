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

    def set_clue(self, *args, **kwargs):
        self.grid.set_clue(*args, **kwargs)

    def set_clue_options(self, clues, options):
        if isinstance(clues, str):
            self.options.append(([clues],[[i] for i in options]))
        else:
            self.options.append((clues, options))

    def find_solutions(self):
        print_all(self.grid, *self.options)
