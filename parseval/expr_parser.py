#!/usr/bin/env python3

import re
import argparse
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
        if initial_lang.casefold() == 'spice':
            self.spice_expr = expr
            self.comsol_expr = None
            self.ast = self.parse_spice()
            self.evaluator = PyxEval(self.spice_expr, self.varnames, language='python')
        elif initial_lang.casefold() == 'comsol':
            self.spice_expr = None
            self.comsol_expr = expr
            self.ast = self.parse_comsol()
            to_be_eval_0 = "".join(str(t) for t in self.ast.inorderAST())
            to_be_eval = re.sub(r'\^','**', to_be_eval_0)  # Replace '^' with '**' for Python syntax
            self.evaluator = PyxEval(to_be_eval, self.varnames, language='python')
        else:
            raise ValueError("Language must be either 'spice' or 'comsol'")

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
    parser = argparse.ArgumentParser(
        description=(
            "Parse, evaluate, and convert SPICE/COMSOL expressions.\n"
            "COMSOL temperature 'T' must be in Kelvin, e.g. 25 degrees Celsius is 298.15 K.\n\n"
            "Examples:\n"
            "  python3 -m src.expr_parser \"(-0.0123*(temp+273.15)**2+1.2345*(temp+273.15)-456.78)*4321\" --varnames temp --lang spice --aeval 25\n"
            "  python3 -m src.expr_parser \"(33/(0.33+1.33e-3*((T-0[degC])/1[K])+1.33e-3*(T/1[K])^2))\" --varnames T --lang comsol --keval T=298.15\n"
            "  python3 -m src.expr_parser \"99.9-0.222*temp+0.444e-5*temp**2\" --varnames temp --lang spice --generate comsol\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("expr", help="The expression to parse and evaluate.")
    parser.add_argument(
        "--varnames", nargs="+", required=True,
        help="Variable names used in the expression (e.g. temp T)."
    )
    parser.add_argument(
        "--lang", choices=["spice", "comsol"], required=True,
        help="Expression language: 'spice' or 'comsol'."
    )
    parser.add_argument(
        "-a", "--aeval", nargs="+", type=float,
        help="Values for variables (positional, for aeval)."
    )
    parser.add_argument(
        "-k", "--keval", nargs="+",
        help="Keyword values for variables (format: var=val, for keval)."
    )
    parser.add_argument(
        "-g", "--generate", choices=["spice", "comsol"],
        help="Generate expression in target format."
    )

    args = parser.parse_args()

    expr_parser = ExprParser(expr=args.expr, varnames=args.varnames, initial_lang=args.lang)

    print(f"Parsed expression: {expr_parser.expr}")

    if args.aeval:
        result = expr_parser.aeval(*args.aeval)
        print(f"aeval result: {result}")

    if args.keval:
        kwargs = dict(kv.split("=") for kv in args.keval)
        # Convert values to float
        kwargs = {k: float(v) for k, v in kwargs.items()}
        result = expr_parser.keval(**kwargs)
        print(f"keval result: {result}")

    if args.generate == "spice":
        print("Generated SPICE:", expr_parser.generate_spice())
    elif args.generate == "comsol":
        print("Generated COMSOL:", expr_parser.generate_comsol())

if __name__ == "__main__":
    main()