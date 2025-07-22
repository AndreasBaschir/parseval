# !/usr/bin/env python3

from pyxeval import PyxEval
import parse_spice, parse_comsol 
from abstract_syntax_tree import AST

class ExprParser:
    def __init__(self, expr: str, argnames: list, language: str = None):
        """
        Initializes the expression parser with an expression, argument names, and the expression language.
        
        :param expr: The expression to be parsed.
        :param argnames: A list of argument names used in the expression.
        :param language: The language of the expression, e.g., 'spice' or 'comsol'.
        """
        self.expr = expr
        self.argnames = argnames
        self.lang = language
        self.AST = None
        self.evaluator = None # to be implemented 

    def aeval(self, *args):
        """
        similar to pyxeval
        """
        pass

    def keval(self, **kwargs):
        """
        similar to pyxeval
        """
        pass

    def parse_spice(self):
        if self.lang == "comsol":
            raise ValueError("parse_spice() cannot be called on 'comsol' expressions!")
        self.AST = parse_spice(self.expr)
        return self.AST

    def parse_comsol(self):
        if self.lang == "spice":
            raise ValueError("parse_comsol() cannot be called on 'spice' expressions!")
        self.AST = parse_comsol(self.expr)
        return self.AST

    def generate_spice(self):
        if self.lang == "spice":
            return self.expr
        return self.AST.generate_spice()

    def generate_comsol(self):
        if self.lang == "comsol":
            return self.expr
        return self.AST.generate_comsol()

def main():

    # Example SPICE usage
    expr_parser_spice = ExprParser(expr="((-0.0036)*kappa*(temp+273.15)**2+4.6305*(temp+273.15)+x-405.38)*3210",
                             argnames=["temp","x"], language="spice")
    
    # ast from spice
    ast_0 = expr_parser_spice.parse_spice()
    
    # Evaluate the expression using aeval and keval
    res_0 = expr_parser_spice.aeval(25, 100)
    res_1 = expr_parser_spice.keval(temp=25, x=100)
    
    # Generate SPICE and COMSOL expressions
    generated_spice_0 = expr_parser_comsol.generate_spice()
    generated_comsol_0 = expr_parser_comsol.generate_comsol()

    # Print results
    print(f"AST: {ast_0}")
    print(f"Result (aeval): {res_0}")
    print(f"Result (keval): {res_1}")
    print(f"Generated SPICE: {generated_spice_0}")
    print(f"Generated COMSOL: {generated_comsol_0}")

    # ========================================================================================================

    # Example COMSOL usage
    expr_parser_comsol = ExprParser(expr="(671+1.04*((T-0[degC])/1[K])-1.17e-3*((T-0[degC])/1[K])^2)", 
                                       argnames=["T"], language="comsol")
    
    # ast from comsol
    ast_1 = expr_parser_comsol.parse_comsol()
    
    # Evaluate the expression using aeval and keval
    res_0 = expr_parser_comsol.aeval(A=25, B=100, C=50, D=10)
    res_1 = expr_parser_comsol.keval(A=25, B=100, C=50, D=10)
    
    # Generate SPICE and COMSOL expressions
    generated_spice_1 = expr_parser_comsol.generate_spice()
    generated_comsol_1 = expr_parser_comsol.generate_comsol()

    # Print results
    print(f"AST: {ast_1}")
    print(f"Result (aeval): {res_0}")
    print(f"Result (keval): {res_1}")
    print(f"Generated SPICE: {generated_spice_1}")
    print(f"Generated COMSOL: {generated_comsol_1}")

if __name__ == "__main__":
    main()