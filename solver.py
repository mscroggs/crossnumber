class NonexistentClue(BaseException):
    pass

class NoSolution(BaseException):
    pass

class WrongLengthAnswer(BaseException):
    pass

RED = "\033[31m"
DEFAULT = "\033[0m"

class Solver:
    def __init__(self, grid):
        self.grid = grid
        self.options = []
        self.clue_desc = {}
        self.clue_value = []
        self.clue_options = []
        self.clue_gen_f = []
        self.clue_function = []
        self.filled = []
        self.solutions = []

    def set_clue(self, clue, desc=None, value=None, options=None, function=None, finput=None):
        if isinstance(clue, str):
            if desc is not None:
                self.clue_desc[clue] = desc
            clue = [clue]
            if value is not None:
                value = [value]
            if options is not None:
                options = [(i,) for i in options]
        elif desc is not None:
            for c,d in zip(clue,desc):
                if d is not None:
                    self.clue_desc[c] = d
        if value is not None:
            self.clue_value.append((clue,value))
        if options is not None:
            self.clue_options.append((clue,options))
        if function is not None:
            if finput is None:
                self.clue_function.append((clue,function))
            else:
                if isinstance(finput, str):
                    finput = (finput,)
                self.clue_gen_f.append((clue,(function,finput)))

    def find_solutions(self,printing=False):
        self.filled = [[list(range(10)) if item else None for item in row] for row in self.grid.data]
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                if self.grid.number_positions[i][j] is not None:
                    self.filled[i][j].remove(0)

        for clues,values in self.clue_value:
            for c,v in zip(clues,values):
                for d,co in zip(str(v),self.grid.clue_dict[c].coords):
                    if int(d) not in self.filled[co[0]][co[1]]:
                        raise NoSolution
                    self.filled[co[0]][co[1]] = [int(d)]
        if printing:
            print(self)
            print("Reducing options")
        self.reduce_options()
        if printing:
            print(self)
            print("Making options from generating functions")
        self.make_options_from_gen_functions()
        if printing:
            print(self)
            print("Reducing options")
        self.reduce_options()
        if printing:
            print(self)
            print("Making options from functions")
        self.make_options_from_functions()
        if printing:
            print(self)
            print("Reducing options")
        self.reduce_options()
        if printing:
            print(self)
            print("Solving...")
        self.solutions = self.try_options(printing=printing)
        return self.solutions

    def print_all_solutions(self):
        return self.find_solutions(printing=True)

    def validate(self, done):
        filled = [[i[0] if i is not None and len(i)==0 else None for i in row] for row in self.filled]
        for clue, value in done.items():
            for digit, co in zip(str(value), self.grid.clue_dict[clue].coords):
                digit = int(digit)
                if filled[co[0]][co[1]] is not None and filled[co[0]][co[1]] != digit:
                    return False
                filled[co[0]][co[1]] = digit
        return True

    def print_solution(self, done):
        filled = [[None for i in row] for row in self.filled]
        for i,row in enumerate(self.filled):
            for j,item in enumerate(row):
                if item is not None:
                    if len(item) == 1:
                        filled[i][j] = str(item[0])
                    else:
                        filled[i][j] = " "
        for clue, value in done.items():
            for digit, co in zip(str(value), self.grid.clue_dict[clue].coords):
                filled[co[0]][co[1]] = digit

        out = u"\u2588"*(self.grid.shape[1]+2) + "\n"
        for row in filled:
            out += u"\u2588"
            for item in row:
                if item is None:
                    out += u"\u2588"
                elif len(item) == 1:
                    out += str(item[0])
                else:
                    out += " "
            out += u"\u2588"
            out += "\n"
        out += u"\u2588"*(self.grid.shape[1]+2)
        print(out)

    def try_options(self, done={}, printing=False):
        if not self.validate(done):
            return []
        todo = []
        for i,j in self.clue_options:
            for clue in i:
                if clue not in done:
                    todo.append((i,j))
                    break
        if len(todo) == 0:
            if printing:
                self.print_solution(done)
            return [done]
        out = []
        clue,options = todo[0]
        for op in options:
            out += self.try_options({**done,**{i:j for i,j in zip(clue,op)}}, printing=printing)
        return out

    def make_options_from_functions(self):
        from itertools import product
        for clues, function in self.clue_function:
            print(clues)
            op = []
            lists = []
            for c in clues:
                lists.append([int("".join(i)) for i in product(*[[str(j) for j in self.filled[co[0]][co[1]]] for co in self.grid.clue_dict[c].coords])])
            for a in product(*lists):
                if function(*a):
                    op.append(a)
            self.clue_options.append((clues,op))

    def make_options_from_gen_functions(self):
        from itertools import product
        for clues, (function, finput) in self.clue_gen_f:
            print(clues)
            op = []
            lists = []
            for c in finput:
                lists.append([int("".join(i)) for i in product(*[[str(j) for j in self.filled[co[0]][co[1]]] for co in self.grid.clue_dict[c].coords])])
            for a in product(*lists):
                b = function(*a)
                if b is not None:
                    op.append(b)
            self.clue_options.append((clues,op))

    def reduce_options(self):
        changed = False
        pre = sum(len(j) for i,j in self.clue_options)
        for n,(clues,options) in enumerate(self.clue_options):
            for i,c in enumerate(clues):
                for j,co in enumerate(self.grid.clue_dict[c].coords):
                    self.clue_options[n] = (clues,[o for o in options if int(str(o[i])[j]) in self.filled[co[0]][co[1]]])
        if pre != sum(len(j) for i,j in self.clue_options):
            changed = True

        for clues,options in self.clue_options:
            for i,c in enumerate(clues):
                for j,co in enumerate(self.grid.clue_dict[c].coords):
                    for o in range(10):
                        if o in self.filled[co[0]][co[1]]:
                            for op in options:
                                if int(str(op[i])[j]) == o:
                                    break
                            else:
                                self.filled[co[0]][co[1]].remove(o)
                                changed = True

        if changed:
            self.reduce_options()

    def __unicode__(self):
        out = u"\u2588"*(self.grid.shape[1]+2) + "\n"
        for row in self.filled:
            out += u"\u2588"
            for item in row:
                if item is None:
                    out += u"\u2588"
                elif len(item) == 1:
                    out += str(item[0])
                else:
                    out += " "
            out += u"\u2588"
            out += "\n"
        out += u"\u2588"*(self.grid.shape[1]+2)
        return out

    def __str__(self):
        return self.__unicode__()

    """def as_html(self):
        out = self.grid.as_html()

    def solution_as_html(self):
        return get_solution(self.grid, self.options).solution_as_html()

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

        return out"""
