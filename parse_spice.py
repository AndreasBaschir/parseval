import re


###################################################################################

# GLOBAL VARIABLES

SPICE_ABS_TEMP_PAT = re.compile(r' *\(? *temp *\+ *273.15 *\)? *')

###################################################################################


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

###################################################################################

# CLASS AST

class AST:
    """
    A class representing an Abstract Syntax Tree (AST) for arithmetic expressions.
    """

    # =======================================================================================

    # CONSTRUCTOR
    
    def __init__(self, token):
        self.token = token
        if isinstance(token, Operator):
            if token.op == '^':
                self.base = None
                self.power = None
            else:
                self.right = None
                self.left = None

    # /CONSTRUCTOR

    # =======================================================================================

    # METHOD inorderAST

    def inorderAST(self):
        """
        Returns the in-order traversal of the AST as a list, adding parentheses where necessary to preserve operator precedence.
        """
        if is_variable(self.token):
            return [self.token]
        elif is_operator(self.token):
            returnList = list()
            if self.token.op == '^':
                base = self.base.inorderAST()
                power = self.power.inorderAST()
                if is_operator(self.base.token):
                    returnList.append(Paranthesis('('))
                    returnList += base
                    returnList.append(Paranthesis(')'))
                else:
                    returnList += base
                returnList.append(self.token)
                if is_operator(self.power.token):
                    returnList.append(Paranthesis('('))
                    returnList += power
                    returnList.append(Paranthesis(')'))
                else:
                    returnList += power
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

    # /METHOD inorderAST

    # =======================================================================================

    # METHOD replace_token

    def replace_token(self, match, replace):
        """
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

    # /METHOD replace_token

    # =======================================================================================

    # METHOD getAST

    # Construction of AST using the prefix order of string. It is easy this way, AST is placing elements from left to right
    @staticmethod
    def getAST(token_list):
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

    # /METHOD getAST

# /CLASS AST

#############################################################################

def tokenization(s: str):
    """
    Tokenize an arithmetic expression string into a list of Variable, Operator, or Paranthesis tokens.
    """
    tokens = list()
    crt_token = ''
    global variable_list 
    variable_list = list()
    # i is used like a pointer through list
    i = 0
    while i < len(s):
        # checks for '-' unary operator at the start of the string
        if i == 0 and s[i] == '-':
            crt_token += s[i]
            i += 1
        # checks for '*'
        elif s[i] == '*':
            if crt_token != '':
                variable_list.append(crt_token)
                if crt_token[0] == '-':
                    crt_token = '(' + crt_token + ')'
                tokens.append(Variable(crt_token))
            crt_token = ''
            # checks for '**' 
            if i + 1 < len(s) and s[i + 1] == '*':
                tokens.append(Operator('^'))
                i += 1
            else:
                tokens.append(Operator(s[i]))
        # checks for '+' or '-' or '/'
        elif s[i] == '+' or s[i] == '-' or s[i] == '/':
            if crt_token != '':
                variable_list.append(crt_token)
                if crt_token[0] == '-':
                    crt_token = '(' + crt_token + ')'
                tokens.append(Variable(crt_token))
            crt_token = ''
            tokens.append(Operator(s[i]))
        # checks for '(' 
        elif s[i] == '(':
            if crt_token != '':
                tokens.append(Variable(crt_token))
                variable_list.append(crt_token)
            crt_token = ''
            tokens.append(Paranthesis(s[i]))
            # checks for '-' unary operator after the paranthesis
            if s[i+1] == '-':
                crt_token += s[i + 1]
                i += 1
        # checks for ')'
        elif s[i] == ')':
            if crt_token != '':
                variable_list.append(crt_token)
                if crt_token[0] == '-':
                    crt_token = '(' + crt_token + ')'
                tokens.append(Variable(crt_token))
            crt_token = ''
            tokens.append(Paranthesis(s[i]))
        # eliminates whitespace and newline characters
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
    Return the precedence of an operator token.
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
    Transform a list of tokens in infix order to postfix order.
    """
    token_list.insert(0, Paranthesis('('))
    token_list.append(Paranthesis(')'))
    size = len(token_list)
    token_stack = list()
    output = list()
    for i in range(size):
        if is_variable(token_list[i]):
            output.append(token_list[i])
        elif is_paranthesis(token_list[i]):
            if token_list[i].par == '(': 
                token_stack.append(token_list[i])
            else:
                while (is_paranthesis(token_stack[-1]) and token_stack[-1].par != '(') or is_operator(token_stack[-1]):
                    pop_element = token_stack.pop()
                    output.append(pop_element)
                token_stack.pop()
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
    Compute the prefix form of a token list.
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

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def spice_to_comsol(s: str, var_list: list = None):
    """
    Convert a SPICE expression to a COMSOL expression.
    Replaces all occurrences of temp+273.15 with (T/1[K]) and temp with ((T-0[degC])/1[K]).
    Handles operator precedence and parentheses using an AST.
    """
    sa = SPICE_ABS_TEMP_PAT.sub('tempa', s)
    listOfTokens = tokenization(sa)
    prefix = infix_to_prefix(listOfTokens)
    ast = AST.getAST(prefix)
    ast.replace_token('tempa', '(T/1[K])')
    ast.replace_token('temp', '((T-0[degC])/1[K])')
    comsolList = ast.inorderAST()
    comsolString = ''.join(str(el) for el in comsolList)
    if var_list is not None:
        var_list.clear()
        var_list.extend(list(set(variable_list)))  # Remove duplicates from variable list
        var_list[:] = [v for v in var_list if not is_number(v)]
    return comsolString

def main():
    # Example usage
    vars = []
    spice_expression = "(-0.0036*(temp+273.15)**2+4.6305*(temp+273.15)-405.38)*3210"
    comsol_expression = spice_to_comsol(spice_expression, var_list=vars)
    print("COMSOL Expression:", comsol_expression)
    print("Variables:", vars)
if __name__ == "__main__":
    main()