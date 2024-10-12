class Clue:
    def __init__(self, type, number, length, row, col):
        self.type = type
        self.number = number
        self.length = length
        self.row = row
        self.col = col
        if type == "a":
            self.coords = [(self.row,self.col+i) for i in range(length)]
        if type == "d":
            self.coords = [(self.row+i,self.col) for i in range(length)]

class CrossnumberGrid:
    def __init__(self, grid):
        self.data = []
        for row in grid.strip().split("\n"):
            rowdata = []
            for item in row:
                rowdata.append(item==".")
            self.data.append(rowdata)
        self.shape = (len(self.data),len(self.data[0]))

        self.clues_in_space = [[[] for i in range(self.shape[1])] for j in range(self.shape[0])]
        self.clue_dict = {}
        self.clues = []
        self.number_positions = [[None for i in range(self.shape[1])] for j in range(self.shape[0])]
        n = 0
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if self.data[i][j] and i+1<self.shape[0] and self.data[i+1][j] and (i==0 or not self.data[i-1][j]):
                    n += 1
                    self.number_positions[i][j] = n
                    a = 0
                    while a+i<self.shape[0] and self.data[i+a][j]:
                        self.clues_in_space[i+a][j].append(("d"+str(n),a))
                        a += 1
                    self.clues.append(Clue("d",n,a,i,j))
                    self.clue_dict["d"+str(n)] = self.clues[-1]
                if self.data[i][j] and j+1<self.shape[1] and self.data[i][j+1] and (j==0 or not self.data[i][j-1]):
                    if self.number_positions[i][j] is None:
                        n += 1
                        self.number_positions[i][j] = n
                    a = 0
                    while a+j<self.shape[1] and self.data[i][j+a]:
                        self.clues_in_space[i][j+a].append(("a"+str(n),a))
                        a += 1
                    self.clues.append(Clue("a",n,a,i,j))
                    self.clue_dict["a"+str(n)] = self.clues[-1]
        self.largest_clue = n

    def as_latex(self):
        out = "\\begin{Puzzle}" + "{"+str(self.shape[0])+"}{"+str(self.shape[1])+"}"
        out += "\n"
        for i,row in enumerate(self.data):
            for j,cell in enumerate(row):
                out += "|"
                if cell:
                    out += "["
                    n = self.number_positions[i][j]
                    if n is not None:
                        out += str(n)
                    out += "][wf]0"
                else:
                    out += "*"
            out += "|.\n"
        out += "\\end{Puzzle}"

        return out

    def as_new_latex(self):
        out = "\\begin{tikzpicture}[x=8mm,y=8mm]"
        out += "\n"
        out += f"\\fill[white] (0,0) rectangle {self.shape};\n"
        out += f"\\foreach \\x in {{0, ..., {self.shape[0]}}}\n"
        out += f"  \\draw[line width=0.5pt, black] (\\x,0) -- (\\x,{self.shape[1]});\n"
        out += f"\\foreach \\y in {{0, ..., {self.shape[1]}}}\n"
        out += f"  \\draw[line width=0.5pt, black] (0,\\y) -- ({self.shape[0]},\\y);\n"

        out += f"\\fill[black]"
        for i, row in enumerate(self.data):
            for j, cell in enumerate(row):
                if not cell:
                    out += f" ({j},{self.shape[1]-i}) rectangle +(1,-1)"
        out += ";\n"
        for i, row in enumerate(self.data):
            for j, cell in enumerate(row):
                if cell:
                    n = self.number_positions[i][j]
                    if n is not None:
                        out += f"\\node[anchor=north west,inner sep=1pt] at ({j},{self.shape[1]-i}) {{\\footnotesize{n}}};\n"
                        pass
        out += "\\end{tikzpicture}"

        return out

    def plot(self):
        import matplotlib.pylab as plt
        for i in range(self.shape[0]+1):
            plt.plot([i,i],[0,self.shape[1]],"k")
        for i in range(self.shape[1]+1):
            plt.plot([0,self.shape[0]],[i,i],"k")
        for x in range(self.shape[0]):
            for y in range(1,self.shape[1]+1):
                if not self.data[-y][x]:
                    plt.fill([x,x,x+1,x+1],[y,y-1,y-1,y],"k")
        plt.axis("equal")
        plt.axis("off")
        plt.show()

    def intersect(self, c1, c2):
        if c1.type == c2.type:
            return None
        if c1.type == "a":
            a = c1
            d = c2
        else:
            d = c1
            a = c2
        if a.col <= d.col < a.col+a.length and d.row <= a.row < d.row+d.length:
            return (d.col,a.row)
        return None

    def __str__(self):
        return self.__unicode__()

    def get(self, item):
        if not item:
            return u"\u2588"
        return " "

    def __unicode__(self):
        out = u"\u2588"*(self.shape[1]+2) + "\n"
        out += "\n".join([u"\u2588"+"".join([self.get(a) for a in row])+u"\u2588" for row in self.data])
        out += "\n" + u"\u2588"*(self.shape[1]+2)
        return out

    def as_html(self):
        out = "\\begin{Puzzle}" + ("{"+str(self.size)+"}")*2
        out += "\n"
        for i,row in enumerate(self.grid):
            for j,cell in enumerate(row):
                out += "|"
                if len(cell) == 0:
                    out += "*"
                else:
                    out += "["
                    n = self.n(i,j)
                    if n is not None:
                        out += str(self.n(i,j))
                    out += "][wf]0"
            out += "|.\n"
        out += "\\end{Puzzle}"

        return out

    def save_latex(self, filename):
        with open(filename,"w") as f:
            f.write(self.as_latex())

    def save_html(self, filename):
        with open(filename,"w") as f:
            f.write(self.as_html())
