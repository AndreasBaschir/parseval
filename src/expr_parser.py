#!/usr/bin/env python3

import re
from .evaluators import PyxEval
from .parsers import parse_spice, parse_comsol, generate_spice, generate_comsol

COMSOL_ABS_TEMP_PAT = re.compile(r'\(\s*T\s*\/\s*1\s*\[\s*K\s*\]\s*\)')
COMSOL_TEMP_PAT = re.compile(r'\(\(T-0\[degC\]\)/1\[K\]\)')

class ExprParser:
    def __init__(self, expr: str, varnames: list, initial_lang: str = None):
        """
        Initializes the expression parser with an expression, variable names, and the expression language.

        :param expr: The expression to be parsed.
        :param varnames: A list of variable names used in the expression.
        :param language: The language of the expression, 'spice' or 'comsol'.
        """
        if not isinstance(varnames, list):
            raise TypeError("varnames must be a list of variable names")
        self.varnames = varnames
        self.expr = expr
        self.initial_expr_lang = initial_lang
        self.ast = None
        if initial_lang.lower() not in ['spice', 'comsol']:
            raise ValueError("Language must be either 'spice' or 'comsol'")
        else:
            if initial_lang == 'spice':
                self.spice_expr = expr
                self.comsol_expr = None
                self.ast = self.parse_spice()
                self.evaluator = PyxEval(self.spice_expr, self.varnames, language='python')
            elif initial_lang == 'comsol':
                self.spice_expr = None
                self.comsol_expr = expr
                self.ast = self.parse_comsol()
                to_be_eval_0 = "".join(str(t) for t in self.ast.inorderAST())
                to_be_eval = re.sub(r'\^','**', to_be_eval_0)  # Replace '^' with '**' for Python syntax
                print(f"Python expression to be evaluated: {to_be_eval}")
                self.evaluator = PyxEval(to_be_eval, self.varnames, language='python')

    def aeval(self, *args):
        """
        Evaluates the expression using the aeval method from PyxEval.

        :param args: Arguments to be passed to the aeval method.
        :return: The evaluated result.
        :rtype: float

        Example:
            Here's how you can use the aeval method:

            **SPICE example:**
            .. code-block:: python
                >>> from expr_parser import ExprParser
                >>> spice_expr = 81.5-0.155*temp+0.133e-3*temp**2
                >>> expr_parser = ExprParser(expr=spice_expr, varnames=["temp"], initial_lang="spice")
                >>> result = expr_parser.aeval(25) # Evaluating at temp = 25 degrees Celsius
                >>> print(result)
                77.708125

            **COMSOL example:**
            .. code-block:: python
                >>> from expr_parser import ExprParser
                >>> comsol_expr = (50/(0.03+1.56e-3*((T-0[degC])/1[K])+1.65e-6*(T/1[K])^2))
                >>> expr_parser = ExprParser(expr=comsol_expr, varnames=["T"], initial_lang="comsol")
                >>> result = expr_parser.aeval(298.15) # Evaluating at T = 298.15 degrees Kelvin (25 degrees Celsius)
                >>> print(result)
                231.83121698411585

        """
        ev = self.evaluator.aeval(*args)
        return ev

    def keval(self, **kwargs):
        """
        Evaluates the expression using the keval method from PyxEval.

        :param kwargs: Keyword arguments to be passed to the keval method.
        :return: The evaluated result.
        :rtype: float

        Example:
            Here's how you can use the keval method:

            **SPICE example:**
            .. code-block:: python
                >>> from expr_parser import ExprParser
                >>> spice_expr = "81.5-0.155*temp+0.133e-3*temp**2"
                >>> expr_parser = ExprParser(expr=spice_expr, varnames=["temp"], initial_lang="spice")
                >>> result = expr_parser.keval(temp=25) # Evaluating at temp = 25 degrees Celsius
                >>> print(result)
                77.708125

            **COMSOL example:**
            .. code-block:: python
                >>> from expr_parser import ExprParser
                >>> comsol_expr = "(50/(0.03+1.56e-3*((T-0[degC])/1[K])+1.65e-6*(T/1[K])^2))"
                >>> expr_parser = ExprParser(expr=comsol_expr, varnames=["T"], initial_lang="comsol")
                >>> result = expr_parser.keval(T=298.15) # Evaluating at T = 298.15 degrees Kelvin (25 degrees Celsius)
                >>> print(result)
                231.83121698411585

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
            return self.spice_expr
        spice_generated = generate_spice(self.ast)
        return spice_generated

    def generate_comsol(self):
        """
        Generates a COMSOL expression from the AST.

        :return: The COMSOL expression as a string.
        :rtype: str
        """
        if self.initial_expr_lang == "comsol":
            return self.comsol_expr
        comsol_generated = generate_comsol(self.ast)
        return comsol_generated

def main():

    # Example SPICE usage
    expr_parser_spice = ExprParser(expr="104-0.287*temp+0.321e-3*temp**2",
                             varnames=["temp"], initial_lang="spice")

    # Evaluate the SPICE expression
    res_0 = expr_parser_spice.aeval(25)
    print(f"Result (aeval): {res_0}")
    res_1 = expr_parser_spice.keval(temp=25)
    print(f"Result (keval): {res_1}")    

    # Generate SPICE and COMSOL expressions
    generated_spice_0 = expr_parser_spice.generate_spice()
    print(f"Generated SPICE: {generated_spice_0}")
    generated_comsol_0 = expr_parser_spice.generate_comsol()
    print(f"Generated COMSOL: {generated_comsol_0}")

    # Example COMSOL usage
    expr_parser_comsol = ExprParser(expr="(104-0.287*((T-0[degC])/1[K])+0.321e-3*((T-0[degC])/1[K])^2)", 
                                       varnames=['T'], initial_lang="comsol")
    
    # Evaluate the COMSOL expression
    res_0 = expr_parser_comsol.aeval(25+273.15)  # Convert 25 degrees Celsius to Kelvin
    print(f"Result (aeval): {res_0}")
    res_1 = expr_parser_comsol.keval(T=25+273.15)
    print(f"Result (keval): {res_1}")
    
    # Generate SPICE and COMSOL expressions
    generated_spice_1 = expr_parser_comsol.generate_spice()
    print(f"Generated SPICE: {generated_spice_1}")
    generated_comsol_1 = expr_parser_comsol.generate_comsol()
    print(f"Generated COMSOL: {generated_comsol_1}")

    
if __name__ == "__main__":
    main()