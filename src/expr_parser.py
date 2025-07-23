# !/usr/bin/env python3

from pyxeval import PyxEval
from parse_spice import parse_spice
from parse_comsol import parse_comsol 

class ExprParser:
    def __init__(self, expr: str, varnames: list, language: str = None):
        """
        Initializes the expression parser with an expression, variable names, and the expression language.

        :param expr: The expression to be parsed.
        :param varnames: A list of variable names used in the expression.
        :param language: The language of the expression, 'spice' or 'comsol'.
        """
        self.expr = expr
        self.varnames = varnames
        self.lang = language
        self.ast = None
        if language not in ['spice', 'comsol']:
            raise ValueError("Language must be either 'spice' or 'comsol'")
        else:
            if language == 'spice':
                self.ast = self.parse_spice()
            elif language == 'comsol':
                self.ast = self.parse_comsol()
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
        ast = parse_spice(self.expr)
        self.ast = ast
        return ast

    def parse_comsol(self):
        if self.lang == "spice":
            raise ValueError("parse_comsol() cannot be called on 'spice' expressions!")
        ast = parse_comsol(self.expr)
        self.ast = ast
        return ast

    def generate_spice(self):
        if self.lang == "spice":
            return self.expr
        spice_generated = ''.join(str(t) for t in self.ast.inorderAST())
        return spice_generated

    def generate_comsol(self):
        if self.lang == "comsol":
            return self.expr
        comsol_generated = ''.join(str(t) for t in self.ast.inorderAST())
        return comsol_generated

def main():

    # Example SPICE usage
    expr_parser_spice = ExprParser(expr="((-0.0036)*kappa*(temp+273.15)**2+4.6305*(temp+273.15)+x-405.38)*3210",
                             varnames=["temp","x"], language="spice")
    
    # ast from spice
    ast_0 = expr_parser_spice.parse_spice()
    
    # Evaluate the expression using aeval and keval
    # res_0 = expr_parser_spice.aeval(25, 100)
    # res_1 = expr_parser_spice.keval(temp=25, x=100)
    
    # Generate SPICE and COMSOL expressions
    generated_spice_0 = expr_parser_spice.generate_spice()
    generated_comsol_0 = expr_parser_spice.generate_comsol()

    # Print results
    print(f"AST: {ast_0}")
    # print(f"Result (aeval): {res_0}")
    # print(f"Result (keval): {res_1}")
    print(f"Generated SPICE: {generated_spice_0}")
    print(f"Generated COMSOL: {generated_comsol_0}")

    # ========================================================================================================

    # ((T-0[degC])/1[K])
    # (T/1[K])
    # Example COMSOL usage
    expr_parser_comsol = ExprParser(expr="((-0.0036)*kappa*T**2+4.6305*T+x-405.38)*3210", 
                                       varnames=["T","x"], language="comsol")
    
    # ast from comsol
    ast_1 = expr_parser_comsol.parse_comsol()
    
    # Evaluate the expression using aeval and keval
    # res_0 = expr_parser_comsol.aeval(25, 100, 50, 10)
    # res_1 = expr_parser_comsol.keval(A=25, B=100, C=50, D=10)
    
    # Generate SPICE and COMSOL expressions
    generated_spice_1 = expr_parser_comsol.generate_spice()
    generated_comsol_1 = expr_parser_comsol.generate_comsol()

    # Print results
    print(f"AST: {ast_1}")
    # print(f"Result (aeval): {res_0}")
    # print(f"Result (keval): {res_1}")
    print(f"Generated SPICE: {generated_spice_1}")
    print(f"Generated COMSOL: {generated_comsol_1}")

if __name__ == "__main__":
    main()