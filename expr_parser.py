from pyxeval import PyxEval
import re

class ExprParser:
    def __init__(self, expr: str, argnames: list, sym_table: dict = None, language: str = None):
        """
        :param expr: a string with the expression that needs to be evaluated
        :param argnames: a list of strings with all the factors names
        :param sym_table: a dictionary for constants
        :param language: string for specifying programming language used in expression
        """
        self.expr = expr
        self.argnames = argnames 
        self.symbol_table = sym_table
        self.language = language
        self.evaluator = PyxEval(expr, self.argnames, self.symbol_table, self.language)

    def aeval(self, *args):
        return self.evaluator.aeval(*args)

    def keval(self, **kwargs):
        return self.evaluator.keval(**kwargs)

    def parse_spice(self):
        pass

    def parse_comsol(self):
        pass

    def generate_spice(self):
        pass

    def generate_comsol(self):
        pass

def main():
    # Example usage of ExprParser
    COMSOL_ABS_TEMP_PAT = re.compile(r'\(\s*T\s*\/\s*1\s*\[\s*K\s*\]\s*\)')
    COMSOL_TEMP_PAT = re.compile(r'\(\(T-0\[degC\]\)/1\[K\]\)')
    
    spice_expr_example_0 = "50/(0.03+1.56e-3*(temp+273.15)+1.65e-6*(temp+273.15)**2)"
    comsol_expr_example_0 = "(50/(0.03+1.56e-3*(T/1[K])+1.65e-6*(T/1[K])^2))"

    comsol_expr_example_0 = re.sub(COMSOL_ABS_TEMP_PAT, 'T', comsol_expr_example_0)
    comsol_expr_example_0 = re.sub(COMSOL_TEMP_PAT, 't', comsol_expr_example_0)

    if '^' in comsol_expr_example_0:
        comsol_expr_example_0 = comsol_expr_example_0.replace('^', '**')
    print(f"COMSOL Expression: {comsol_expr_example_0}")
    parser = ExprParser(expr=comsol_expr_example_0, argnames=['T'])
    result = parser.aeval(273.15) 
    print(f"COMSOL Result: {result}")
    print("===============================\n")

    spice_expr_example_1 = "(671+1.04*temp-1.17e-3*temp**2)*2320"
    comsol_expr_example_1 = "(671+1.04*((T-0[degC])/1[K])-1.17e-3*((T-0[degC])/1[K])^2)"

    comsol_expr_example_1 = re.sub(COMSOL_ABS_TEMP_PAT, 'T', comsol_expr_example_1)
    comsol_expr_example_1 = re.sub(COMSOL_TEMP_PAT, 't', comsol_expr_example_1)

    if '^' in comsol_expr_example_1:
        comsol_expr_example_1 = comsol_expr_example_1.replace('^', '**')
    print(f"COMSOL Expression: {comsol_expr_example_1}")
    parser = ExprParser(expr=comsol_expr_example_1, argnames=['t'])
    result = parser.aeval(0)
    print(f"COMSOL Result: {result}")


if __name__ == "__main__":
    main()