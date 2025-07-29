#!/usr/bin/env python3

import re

COMSOL_ABS_TEMP_PAT = re.compile(r'\(\s*T\s*\/\s*1\s*\[\s*K\s*\]\s*\)')
COMSOL_TEMP_PAT = re.compile(r'\(\(T-0\[degC\]\)/1\[K\]\)')

class Variable:
    def __init__(self, s: str):
        self.var = s
    def __str__(self):
        return self.var

def is_variable(token):
    return isinstance(token, Variable)

class Operator:
    def __init__(self, s: str):
        self.op = s
    def __str__(self):
        return self.op

def is_operator(token):
    return isinstance(token, Operator)

class Paranthesis:
    def __init__(self, s: str):
        self.par = s
    def __str__(self):
        return self.par

def is_paranthesis(token):
    return isinstance(token, Paranthesis)


def tokenization(s: str):
    """
    :param s: A string with an arithmetic expression
    :return: A list of tokens, where each token is an instance of Variable, Operator or Paranthesis class
    :rtype: list
    """
    tokens = list()
    crt_token = ''


    # i is used like a pointer through list
    i = 0
    while i < len(s):
        # checks for '-' unary operator at the start of the string
        if i == 0 and s[i] == '-':
            crt_token += s[i]
            i += 1

        # checks for operators
        if s[i] == '*' or s[i] == '^' or s[i] == '+' or s[i] == '-' or s[i] == '/':
            if crt_token != '':
                if crt_token[0] == '-':
                    crt_token = '(' + crt_token + ')'
                tokens.append(Variable(crt_token))
            crt_token = ''
            tokens.append(Operator(s[i]))

        # checks for '('
        elif s[i] == '(':
            if crt_token != '':
                tokens.append(Variable(crt_token))
            crt_token = ''
            tokens.append(Paranthesis(s[i]))
            # checks for '-' unary operator after the paranthesis
            if s[i+1] == '-':
                crt_token += s[i + 1]
                i += 1
        # checks for ')'
        elif s[i] == ')':
            if crt_token != '':
                if crt_token[0] == '-':
                    crt_token = '(' + crt_token + ')'
                tokens.append(Variable(crt_token))
            crt_token = ''
            tokens.append(Paranthesis(s[i]))

        # skip white space (space and control characters)
        elif ord(s[i]) <= 0x20:
            pass

        # if not an operator, it is a variable (operand) token
        else:
            crt_token += s[i]

            if (i + 1) == len(s):
                tokens.append(Variable(crt_token))
        i += 1

    print([x.__str__() for x in tokens])
    return tokens


def precedence(operator):
    """
    :param operator: An Operator token
    :return: An integer representing the precedence (priority) of the operator
    """
    if is_operator(operator):
        if operator.op == '-' or operator.op == '+':
            return 1
        elif operator.op == '*' or operator.op == '/':
            return 2
        elif operator.op == '^':
            return 3
    return 0


def infix_to_postfix(token_list: list):
    """
    :param token_list: A list of tokens in infix order
    :return: A list of tokens in postfix order
    :rtype: list
    """
    token_list.insert(0, Paranthesis('('))
    token_list.append(Paranthesis(')'))
    size = len(token_list)
    token_stack = list()
    output = list()

    # i used like a pointer
    for i in range(size):
        # Variable token case
        if is_variable(token_list[i]):
            output.append(token_list[i])

        # Paranthesis token case
        elif is_paranthesis(token_list[i]):
            if token_list[i].par == '(':
                token_stack.append(token_list[i])
            else:
                while (is_paranthesis(token_stack[-1]) and token_stack[-1].par != '(') or is_operator(token_stack[-1]):
                    pop_element = token_stack.pop()
                    output.append(pop_element)
                token_stack.pop()

        # Operator token case
        else:
            if is_operator(token_stack[-1]) or is_paranthesis(token_stack[-1]):
                if is_operator(token_list[i]) and token_list[i].op == '^':
                    while precedence(token_list[i]) <= precedence(token_stack[-1]):
                        pop_element = token_stack.pop()
                        output.append(pop_element)
                else:
                    while precedence(token_list[i]) < precedence(token_stack[-1]):
                        pop_element = token_stack.pop()
                        output.append(pop_element)
                token_stack.append(token_list[i])

    while len(token_stack) != 0:
        pop_element = token_stack.pop()
        output.append(pop_element)
    return output


def infix_to_prefix(token_list):
    """
    :param token_list: a list of tokens in infix order
    :return: a list of tokens in prefix order
    :rtype: list
    
    This function transforms a list of tokens from infix order to prefix order.    
    """
    token_list = token_list[::-1]

    for i in range(len(token_list)):
        if is_paranthesis(token_list[i]):
            if token_list[i].par == '(':
                token_list[i].par = ')'
            else:
                token_list[i].par = '('

    prefix = infix_to_postfix(token_list)
    prefix = prefix[::-1]

    return prefix


class AST:
    """
        A class representing an Abstract Syntax Tree (AST) for arithmetic expressions.
    """
       
    def __init__(self, token_or_list):
        """
        :param token: A token that will be the root of the AST
        :type token: Variable, Operator, Paranthesis
        :return: None        
        """
        if isinstance(token_or_list, list):
            prefix = infix_to_prefix(token_or_list[:])
            ast = AST.getAST(prefix)
            # Copy ast's attributes to self
            self.__dict__ = ast.__dict__
        else:
            self.token = token_or_list
            if isinstance(token_or_list, Operator):
                if token_or_list.op == '^':
                    self.base = None
                    self.power = None
                else:
                    self.right = None
                    self.left = None

    
    def replace_token(self, match: str, replace: str):
        """

        :param match: the Variable token to be replaced
        :param replace: the Variable token that will replace the match
        :return: None

        Replace a Variable token with another Variable token, keeping the AST untoched.
        """
        # base case: replacing the matching
        if is_variable(self.token):
            if self.token.var == match:
                self.token = Variable(replace)

        # tail - recursion
        elif is_operator(self.token):
            if self.token.op == '^':
                self.base.replace_token(match, replace)
                self.power.replace_token(match, replace)
            else:
                self.right.replace_token(match, replace)
                self.left.replace_token(match, replace)


    @staticmethod
    def getAST(token_list) -> "AST":
        """
        :param token_list: A list of tokens in prefix order.
        :return: An AST object constructed from the token list.
        :rtype: An AST object.
        Construct an AST from a list of tokens in prefix order.
        If the list is empty, return None.
        """
        if len(token_list) == 0:
            return None

        token = token_list.pop(0)
        node = AST(token)

        if is_operator(token):
            if token.op == '^':
                node.base = AST.getAST(token_list)
                node.power = AST.getAST(token_list)
            else:
                node.left = AST.getAST(token_list)
                node.right = AST.getAST(token_list)

        return node
    

    def inorderAST(self):
        """
        :return: A list of tokens representing the in-order traversal of the AST
        :rtype: list
        \nReturns the in-order traversal of the AST as a list, adding parentheses where necessary to preserve operator precedence.
        
        """

        # base case of recursion
        if is_variable(self.token):
            return [self.token]

        # operator case
        elif is_operator(self.token):
            returnList = list()

            # '^' operation have separeted fields, for base and power
            if self.token.op == '^':
                base = self.base.inorderAST()
                power = self.power.inorderAST()

                # verify if base is variable or expression to add paranthesis
                if is_operator(self.base.token):
                    returnList.append(Paranthesis('('))
                    returnList += base
                    returnList.append(Paranthesis(')'))
                else:
                    returnList += base

                returnList.append(self.token)

                # verify if power is variable or expression to add paranthesis
                if is_operator(self.power.token):
                    returnList.append(Paranthesis('('))
                    returnList += power
                    returnList.append(Paranthesis(')'))
                else:
                    returnList += power

            # for other operations, we have left and right fields
            else:
                left = self.left.inorderAST()
                right = self.right.inorderAST()

                if is_operator(self.left.token):
                    if precedence(self.token) > precedence(self.left.token):
                        returnList.append(Paranthesis('('))
                        returnList += left
                        returnList.append(Paranthesis(')'))
                    else:
                        returnList += left
                else:
                    returnList += left

                returnList.append(self.token)

                # same idea, done for right field
                if is_operator(self.right.token):
                    if precedence(self.token) > precedence(self.right.token):
                        returnList.append(Paranthesis('('))
                        returnList += right
                        returnList.append(Paranthesis(')'))
                    else:
                        returnList += right
                else:
                    returnList += right

            return returnList

    def __str__(self):
        return ''.join(str(t) for t in self.inorderAST())
    
    def __repr__(self):
        attrs = ', '.join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

def generate_spice(ast: AST):
    """
    Generate a SPICE expression from an AST.

    :param ast: The AST to convert.
    :return: A SPICE expression string.
    """
    ast.replace_token('T_ABS', '(temp+273.15)')
    ast.replace_token('T', 'temp')
    expr = ast.inorderAST()
    spice_generated_0 = ''.join(str(t) for t in expr)
    spice_generated_1 = re.sub(r'\^','**', spice_generated_0)  # Replace '^' with '**' for Python syntax
    return spice_generated_1

def parse_comsol(expr: str):
    """
    Convert a COMSOL expression to an AST.

    :param expr: A COMSOL expression string.
    :return: An AST object representing the COMSOL expression.
    :rtype: AST
    """
    expr = re.sub(COMSOL_ABS_TEMP_PAT, 'T_ABS', expr)
    expr = re.sub(COMSOL_TEMP_PAT, 'T', expr)
    list_of_tokens = tokenization(expr)
    ast = AST(list_of_tokens)
    print(ast)
    return ast


# Example usage
def main():
    comsol_expression = "(104-0.287*(T/1[K])+0.321e-3*((T-0[degC])/1[K])^2)"
    ast = parse_comsol(comsol_expression)
    print("COMSOL Expression from AST:", ast)
    print("SPICE Expression from AST:", generate_spice(ast))

if __name__ == "__main__":
    main()