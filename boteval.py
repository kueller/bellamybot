import shlex
import operator
from functools import reduce

# A sort of mini Lisp interpreter type that can be used.

class BotEval:

    def __init__(self):
        self.functions = {
            '+': self.add,
            '-': self.sub,
            '*': self.mult,
            '/': self.div,
            'if': self.if_compare,
            'cond': self.cond,
            '=': self.equals,
            'not': self.not_boolean,
            'is-mod': self.is_mod,
            'print': self.printf_irc
        }

        self.irc = None

    # Parsing and evaluating functions
    def compute(self, args):
        try:
            result = self.functions[args[0]](args[1:])
        except KeyError as k:
            raise KeyError("Function %s not found." % k)
        except TypeError as t:
            raise TypeError(t)
        return result
        
    # Based off Peter Norvig's 'lis.py' http://norvig.com/lispy.html
    def separate(self, tokens):
        if len(tokens) == 0:
            raise SyntaxError("Unexpected instruction end.")
        token = tokens.pop(0)
        if '(' == token:
            L = []
            try:
                while tokens[0] != ')':
                    L.append(self.separate(tokens))
                tokens.pop(0)
            except IndexError as i:
                raise SyntaxError("Mismatched parentheses.")
            return L
        elif ')' == token:
            raise SyntaxError("Mismatched parentheses.")
        else:
            try:
                return int(token)
            except ValueError:
                try:
                    return float(token)
                except ValueError:
                    return token

    def eval(self, irc, text):
        self.irc = irc
        text = text.replace('(', ' ( ').replace(')', ' ) ')
        try:
            tokens = shlex.split(text)
        except ValueError as v:
            irc.msg("Error: %s" % v)
            return

        try:
            full_inst = self.separate(tokens)
        except SyntaxError as s:
            irc.msg("Error: %s" % s)
            return

        try:
            result = self.compute(full_inst)
        except KeyError as k:
            irc.msg("Error: %s" % k)
            return
        except TypeError as t:
            irc.msg("Error: %s" % t)
            return
        except ValueError as v:
            irc.msg("Error: %s" % v)
            return

        irc.msg(result)        
        return
        
    # Basic arithmetic
    def add(self, args):
        for i, arg in enumerate(args):
            if isinstance(arg, list):
                args[i] = self.compute(arg)

        try:
            result = reduce(operator.add, args)
        except TypeError as t:
            raise TypeError(t)

        return result

    def sub(self, args):
        for i, arg in enumerate(args):
            if isinstance(arg, list):
                args[i] = self.compute(arg)

        try:
            result = reduce(operator.sub, args)
        except TypeError as t:
            raise TypeError(t)

        return result

    def mult(self, args):
        for i, arg in enumerate(args):
            if isinstance(arg, list):
                args[i] = self.compute(arg)

        try:
            result = reduce(operator.mul, args)
        except TypeError as t:
            raise TypeError(t)

        return result

    def div(self, args):
        for i, arg in enumerate(args):
            if isinstance(arg, list):
                args[i] = self.compute(arg)

        try:
            result = reduce(operator.__truediv__, args)
        except TypeError as t:
            raise TypeError(t)

        return result

    # Comparisons
    def if_compare(self, args):
        if len(args) != 3:
            raise ValueError("Invalid argument count in function \'if\'.")

        if isinstance(args[0], list):
            check = self.compute(args[0])

        if check:
            if isinstance(args[1], list):
                return self.compute(args[1])
            else:
                return args[1]
        else:
            if isinstance(args[2], list):
                return self.compute(args[2])
            else:
                return args[2]

    def cond(self, args):
        for arg in args:
            if len(arg) != 2:
                raise ValueError("Invalid argument count for condition.")

            if isinstance(arg[0], list):
                check = self.compute(arg[0])

            if check:
                if isinstance(arg[1], list):
                    return self.compute(arg[1])
                else:
                    return arg[1]
        return None

    def equals(self, args):
        for i, arg in enumerate(args):
            if isinstance(arg, list):
                args[i] = self.compute(arg)

        return reduce(operator.eq, args)

    def not_boolean(self, args):
        if len(args) == 0:
            return True
        if len(args) > 1:
            return False

        if isinstance(args[0], list):
            args[0] = self.compute(args[0])
        return args[0] is False

    def is_mod(self, args):
        if len(args) != 1:
            raise ValueError("Function \'is-mod\' can only check for one user at a time.")

        if isinstance(args[0], list):
            args[0] = self.compute(args[0])

        return args[0] in self.irc.modlist

    def printf_irc(self, args):
        for i, arg in enumerate(args):
            if isinstance(arg, list):
                args[i] = self.compute(arg)
            args[i] = str(args[i])

        return ' '.join(args)
