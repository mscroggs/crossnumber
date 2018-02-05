class NonexistentClue(BaseException):
    pass

class WrongLengthAnswer(BaseException):
    pass

class Crossnumber:
    def __init__(self, size):
        self.size = size
        self.across = []
        self.down = []

    def add_across(self,l,x,y):
        self.across.append((l,x,y))

    def add_down(self,l,x,y):
        self.down.append((l,x,y))

    def n(self, x, y):
        for i,j in self.starts.items():
            if x == i[0] and y == i[1]:
                return j

    def generate(self):
        st = []
        for l,x,y in self.across+self.down:
            if (x,y) not in st:
                st.append((x,y))
        self.starts = {(x,y):i+1 for i,(x,y) in enumerate(sorted(st))}
        self.grid = [[[] for j in range(self.size)] for i in range(self.size)]
        self.data = {}
        self.clues = {}
        for l,x,y in self.across:
            for i in range(l):
                self.grid[x][y+i].append(("a",self.n(x,y),i))
                self.data["a"+str(self.n(x,y))] = None
                self.clues["a"+str(self.n(x,y))] = l
        for l,x,y in self.down:
            for i in range(l):
                self.grid[x+i][y].append(("d",self.n(x,y),i))
                self.data["d"+str(self.n(x,y))] = None
                self.clues["d"+str(self.n(x,y))] = l

    def set_clue(self, clue, answer):
        if clue not in self.clues:
            raise NonexistentClue
        if len(str(answer)) != self.clues[clue]:
            raise WrongLengthAnswer
        self.data[clue] = answer

    def unset_clue(self, clue):
        if clue not in self.clues:
            raise NonexistentClue
        self.data[clue] = None

    def test(self):
        for row in self.grid:
            for cell in row:
                if len(cell) == 2:
                    a = self.data[cell[0][0]+str(cell[0][1])]
                    d = self.data[cell[1][0]+str(cell[1][1])]
                    if a is not None:
                        a = str(a)[cell[0][2]]
                    if d is not None:
                        d = str(d)[cell[1][2]]
                    if a is not None and d is not None and a != d:
                        return False
        for i in self.starts:
            cell = self.grid[i[0]][i[1]]
            for a in cell:
                b = self.data[a[0]+str(a[1])]
                if b is not None and str(b)[0]=="0":
                    return False
        return True

    def __str__(self):
        return self.__unicode__()

    def get(self, ls):
        if len(ls) == 0:
            return u"\u2588"
        for a,n,i in ls:
            if self.data[a+str(n)] is not None:
                return str(self.data[a+str(n)])[i]
        return "."

    def __unicode__(self):
        out = u"\u2588"*(self.size+2) + "\n"
        out += "\n".join([u"\u2588"+"".join([self.get(a) for a in row])+u"\u2588" for row in self.grid])
        out += "\n" + u"\u2588"*(self.size+2)
        return out
