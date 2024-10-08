import os
from typing import Union, List, Optional

alphabet_chars = list("abcdefghijklmnopqrstuvwxyz") + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
numeric_chars = list("0123456789")
var_chars = alphabet_chars + numeric_chars
all_valid_chars = var_chars + ["(", ")", ".", "\\"]
valid_examples_fp = "./valid_examples.txt"
invalid_examples_fp = "./invalid_examples.txt"
extra_invalid_examples_fp = "./extra_invalid_examples.txt"
extra_valid_examples_fp = "./extra_valid_examples.txt"

def read_lines_from_txt(fp: [str, os.PathLike]) -> List[str]:
    """
    :param fp: File path of the .txt file.
    :return: The lines of the file path removing trailing whitespaces
    and newline characters.
    """
    lines = []
    with open(fp, 'r') as file: #we open the file and set our cursor to read mode
        for line in file.readlines():
            lines.append(line.strip()) #we append a list of strings that will need to be evaluated

    return lines


def is_valid_var_name(s: str) -> bool:
    """
    :param s: Candidate input variable name
    :return: True if the variable name starts with a character,
    and contains only characters and digits. Returns False otherwise.
    """
    if not s: #if empty, then false
        return False
    
    if s[0] not in alphabet_chars:
        return False #if the beginning does not start with an alphabetical number, then return false
    
    for c in s:
        if c not in all_valid_chars:
            return False #if the characters in string s are not part of the valid characters, return false

    return True


class Node:
    """
    Nodes in a parse tree
    Attributes:
        elem: a string (single token)
        children: a list of child nodes
    """
    def __init__(self, elem: str = None):
        self.elem = elem
        self.children = []

    def add_child_node(self, node: 'Node') -> None:
        """Add a child node to the current node"""
        self.children.append(node)



def parse_tokens(s_: str) -> Union[List[str], bool]:
    """
    Gets the final tokens for valid strings as a list of strings, only for valid syntax,
    where tokens are (no whitespace included)
    \\ values for lambdas
    valid variable names
    opening and closing parenthesis
    Note that dots are replaced with corresponding parenthesis
    :param s_: the input string
    :return: A List of tokens (strings) if a valid input, otherwise False
    """

    s = s_[:]  #  Don't modify the original input string
    tokens = []
    i = 0
    open_parens = 0

    while i < len(s):
        char = s[i]
        if char.isspace(): #we ignore whitespace
            i += 1
            continue
        
        if char not in all_valid_chars:
            print(f"Error: Invalid character '{char}' at index {i}")
            return False #if the character is not in the set of valid characters, return False
        
        if char.isalpha(): #if we find an alphabetic character, then it must be a variable
            var_name = char
            i+= 1
            while i <len(s) and s[i] in var_chars: #loop through variable to find the entire variable
                var_name += s[i]
                i += 1

            if is_valid_var_name(var_name): #check if the variable is valid
                tokens.append(var_name)
            else:
                print(f"Error: Invalid variable name '{var_name}' at index {i}")
                return False
            

        elif char == '(':
            tokens.append(char)
            open_parens += 1 #track number of open parantheses
            i += 1

            if i < len(s) and s[i] == ')': #Check for empty parantheses
                print(f"Error: Missing expression inside parentheses at index {i}")
                return False 
            
        elif char == ')':
            if open_parens == 0: #If open_parens == 0, then there are no more open parentheses to match the closing one
                print(f"Bracket ')' at index {i} is not matched with an opening bracket '('.")
                return False
            tokens.append(char)
            open_parens -= 1
            i += 1

            
        elif char == '\\':
            index_backslash = s.index(char)
            if i + 1 < len(s) and s[i + 1].isspace(): #if there is a space after a backslash, then it is wrong
                print(f"Error: Invalid space inserted after '\\' at index {i}")
                return False
            if i + 1 == len(s) or not s[i + 1].isalpha(): #If the variable after the backslash does not start with an alphabetic number, then its invalid
                print(f"Error: Backslash '\\' not followed by a valid variable name at index {i}")
                return False
            
            var_name = s[i + 1]
            i += 2  # Move past the backslash and the first letter of the variable
            while i < len(s) and s[i] in var_chars:
                var_name += s[i]
                i += 1

            if is_valid_var_name(var_name): #append both the variable and backslash if variable name is valid
                tokens.append('\\')
                tokens.append(var_name)
            else:
                print(f"Error: Invalid variable name after '\\' at index {i}")
                return False

            # After lambda abstraction, check if there is an expression following
            if i >= len(s) or (s[i] not in all_valid_chars and not s[i].isspace()):
                print(f"Error: Missing expression after lambda abstraction at index {index_backslash}")
                return False
            
        # Parse dot (.)
        elif char == '.':
            # Ensure dot follows a valid variable
            if len(tokens) == 0 or tokens[-1] not in var_chars or s[i-1] not in var_chars:
                print(f"Error: Must have a variable name before character '.' at index {i}")
                return False

            # When a dot is found, add an opening parenthesis to group following tokens
            tokens.append('(')
            i += 1
            # Ensure there is a valid expression after the dot
            if i >= len(s) or s[i] == ')':
                print(f"Error: Missing expression after dot at index {i}")
                return False

        else:
            print(f"Error: Invalid character '{char}' at index {i}")
            return False

    # Check for unmatched opening parentheses
    if open_parens > 0:
        print(f"Error: Bracket '(' at index {s.index('(')} is not matched with a closing bracket ')'")
        return False

    # After the entire token stream is parsed, close any open parentheses for dots
    open_parens = tokens.count('(')
    close_parens = tokens.count(')')
    if open_parens > close_parens:
        tokens += [')'] * (open_parens - close_parens)

    return tokens if tokens else False
        


def read_lines_from_txt_check_validity(fp: [str, os.PathLike]) -> None:
    """
    Reads each line from a .txt file, and then
    parses each string  to yield a tokenized list of strings for printing, joined by _ characters
    In the case of a non-valid line, the corresponding error message is printed (not necessarily within
    this function, but possibly within the parse_tokens function).
    :param fp: The file path of the lines to parse
    """
    lines = read_lines_from_txt(fp)
    valid_lines = []
    for l in lines:
        tokens = parse_tokens(l)
        if tokens:
            valid_lines.append(l)
            
            print(f"The tokenized string for input string {l} is {'_'.join(tokens)}")
    if len(valid_lines) == len(lines):
        print(f"All lines are valid")



def read_lines_from_txt_output_parse_tree(fp: [str, os.PathLike]) -> None:
    """
    Reads each line from a .txt file, and then
    parses each string to yield a tokenized output string, to be used in constructing a parse tree. The
    parse tree should call print_tree() to print its content to the console.
    In the case of a non-valid line, the corresponding error message is printed (not necessarily within
    this function, but possibly within the parse_tokens function).
    :param fp: The file path of the lines to parse
    """
    lines = read_lines_from_txt(fp)
    for l in lines:
        tokens = parse_tokens(l)
        if tokens:
            print("\n")
            parser = Parser(tokens)
            parse_tree = parser.parse()  # Parse the tokens
            print_tree(parse_tree)  # Print the resulting parse tree




class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        """Return the current token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        """Move to the next token"""
        if self.pos < len(self.tokens):
            self.pos += 1

    def expect(self, expected_value):
        """Ensure the current token matches the expected value and go to the next token"""
        token = self.current_token()
        if token is None or token != expected_value:
            raise SyntaxError(f"Expected {expected_value}, found {token}")
        self.advance()

    def parse_expr(self):
        """
        Parses an expression, which can be a sequence of terms representing function application
        Returns a Node object representing the parsed expression.
        """
        left = self.parse_term()

        while True:
            token = self.current_token()
            if token is None or token in [')']:
                break  # Stop parsing if end of expression is reached
            # Parse the next term
            right = self.parse_term()
            # Create an application node
            app_node = Node('application function')
            app_node.add_child_node(left)
            app_node.add_child_node(right)
            left = app_node  # The new left is the application node

        return left

    def parse_term(self):
        """
        Parses a specific term, which can be a variable, labmda expression, or parentheses
        Retunrs a call to the correct non terminal function to parse
        """
        token = self.current_token()
        if token is None:
            raise SyntaxError("Unexpected end of input")
        if token.isalpha():
            return self.parse_var()
        elif token == '\\':
            return self.parse_lambda_expr()
        elif token == '(':
            return self.parse_paren_expr()
        else:
            raise SyntaxError(f"Unexpected token: {token}")

    def parse_var(self) -> Node:
        """
        Parses a variable
        Returns a Node object representing the variable term
        """

        token = self.current_token()
        if token and token.isalpha():
            var_node = Node(token)  # Create a node for the variable
            self.advance()
            return var_node
        else:
            raise SyntaxError(f"Expected variable, found {token}")

    def parse_paren_expr(self) -> Node:
        """
        Parses an expression term
        Returns a Node object representing the expressions parent node
        """
        self.expect('(')
        left_paren_node = Node('(')  # Node for '('
        expr = self.parse_expr()
        self.expect(')')
        right_paren_node = Node(')')  # Node for ')'
        paren_node = Node('parens')
        paren_node.add_child_node(left_paren_node)
        paren_node.add_child_node(expr)
        paren_node.add_child_node(right_paren_node)

        return paren_node


    def parse_lambda_expr(self) -> Node:
        """
        Parses a lambda term
        Returns a Node object representing the whole lambda expression
        """
        self.expect('\\')
        backslash_node = Node('\\')  # Node for '\'
        var_node = self.parse_var()
        
        expr_node = self.parse_expr()
        lambda_node = Node('lambda')
        lambda_node.add_child_node(backslash_node)
        lambda_node.add_child_node(var_node)
        lambda_node.add_child_node(expr_node)

        return lambda_node


    def parse(self) -> Node:
        return self.parse_expr()


def reconstruct_expr(node: Node) -> str:
    """
        Recursively builds the parse tree starting at the root and going down
        Returns string representation of the parse tree
        """
    if not node.children:
        return node.elem
    elif node.elem == 'app':
        return '_'.join([reconstruct_expr(child) for child in node.children])
    elif node.elem == 'lambda':
        # Children: ['\\', var_node, expr_node]
        var_expr = reconstruct_expr(node.children[1])
        expr_expr = reconstruct_expr(node.children[2])
        return '\\_' + var_expr + '_' + expr_expr
    elif node.elem == 'parens':
        # Children: ['(', expr_node, ')']
        expr_expr = reconstruct_expr(node.children[1])
        return '(_' + expr_expr + '_)'
    else:
        # For nodes like '\\', '(', ')', variables
        return '_'.join([reconstruct_expr(child) for child in node.children]) if node.children else node.elem

    

def print_tree(node: Node, level: int = 0) -> None:
    """
    Recursively prints the parse tree with indentation to reflect structure.
    :param node: A Node object
    :param level: the current tree level 
    """
    indent = "----" * level
    expr = reconstruct_expr(node)
    print(f"{indent}{expr}")  # Print the current node with indentation

    for child in node.children:
        print_tree(child, level + 1)  # Recursively print each child with increased indentation




if __name__ == "__main__":

    print("\n\nChecking valid examples...")
    read_lines_from_txt_check_validity(valid_examples_fp)
    print("Checking extra valid examples...")
    read_lines_from_txt_check_validity(extra_valid_examples_fp)

    read_lines_from_txt_output_parse_tree(extra_valid_examples_fp)

    read_lines_from_txt_output_parse_tree(valid_examples_fp)

    print("Checking invalid examples...")
    read_lines_from_txt_check_validity(invalid_examples_fp)
    print("Checking extra invalid examples...")
    read_lines_from_txt_check_validity(extra_invalid_examples_fp)




