import sys

sys.setrecursionlimit(10_000)

class LispError(Exception):
    """
    A type of exception to be raised if there is an error with a Lisp
    program.
    """
    pass


class LispSyntaxError(LispError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """
    pass


class LispNameError(LispError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """
    pass


class LispEvaluationError(LispError):
    """
    Exception to be raised if there is an error during evaluation other than a
    LispNameError.
    """
    pass


# Tokenization and Parsing

def number_or_symbol(x):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Lisp
                      expression
    """
    res = []
    i = 0
    while i < len(source):
        if source[i] == "(":
            res.append("(")
            i += 1
        elif source[i] == ")":
            res.append(")")
            i += 1
        elif source[i] == "#":
            while i < len(source) and source[i] != "\n":
                i += 1
        else:
            start = i
            end = i
            while end < len(source) and (source[end] != " " and source[end] != ")" and source[end] != "(" and source[end] != "\n"):
                if source[end] == "#":
                    while end < len(source) and source[end] != "\n":
                        end += 1
                    break
                end += 1
            if i != end:
                res.append(source[start:end])
                i = end
            else:
                i += 1
    return res


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    if tokens[0] == ")" or tokens[-1] == "(" or tokens[0] == ":=":
        raise LispSyntaxError

    if len(tokens) == 1:
        if tokens[0] in ["(", ")"]:
            raise LispSyntaxError
        else:
            return number_or_symbol(tokens[0])

    elif len(tokens) == 3:
        if tokens[0] == "(" and tokens[2] == ")":
            return [tokens[1]]    
    
    paren_stack = []
    parsed = []
    for i in range(1, len(tokens) - 1):
        if tokens[i] == "(":
            paren_stack.append(i)
        elif tokens[i] == ")":
            if len(paren_stack) == 0:
                raise LispSyntaxError
            elif len(paren_stack) == 1:
                beg_idx = paren_stack.pop()
                parsed.append(parse(tokens[beg_idx : i+1]))
            else:
                paren_stack.pop()
        elif len(paren_stack) == 0:
            parsed.append(number_or_symbol(tokens[i]))

    if len(paren_stack) != 0: 
        raise LispSyntaxError
    return parsed


# Built-in Functions

def multiply(args):
    res = 1
    for i in range(len(args)):
        res *= args[i]
    return res

def divide(args):
    res = args[0]
    for i in range(1, len(args)):
        res /= args[i]
    return res

def equal(args):
    base = args[0]
    for i in range(1, len(args)):
        if args[i] != base:
            return False
    return True

def decreasing(args):
    for i in range(len(args) - 1):
        if args[i] <= args[i+1]:
            return False
    return True

def nonincreasing(args):
    for i in range(len(args) - 1):
        if args[i] < args[i+1]:
            return False
    return True

def increasing(args):
    for i in range(len(args) - 1):
        if args[i] >= args[i+1]:
            return False
    return True

def nondecreasing(args):
    for i in range(len(args) - 1):
        if args[i] > args[i+1]:
            return False
    return True

def flip(args):
    if len(args) != 1:
        raise LispEvaluationError
    return not args[0]

def head(args):
    if type(args) != Pair or len(args) != 2:
        raise LispEvaluationError
    return args[0]

def pair_assign(args):
    if len(args) != 2:
        raise LispEvaluationError
    return Pair(args[0], args[1])

def head(args):
    if len(args) != 1 or type(args[0]) != Pair:
        raise LispEvaluationError
    return args[0].head

def tail(args):
    if len(args) != 1 or type(args[0]) != Pair:
        raise LispEvaluationError
    return args[0].tail

def create_list(args):
    if len(args) == 0:
        return None
    return Pair(args[0], create_list(args[1:]))

def is_linked_list(args):
    if args == None:
        return True
    if type(args) == Pair:
        return is_linked_list(args.tail) 
    return False

def length(args):
    if args != None and type(args) != Pair:
        raise LispEvaluationError
    elif args == None:
        return 0
    return 1 + length(args.tail)

def retrieve_n(linked_list, idx):
    if not type(linked_list) == Pair and idx >= length(linked_list):
        raise LispEvaluationError
    if idx == 0:
        return linked_list.head
    if type(linked_list) == Pair and is_linked_list(linked_list) == False:
        raise LispEvaluationError
    
    return retrieve_n(linked_list.tail, idx-1)

def merge(first, second):
    if first == None:
        return second
    else:
        return Pair(first.head, merge(first.tail, second))

def duplicate(args):
    if args == None:
        return None
    if type(args) != Pair:
        raise LispEvaluationError
    return Pair(args.head, duplicate(args.tail))

def concat(args):
    if args == None:
        return None
    if len(args) == 1:
        return args[0]
    if len(args) == 0:
        return None
    joined_list = merge(duplicate(args[0]), duplicate(args[1]))
    try:
        return concat([joined_list] + args[2:])
    except:
        return joined_list

def map(function, lis):
    res = None
    for i in range(length(lis)):
        res = Pair(evaluate([function, retrieve_n(lis, length(lis) - i - 1)]), res)
    return res

def filter(function, lis):
    if type(function) != Function and function not in Lisp_builtins:
        raise LispEvaluationError

    if type(lis) != Pair and lis != None:
        raise LispEvaluationError
    
    if lis == None:
        return None

    if func_eval(function, [lis.head]) == True:
        return Pair(lis.head, filter(function, lis.tail))
    return filter(function, lis.tail)

def reduce(function, lis, base):
    temp = base
    for i in range(length(lis)):
        temp = evaluate([function, temp, retrieve_n(lis, i)])
    return temp

def begin(args):
    return args[-1]

def factorial(args):
    if args == 1:
        return 1
    return args * factorial(args - 1)

Lisp_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": multiply,
    "/": divide,
    "=?": equal,
    ">": decreasing,
    ">=": nonincreasing,
    "<": increasing,
    "<=": nondecreasing,
    "@t": True,
    "@f": False,
    "not": flip,
    "pair": pair_assign,
    "head": head,
    "tail": tail,
    "nil": None,
    "list": create_list,
    "list?": lambda args: is_linked_list(args[0]),
    "length": lambda args: length(args[0]),
    "nth": lambda args: retrieve_n(args[0], args[1]),
    "concat": concat,
    "map": lambda args: map(args[0], args[1]),
    "filter": lambda args: filter(args[0], args[1]),
    "reduce": lambda args: reduce(args[0], args[1], args[2]),
    "begin": begin,
    "factorial": factorial
}

# Evaluation 

class Environment:
    def __init__(self, parent = None):
        self.var_bind = {}
        self.parent = parent
    
    def retrieve(self, var):
        if var in self.var_bind:
            return self.var_bind[var]
        elif type(self.parent) == dict and var in self.parent:
            return self.parent[var]
        elif var in Lisp_builtins:
            return Lisp_builtins[var]
        elif type(self.parent) == Environment:
            return self.parent.retrieve(var)
        else:
            raise LispNameError
    def delete(self, name):
        if name in self.var_bind:
            temp = self.var_bind[name]
            del self.var_bind[name]
            return temp
        raise LispNameError

class Function:
    def __init__(self, body, params, env):
        self.body = body 
        self.params = params
        self.env = env

class Pair:
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

def evaluate_file(file, env = Environment()):
    with open(file, 'r') as f:
        file_txt = f.read()
        tokenized = tokenize(file_txt)
        parsed = parse(tokenized)
        return evaluate(parsed, env)

def func_eval(function_obj, function_args):    
    func_env = Environment(function_obj.env)
    for i in range(len(function_args)):
        func_env.var_bind[function_obj.params[i]] = function_args[i]
    return evaluate(function_obj.body, func_env)



def evaluate(tree, env = Environment()):
    """
    Evaluate the given syntax tree according to the rules of the Lisp
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if type(tree) in [int, float, Function, Pair]:
        return tree
    
    elif type(tree) == list:
        if tree == [] or type(tree[0]) == int:
            raise LispEvaluationError
 
        if tree[0] == "function":
            return Function(tree[2], tree[1], env)
        
        elif tree[0] == ":=":
            if type(tree[1]) == list:
                env.var_bind[tree[1][0]] = Function(tree[2], tree[1][1:], env)
                return env.var_bind[tree[1][0]]
            env.var_bind[tree[1]] = evaluate(tree[2], env)
            return env.var_bind[tree[1]]
        
        elif tree[0] == "if":
            if evaluate(tree[1], env) == True:
                return evaluate(tree[2], env)
            return evaluate(tree[3], env)
        
        elif tree[0] == "and":
            for i in range(1, len(tree)):
                if evaluate(tree[i], env) == False:
                    return False
            return True

        elif tree[0] == "or":
            for i in range(1, len(tree)):
                if evaluate(tree[i], env) == True:
                    return True
            return False
        elif tree[0] == "del":
            return env.delete(tree[1])

        elif tree[0] == 'let':
            func_env = Environment(env)
            for i in tree[1]:
                func_env.var_bind[i[0]] = evaluate(i[1], env)
            return evaluate(tree[2], func_env)

        elif tree[0] == 'set!':
            current_env = env
            while True:
                if tree[1] in current_env.var_bind:
                    current_env.var_bind[tree[1]] = evaluate(tree[2], env)
                    return current_env.var_bind[tree[1]]
                if current_env.parent == None:
                    raise LispNameError
                current_env = current_env.parent

        else:
            func_obj = evaluate(tree[0], env)
            function_args = []
            for i in range(1, len(tree)):
                    function_args.append(evaluate(tree[i], env))
            if type(func_obj) == Function:
                if len(function_args) == len(func_obj.params):
                    return func_eval(func_obj, function_args)
                raise LispEvaluationError
            return func_obj(function_args)
    elif callable(tree) == True or tree == None:
        return tree
    else:
        return env.retrieve(tree)
        


def REPL():
    while 1:
        user_input = input("in> ")
        if user_input == "EXIT":
            break
        try:
            print('     out> ' + str(evaluate(parse(tokenize(user_input)), Environment())) + '\n')
        except:
            print("Invalid Expression\n")


def result_and_env(tree, env = None):
    if env == None: 
        env = Environment()
    result = evaluate(tree, env)
    return result, env


if __name__ == "__main__":
    REPL()

