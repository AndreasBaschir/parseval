#!/usr/bin/env python3

import re
from asteval import Interpreter
from asteval.astutils import FROM_PY, FROM_MATH, FROM_NUMPY, NUMPY_RENAMES

###################################################################################

# GLOBAL VARIABLES

ALLOWED_LANGUAGES = ('matlab', 'python')

###################################################################################


class PyxEval:
    """
        A class that provides safe evaluation of user input arithmetic expressions in Python
    """

    # =======================================================================================

    # CONSTRUCTOR

    def __init__(self, expr: str, argnames: list, sym_table: dict = None, language: str = None, *options: dict):
        """

        :param expr: a string with the expression that needs to be evaluated
        :param argnames: a list of strings with all the factors names
        :param sym_table: a dictionary for constants
        :param language: string for specifying programming language used in expression
        :param options: to be implemented

        Constructor will parse given expression and make a list of variable names found in it.
        """
        self.argnames = argnames
        self.expr = expr
        self.sym_table = sym_table

        # We transform matlab syntax in python syntax
        if (language is None or language.lower() == 'matlab') and '^' in expr:
            self.expr = self.expr.replace('^', '**')
        elif language is not None and language not in ALLOWED_LANGUAGES:
            raise ValueError('Language is not in ALLOWED_LANGUAGES. Please write sintax only in '
                             + str(ALLOWED_LANGUAGES))

        self.interpreter = Interpreter()
        if sym_table:
            self.givenvar_symtable = len(sym_table.keys())
            # We add to interpreter's symbol table the custom dictionary
            for elem in sym_table.keys():
                self.interpreter.symtable[elem] = sym_table[elem]
        else:
            self.givenvar_symtable = 0

        # We make a list with the variables names used in expression to be used by xeval method
        self.expr_vars = set(
            sym for sym in re.findall('[a-zA-Z_][a-zA-Z0-9_]*', self.expr)
            if not any(sym in L for L in [FROM_PY, FROM_MATH, FROM_NUMPY, NUMPY_RENAMES])
        )
        # print('expr_vars:', self.expr_vars)

        self.my_parsed_expr = self.interpreter.parse(self.expr)  # We parse the expression only once

    # /CONSTRUCTOR

    # =======================================================================================

    # METHOD aeval

    def aeval(self, *args):
        """

        :param args: a list with values given for every factor
        :return: number if function executed correctly
        """
        if not len(args) == len(self.argnames):
            raise ValueError('Number of given arguments is not the same as the number of'
                             'factor names. Please give values for all factors when using PyxEval aeval function')
        # We check if received arguments are numbers
        index = 0
        for factor in args:
            self.interpreter.symtable[self.argnames[index]] = factor  # We update interpreter's symbol table
            index = index+1

        result = self.interpreter.run(self.my_parsed_expr)
        return result  # result should be a number if function executed correctly

    # /METHOD aeval

    # =======================================================================================

    # METHOD keval

    def keval(self, **kwargs):
        """

        :param kwargs: a dictionary with every factor and its given value
        :return: number if function executed correctly
        """
        if not len(kwargs) == len(self.argnames):
            raise ValueError('Number of given arguments is not the same as the number of'
                             'factor names. Please give values for all factors when using PyxEval keval function')

        # We check if the names of the factors are allowed
        for factor in self.argnames:
            if factor not in kwargs.keys():
                raise NameError('Factor {} does not exist. Please check given arguments names'.format(str(factor)))
            else:
                self.interpreter.symtable[factor] = kwargs[factor]  # We update interpreter's symbol table

        result = self.interpreter.run(self.my_parsed_expr)
        return result  # result should be a number if function executed correctly

    # /METHOD keval

    # =======================================================================================

    # METHOD __call__

    __call__ = aeval

    # /METHOD __call__

    # =======================================================================================

    # METHOD xeval

    def xeval(self, *args):
        """

        :param args: a list with at least the minimum number of values needed for evaluating expressions
                    can be given a dictionary for updating the symbol table as the last argument
        :return: number if executed correctly
        """
        #  We count how many variables we find in expression
        #  self.expr_vars is a list with variables and constants found in expression
        used_variables = 0
        for elem in self.expr_vars:
            used_variables = used_variables + int(elem in self.argnames)

        #  We check if the minimum parameters required are given
        if used_variables > (len(args) - int(type(args[len(args)-1]) == dict)):
            raise ValueError('Not enough values given for all the factor used in expression. Please give at least '
                             '{} arguments'.format(used_variables))

        if len(self.argnames) < (len(args) - int(type(args[len(args)-1]) == dict)):
            raise ValueError('Too many values given. Please give at most '
                             '{} arguments'.format(len(self.argnames)))

        index = 0
        for factor in args:
            #  The last argument given can be a dictionary meant for updating the symbol table
            if type(factor) is dict:
                self.update_symbol_table(**factor)
            else:
                self.interpreter.symtable[self.argnames[index]] = factor  # We update interpreter's symbol table
                index = index + 1
        for i in range(index, len(self.argnames)):
            self.interpreter.symtable[self.argnames[i]] = 0  # We update interpreter's symbol table
        result = self.interpreter.run(self.my_parsed_expr)
        return result  # result should be a number if function executed correctly

    # /METHOD xeval

    # =======================================================================================

    # METHOD update_symbol_table

    def update_symbol_table(self, **kwargs):
        """

        :param kwargs: a dictionary with a new symbol table
        """
        for elem in kwargs.keys():
            self.interpreter.symtable[elem] = kwargs[elem]  # We update interpreter's symbol table

    # /METHOD update_symbol_table

# /CLASS PyxEval

#############################################################################

