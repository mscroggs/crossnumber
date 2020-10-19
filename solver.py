from itertools import product

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
        self.clue_desc = {}
        self.clue_value = []
        self.clue_options = []
        self.clue_gen_f = []
        self.clue_function = []
        self.clue_function_check = []
        self.filled = []
        self.solutions = []
        self.prepared = False

    def set_clue(self, clue, desc=None, value=None, options=None, function=None, finput=None, checkonly=False):
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
                if checkonly:
                    self.clue_function_check.append((clue,(function,clue)))
                else:
                    self.clue_function.append((clue,function))
            else:
                if isinstance(finput, str):
                    finput = (finput,)
                if checkonly:
                    self.clue_function_check.append((clue,(function,finput)))
                else:
                    self.clue_gen_f.append((clue,(function,finput)))

    def prepare(self,printing=False):
        self.prepared = True
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
            print("Reducing options")
        self.reduce_options()
        if printing:
            print(self)
            print("Making options from generating functions")
        self.make_options_from_gen_functions()
        if printing:
            print("Reducing options")
        self.reduce_options()
        if printing:
            print(self)
            print("Making options from functions")
        self.make_options_from_functions()
        if printing:
            print("Reducing options")
        self.reduce_options()
        for clue,op in self.clue_options:
            if len(op) == 0:
                if printing:
                    print("No options for",clue)
                return []
        for i,row in enumerate(self.filled):
            for j,item in enumerate(row):
                if item is not None and len(item)==0:
                    if printing:
                        print("No options at",(i,j))
                    return []

    def find_solutions(self,printing=False):
        if not self.prepared:
            self.prepare(printing=printing)
        if printing:
            print(self)
            n = 1
            for i in self.clue_options:
                n *= len(i[1])
            print("Solving... ("+str(n)+" options to try)")
            maxi = (0,None)
            for i in self.clue_options:
                if len(i[1]) > maxi[0]:
                    maxi = (len(i[1]),i[0])
            print("Most options ("+str(maxi[0])+"):",maxi[1])
        self.solutions = self.try_options(printing=printing)
        if printing:
            sols = len(self.solutions)
            if sols == 1:
                print("There is 1 solution.")
            else:
                print("There are",sols,"solutions.")

            if sols > 0:
                self.print_unique(self.solutions)
        return self.solutions


    def solve_part(self, cluelist, printing=False):
        if printing:
            print("Solving a small part of the crossnumber:",cluelist)
        minisolver = Solver(self.grid)
        for i,clues in enumerate(self.clue_options):
            for c in clues[0]:
                if c in cluelist:
                    minisolver.clue_options.append(clues)
                    break
        for clues in self.clue_function_check:
            for c in clues[1][1]:
                if c in cluelist:
                    minisolver.clue_function_check.append(clues)

        minisolver.filled = self.filled
        solutions = minisolver.try_options(done={i:j for i,j in self.clue_value},printing=printing)

        filled = [[None for i in row] for row in self.filled]

        for sol in solutions:
            for clue, n in sol.items():
                for co,digit in zip(self.grid.clue_dict[clue].coords,str(n)):
                    if filled[co[0]][co[1]] is None:
                        filled[co[0]][co[1]] = []
                    if int(digit) not in filled[co[0]][co[1]]:
                        filled[co[0]][co[1]].append(int(digit))

        if printing:
            print("Filtering digits")

        for i,row in enumerate(filled):
            for j,item in enumerate(row):
                if item is not None:
                    for digit in range(10):
                        if digit in self.filled[i][j] and digit not in item:
                            self.filled[i][j].remove(digit)

        if printing:
            print("Reducing options")
        self.reduce_options()
        if printing:
            print(self)

    def print_all_solutions(self):
        return self.find_solutions(printing=True)

    def can_add(self, done, clue, value):
        for a,co in enumerate(self.grid.clue_dict[clue].coords):
            for c,b in self.grid.clues_in_space[co[0]][co[1]]:
                if c in done and str(done[c])[b] != str(value)[a]:
                    return False
        return True

    def validate(self, done):
        for _,(func, finp) in self.clue_function_check:
            for c in finp:
                if c not in done:
                    break
            else:
                if not func(*[done[c] for c in finp]):
                    return False
        filled = [[i[0] if i is not None and len(i)==1 else None for i in row] for row in self.filled]
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

    def html_solution(self, done):
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

        out = "<table>\n"
        for row in filled:
            out += "<tr>"
            for item in row:
                if item is None:
                    out += "<td class='black'></td>"
                else:
                    assert len(item) == 1
                    out += f"<td>{item[0]}</td>"
            out += "</tr>\n"
        out += "</table>"
        return out

    def finish_off(self, done):
        filled = [[j for j in i] for i in self.filled]
        for clue,value in done.items():
            for co,digit in zip(self.grid.clue_dict[clue].coords,str(value)):
                filled[co[0]][co[1]] = [int(digit)]
        todos = []
        acceptables = []
        for _,(func, finp) in self.clue_function_check:
            todo = [i for i in finp if i not in done]
            if len(todo) == 0 and not func(*[done[i] for i in finp]):
                return []
            if len(todo) > 0:
                options = []
                for clue in todo:
                    opthis = []
                    for digits in product(*[filled[co[0]][co[1]] for co in self.grid.clue_dict[clue].coords]):
                        opthis.append(int("".join([str(i) for i in digits])))
                    options.append(opthis)
                acceptable = []
                for op in product(*options):
                    if func(*[op[todo.index(i)] if i in todo else done[i] for i in finp]):
                        acceptable.append(op)
                acceptables.append(acceptable)
                todos.append(todo)
        if len(todos) == 0:
            return [done]
        out = []
        for choice in product(*acceptables):
            new = {}
            for i,j in zip(todos,choice):
                new = {**new,**{a:b for a,b in zip(i,j)}}
            sol = {**done,**new}
            if self.check(sol) and sol not in out:
                out.append(sol)
        return out

    def check(self, done):
        for _,(func, finp) in self.clue_function_check:
            if not func(*[done[i] for i in finp]):
                return False
        return True

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
            sols = self.finish_off(done)
            if printing:
                for s in sols:
                    self.print_solution(s)
            return sols
        out = []
        todo.sort(key=lambda x:self.rating(x[0],x[1],done))
        clue,options = todo[0]
        for op in options:
            for c,o in zip(clue,op):
                if not self.can_add(done,c,o):
                    break
            else:
                out += self.try_options({**done,**{i:j for i,j in zip(clue,op)}}, printing=printing)
        return out

    def rating(self, clue, options, done):
        out = 0
        for c in clue:
            for co in self.grid.clue_dict[c].coords:
                if len(self.filled[co[0]][co[1]]) == 1:
                    out += 1
                for c2 in self.grid.clues_in_space[co[0]][co[1]]:
                    if c2 != c and c2 not in done:
                        out += 1
        return out

    def make_options_from_functions(self):
        for clues, function in self.clue_function:
            op = []
            lists = []
            for c in clues:
                lists.append([int("".join(i)) for i in product(*[[str(j) for j in self.filled[co[0]][co[1]]] for co in self.grid.clue_dict[c].coords])])
            for a in product(*lists):
                if function(*a):
                    for c,i in zip(clues,a):
                        if len(str(i)) != self.grid.clue_dict[c].length:
                            break
                    else:
                        op.append(a)
            self.clue_options.append((clues,op))

    def make_options_from_gen_functions(self):
        for clues, (function, finput) in self.clue_gen_f:
            op = []
            lists = []
            for c in finput:
                lists.append([int("".join(i)) for i in product(*[[str(j) for j in self.filled[co[0]][co[1]]] for co in self.grid.clue_dict[c].coords])])
            for a in product(*lists):
                b = function(*a)
                try:
                    len(b)
                except:
                    b = [b]
                if b is not None:
                    for c,i in zip(clues,b):
                        if len(str(i)) != self.grid.clue_dict[c].length:
                            break
                    else:
                        op.append(b)
            self.clue_options.append((clues,op))

    def reduce_options(self, printing=False):
        changed = False
        pre = sum(len(j) for i,j in self.clue_options)
        for n,(clues,options) in enumerate(self.clue_options):
            for i,c in enumerate(clues):
                for j,co in enumerate(self.grid.clue_dict[c].coords):
                    self.clue_options[n] = (clues,[o for o in self.clue_options[n][1] if int(str(o[i])[j]) in self.filled[co[0]][co[1]]])

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
            if printing:
                print("Reducing again")
            self.reduce_options()

        for i,j in self.clue_options:
            if len(j) == 0:
                if printing:
                    print("No options for",i)

        for i in self.clue_options:
            if len(i[1]) == 1:
                for c,v in zip(i[0],i[1][0]):
                    self.clue_value.append((c,v))
        self.clue_options = [i for i in self.clue_options if len(i[1]) != 1]

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

    def print_unique(self,solutions):
        filled = [[None if i is None else (i if len(i)==1 else []) for i in row] for row in self.filled]
        for s in solutions:
            for clue,value in s.items():
                for co,digit in zip(self.grid.clue_dict[clue].coords,str(value)):
                    if int(digit) not in filled[co[0]][co[1]]:
                        filled[co[0]][co[1]].append(int(digit))
######
        print(u"\u2588"*(self.grid.shape[1]+2))
        for row in filled:
            out = u"\u2588"
            for item in row:
                if item is None:
                    out += u"\u2588"
                elif len(item) == 1:
                    out += str(item[0])
                else:
                    out += " "
            out += u"\u2588"
            print(out,*[i for i in row if i is not None and len(i)>1])
        print("\u2588"*(self.grid.shape[1]+2))

    def __str__(self):
        return self.__unicode__()

    """def as_html(self):
        out = self.grid.as_html()

    def solution_as_html(self):
        return get_solution(self.grid, self.options).solution_as_html()
"""
    def as_latex(self):
        out = self.grid.as_latex()
        out += "\n\n"
        out += "\\begin{crossnumberclues}{Across}\n"
        for i in range(1,self.grid.largest_clue+1):
            key = "a"+str(i)
            if key in self.grid.clue_dict:
                out += str(i)+"&"
                try:
                    out += self.clue_desc[key]
                except:
                    pass
                out += "&(" + str(self.grid.clue_dict[key].length) + ")\\\\\n"
        out += "\\end{crossnumberclues}\n\\hfill\n"

        out += "\\begin{crossnumberclues}{Down}\n"
        for i in range(1,self.grid.largest_clue+1):
            key = "d"+str(i)
            if key in self.grid.clue_dict:
                out += str(i)+"&"
                try:
                    out += self.clue_desc[key]
                except:
                    pass
                out += "&(" + str(self.grid.clue_dict[key].length) + ")\\\\\n"
        out += "\\end{crossnumberclues}"

        return out

    def save_latex(self, filename):
        with open(filename,"w") as f:
            f.write(self.as_latex())

