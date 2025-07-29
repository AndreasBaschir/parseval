# !/usr/bin/env python3

import ast
import re
from .evaluators import PyxEval
from .parsers import parse_spice, parse_comsol, generate_spice, generate_comsol

class ExprParser:
    def __init__(self, expr: str, varnames: list, initial_lang: str = None):
        """
        Initializes the expression parser with an expression, variable names, and the expression language.

        :param expr: The expression to be parsed.
        :param varnames: A list of variable names used in the expression.
        :param language: The language of the expression, 'spice' or 'comsol'.
        """
        self.expr = expr
        self.varnames = varnames
        if not isinstance(varnames, list):
            raise TypeError("varnames must be a list of variable names")
        self.initial_expr_lang = initial_lang
        self.spice_expr = None
        self.comsol_expr = None
        self.ast = None
        if initial_lang not in ['spice', 'comsol']:
            raise ValueError("Language must be either 'spice' or 'comsol'")
        else:
            if initial_lang == 'spice':
                self.spice_expr = expr
                self.ast = self.parse_spice()
            elif initial_lang == 'comsol':
                self.comsol_expr = expr
                self.ast = self.parse_comsol()
                self.spice_expr = self.generate_spice()
        self.evaluator = PyxEval(self.spice_expr, self.varnames, language='python')

    def aeval(self, *args):
        """
        similar to pyxeval
        """
        ev = self.evaluator.aeval(*args)
        return ev

    def keval(self, **kwargs):
        """
        similar to pyxeval
        """
        ev = self.evaluator.keval(**kwargs)
        return ev

    def parse_spice(self):
        """
        Parses the SPICE expression into an AST.

        :return: The AST representation of the SPICE expression.
        :rtype: AST object
        """
        if self.initial_expr_lang == "comsol":
            raise ValueError("parse_spice() cannot be called on 'comsol' expressions!")
        ast = parse_spice(self.expr)
        self.ast = ast
        return ast

    def parse_comsol(self):
        """
        Parses the COMSOL expression into an AST.
        
        :return: The AST representation of the COMSOL expression.
        :rtype: AST object
        """
        if self.initial_expr_lang == "spice":
            raise ValueError("parse_comsol() cannot be called on 'spice' expressions!")
        ast = parse_comsol(self.expr)
        self.ast = ast
        return ast

    def generate_spice(self):
        """
        Generates a SPICE expression from the AST.
        
        :return: The SPICE expression as a string.
        :rtype: str
        """
        if self.initial_expr_lang == "spice":
            return self.expr
        spice_generated = generate_spice(self.ast)
        return spice_generated

    def generate_comsol(self):
        """
        Generates a COMSOL expression from the AST.

        :return: The COMSOL expression as a string.
        :rtype: str
        """
        if self.initial_expr_lang == "comsol":
            return self.expr
        comsol_generated = generate_comsol(self.ast)
        return comsol_generated

def main():

    # Example SPICE usage
    expr_parser_spice = ExprParser(expr="((-0.0036)*(temp+273.15)**2+4.6305*(temp+273.15)-405.38)*3210",
                             varnames=["temp"], initial_lang="spice")
    
    # Evaluate the expression using aeval and keval
    res_0 = expr_parser_spice.aeval(0)
    res_1 = expr_parser_spice.keval(temp=0)
    
    # Generate SPICE and COMSOL expressions
    generated_spice_0 = expr_parser_spice.generate_spice()
    generated_comsol_0 = expr_parser_spice.generate_comsol()

    # Print results
    print(f"Result (aeval): {res_0}")
    print(f"Result (keval): {res_1}")
    print(f"Generated SPICE: {generated_spice_0}")
    print(f"Generated COMSOL: {generated_comsol_0}")

    # ========================================================================================================

    # ((T-0[degC])/1[K])
    # (T/1[K])
    # Example COMSOL usage
    expr_parser_comsol = ExprParser(expr="(104-0.287*((T-0[degC])/1[K])+0.321e-3*((T-0[degC])/1[K])^2)", 
                                       varnames=["T"], initial_lang="comsol")
    
    # Evaluate the expression using aeval and keval
    res_0 = expr_parser_comsol.aeval(25)
    res_1 = expr_parser_comsol.keval(temp=25)
    
    # Generate SPICE and COMSOL expressions
    generated_spice_1 = expr_parser_comsol.generate_spice()
    generated_comsol_1 = expr_parser_comsol.generate_comsol()

    # Print results
    print(f"Result (aeval): {res_0}")
    print(f"Result (keval): {res_1}")
    print(f"Generated SPICE: {generated_spice_1}")
    print(f"Generated COMSOL: {generated_comsol_1}")

if __name__ == "__main__":
    main()