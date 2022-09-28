BINARYS = ['^', '/', '*', '-', '+']
UNARYS = ['ln', 'sin', 'cos', '-']
CONSTANT = "constant"
VARIABLE = "variable"
BINARY = "binary"
UNARY = "unary"

def get_priority(BINARY):
    return BINARYS.index(BINARY)

def is_binary(character):
    return BINARYS.count(character)

def find_binary(input):
    open_brackets, BINARY_index, highest_priority = 0, -1, -1
    for i in range(len(input)):
        ch = input[i]
        if(ch == '('):
            open_brackets += 1
        elif(ch == ')'):
            open_brackets -= 1
        else:
            if(open_brackets == 0 and is_binary(ch) and highest_priority < get_priority(ch)):
                BINARY_index, highest_priority = i, get_priority(ch)
    if(open_brackets):
        raise Exception("Not a valid Expression!")
    return BINARY_index


def parse(input:str):
    if(input.isdigit()):
        return CONSTANT,int(input)
    else:
        return VARIABLE,input

def copy(a,b):
    a.type = b.type
    a.value = b.value
    if(b.left != None):
        a.left = deep_copy(b.left)
    if(b.right != None):
        a.right = deep_copy(b.right)

def equal(a,b):
    if(a == None or b == None):
        return a==None and b == None
    return a.type == b.type and a.value == b.value and equal(a.left,b.left) and equal(a.right,b.right)

def calculate(a,b,binary):
    if(binary == '+'):
        return a+b
    elif(binary == '-'):
        return a-b
    elif(binary == '/'):
        return a/b
    elif(binary == '^'):
        return pow(a,b)
    else:
        return a*b

def deep_copy(expr):
    copy_expr = Expression(type=CONSTANT,value=0)
    copy_expr.type = expr.type
    copy_expr.value = expr.value
    if(expr.left != None):
        copy_expr.left = deep_copy(expr.left)
    if(expr.right != None):
        copy_expr.right = deep_copy(expr.right)
    return copy_expr


def fully_wrapped(input):
    o = 0
    for i in range(1,len(input)-1):
        if(input[i] == '('):
            o += 1
        elif(input[i] == ')'):
            o-=1
        if(o < 0):
            return False
    return o == 0 and input[0] == '(' and input[-1] == ')'

class Expression:
    def __init__(self,type=None,value=None,left=None,right=None,input:str=None):
        if(input):
            input = "".join(input.split())
            while(len(input) >= 2 and fully_wrapped(input)):
                input = input[1:-1]
            binary_index = find_binary(input)
            if(binary_index > 0 and binary_index < len(input)-1):
                self.left,self.right = Expression(input=input[:binary_index]), Expression(input=input[binary_index+1:])
                self.type, self.value = BINARY, input[binary_index]
            else:
                unary_found = False
                for unary in UNARYS:
                    if(len(input) > len(unary) and input.startswith(unary)):
                        unary_found = True
                        self.left = Expression(input=input[len(unary):])
                        self.right = None
                        self.type = UNARY
                        self.value = unary
                if(not unary_found):
                    self.type,self.value = parse(input)
                    self.left, self.right = None, None
        else:
            self.type = type
            self.value = value
            self.left = left
            self.right = right
        self.fix()

    def isOne(self):
        return (self.type == CONSTANT and self.value == 1)

    def isZero(self):
        return (self.type == CONSTANT and self.value == 0)

    def fix(self):
        if(self.type == BINARY):
            if(self.left.type == CONSTANT and self.right.type == CONSTANT):
                copy(self,Expression(type=CONSTANT,value=calculate(self.left.value,self.right.value,self.value)))
            if(self.value == '*'):
                if(self.left.isOne()):
                    copy(self,self.right)
                elif(self.right.isOne()):
                    copy(self,self.left)
                elif(self.left.isZero()):
                    copy(self, self.left)
                elif(self.right.isZero()):
                    copy(self.self.right)
            elif(self.value == '+'):
                if(self.left.isZero()):
                    copy(self,self.right)
                elif(self.right.isZero()):
                    copy(self,self.left)
            elif(self.value == '/'):
                if(self.left.isZero()):
                    copy(self,self.left)
                elif(self.right.isZero()):
                    raise Exception("Dividing by zero!")
                elif(self.right.isOne()):
                    copy(self,self.left)
                elif(equal(self.left,self.right)):
                    copy(self,Expression(type=CONSTANT,value=1))
            elif(self.value == '-'):
                if(self.right.isZero()):
                    copy(self,self.left)
                elif(self.left.isZero()):
                    copy(self,Expression(type=UNARY,value='-',left=deep_copy(self.right)))
                elif(equal(self.left,self.right)):
                    copy(self,Expression(type=CONSTANT,value=0))
                elif(self.right.type == UNARY and self.right.value == '-'):
                    copy(self,self.right.left)
            elif(self.value == '^'):
                if(self.right.isOne()):
                    copy(self,self.left)
                elif(self.right.isZero()):
                    copy(self,Expression(type=CONSTANT,value=1))
                elif(self.left.isOne()):
                    copy(self,Expression(type=CONSTANT,value=1))
                elif(self.left.isZero()):
                    copy(self,Expression(type=CONSTANT,value=0))
        elif(self.type == UNARY):
            if(self.value == '-'):
                if(self.left.type == CONSTANT):
                    copy(self, Expression(type=CONSTANT,value=-self.left.value))
                elif(self.left.type == UNARY and self.left.value == '-'):
                    copy(self,deep_copy(self.left.left))
            elif(self.value == 'ln'):
                if(self.left.isOne()):
                    copy(self,Expression(type=CONSTANT,value =0))


    def __str__(self):
        output = str(self.value)
        if(self.type == BINARY):
            output = f"({self.left.__str__()} {output} {self.right.__str__()})"
        elif(self.type == UNARY):
            output = f"{self.value}({self.left.__str__()})"
        return output

    def differentiate(self, variable):
        if(self.type == CONSTANT):
            return Expression(type=CONSTANT, value=0)
        elif(self.type == VARIABLE):
            if(variable == self.value):
                return Expression(type=CONSTANT,value=1)
            else:
                return Expression(type=self.type,value=self.value)
        elif(self.type == BINARY):
            if(self.value == '+'):
                return Expression(BINARY,'+',self.left.differentiate(variable),self.right.differentiate(variable))
            elif(self.value == '-'):
                return Expression(BINARY,'-',self.left.differentiate(variable),self.right.differentiate(variable))
            elif(self.value == '*'):
                return Expression(BINARY,'+',Expression(BINARY,'*',self.left.differentiate(variable),deep_copy(self.right)),Expression(BINARY,'*',deep_copy(self.left),self.right.differentiate(variable)))
            elif(self.value == '/'):
                return Expression(BINARY,'/',Expression(BINARY,'-',Expression(BINARY,'*',self.left.differentiate(variable),deep_copy(self.right)),Expression(BINARY,'*',deep_copy(self.left),self.right.differentiate(variable))), Expression(BINARY,'^',deep_copy(self.right),Expression(CONSTANT,2)))
            elif(self.value == '^'):
                return Expression(BINARY,'*',Expression(BINARY,'^',deep_copy(self.left),deep_copy(self.right)),Expression(BINARY,'+',Expression(BINARY,'/',Expression(BINARY,'*',deep_copy(self.right),self.left.differentiate(variable)), deep_copy(self.left)), Expression(BINARY,'*',self.right.differentiate(variable),Expression(UNARY,'ln',deep_copy(self.left)))))
        else:
            left = self.left.differentiate(variable)
            if(self.value == '-'):
                return Expression(UNARY,'-',left)
            elif(self.value == 'ln'):
                return Expression(BINARY,'*',left,Expression(BINARY,'/',Expression(CONSTANT,1),deep_copy(self.left)))
            elif(self.value == 'sin'):
                return Expression(BINARY,'*',left,Expression(UNARY,'cos',deep_copy(self.left)))
            elif(self.value == 'cos'):
                return Expression(UNARY,'-',Expression(BINARY,'*',left,Expression(UNARY,'sin',deep_copy(self.left))))
