class TokenType:
    LBRACE = 'LBRACE'  # '{'
    RBRACE = 'RBRACE'  # '}'
    COMMA = 'COMMA'  # ','
    COLON = 'COLON'  # ':'
    STRING = 'STRING'  # 
    NUMBER = 'NUMBER'  # 
    BOOL = 'BOOL'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    DIV = 'DIVIDE'
    MULT = 'MULT'
    NULL = 'NULL'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    EOF = 'EOF'  # End of input

class Token:
    def __init__(self, datatype, content=None):
        self.datatype = datatype
        self.content = content

def __repr__(self):
    return f"<{self.datatype}, {self.content}>"

class Tree_Node:
    def __init__(self, content='', depth=0):
        self.children = []
        self.content = content
        self.depth = depth

    def out(self):
        result = '    '* self.depth + self.content+'\n'
        for child in self.children:
            result+=child.out()
        return result
    
class Parse_Tree:
    def __init__(self):
        self.parse_tree = ''
        self.first = True
        self.root = Tree_Node()
        self.order = []
        self.curr_depth = 0
                
    def add_node(self, node_str, depth):

        if self.first:
            self.root = Tree_Node(node_str)
            self.order.append(self.root)
            self.first=False
        else:
            node = Tree_Node(node_str, depth)
            if node_str in ['dict', 'pair', 'value', 'list'] and depth>self.curr_depth:
                self.curr_depth = depth
                self.order[0].children.append(node)
                self.order.insert(0, node)
            elif depth<self.curr_depth:
                self.curr_depth = depth
                if len(self.order)>1:
                        self.order.remove(self.order[0])
                self.order[0].children.append(node)
            elif depth>self.curr_depth:
                self.curr_depth = depth
                self.order[0].children.append(node)
            else:
                self.order[0].children.append(node)
                
        self.parse_tree = self.root.out()

    def print_tree(self):
        print(self.root.out())
    

class Parser:
    def __init__(self, input_files):
        self.input_files = input_files
        self.error_list = ['ERROR STACK:']
        self.parse_tree = Parse_Tree()
        self.indent = '    '
        self.depth = 0
        self.sc_output = []
        self.position = 0
        self.curr_token = Token(None, None)
        self.keywords = ["true", "false", "null"]
        self.semantic_errors = 0
        self.coming_from_outer = False

    def reset(self):
        self.error_list = ['ERROR STACK:']
        self.parse_tree = Parse_Tree()
        self.depth = 0
        self.sc_output = []
        self.position = 0
        self.curr_token = Token(None, None)
        self.semantic_errors = 0

    # Panic mode
    def panic(self, message, expected=None):
        self.error_list.append(f"Error: {message}")
        sync_tokens = {TokenType.COMMA, TokenType.RBRACKET, TokenType.RBRACE, TokenType.EOF}

        # Skip tokens until a sync token is found
        while self.curr_token.datatype not in sync_tokens and self.position < len(self.sc_output):
            self.get_next_token()

        self.get_next_token()

    def validate(self, curr):
        if curr.datatype == TokenType.NUMBER:
            if (curr.content[0] == '0' and "." not in curr.content and len(curr.content)>1) or curr.content[0] == '+':
                try:
                        self.semantic_errors+=1
                        raise Exception(f"Error type 3 at {self.curr_token.content} : Number cannot start with + or 0")
                except Exception as e:
                        self.error_list.append(str(e))     

            if curr.content[-1] == ".":
                try:
                        self.semantic_errors+=1
                        raise Exception(f"Error type 1 at {self.curr_token.content} : Number cannot end with decimal point")
                except Exception as e:
                        self.error_list.append(str(e))

            i = 0
            while i<len(curr.content) and curr.content[i] != "." :
                i+=1

            if i==0 and curr.content[i] == ".":
                try:
                        self.semantic_errors+=1
                        raise Exception(f"Error type 1 at {self.curr_token.content} : Number cannot start with decimal point")
                except Exception as e:
                        self.error_list.append(str(e))


        elif curr.datatype == TokenType.STRING:
            if curr.content in self.keywords:
                try:
                        self.semantic_errors+=1
                        if self.coming_from_outer:
                            raise Exception(f"Error type 4 at {self.curr_token.content} : String cannot be a keyword")
                        else:
                            raise Exception(f"Error type 7 at {self.curr_token.content} : String cannot be a keyword") 
                except Exception as e:
                        self.error_list.append(str(e))

            elif curr.content in [" ", ''] and self.peek_next_token().datatype == TokenType.COLON:
                try:
                        self.semantic_errors+=1
                        raise Exception(f"Error type 2 at {self.curr_token.content} : String cannot be empty for a key")
                except Exception as e:
                        self.error_list.append(str(e))                 
            

    def parse(self):
        i = 0
        # Iterate over "batch of .txt files" and print parse tree in corresponding parse_tree_i.txt file
        for file in self.input_files:

            # Add each line of the file to a list
            for line in file:
                self.sc_output.append(line)
            if '<EOF, EOF>' not in self.sc_output[len(self.sc_output)-1] :
                self.sc_output.append('<EOF, EOF>')
            
            # Start parsing
            self.get_next_token()
            self.value()
            self.get_next_token()

            # CHeck that no object is initialized after the json file should have ended
            if self.curr_token.datatype != TokenType.EOF:
                try:
                        raise Exception(f"Unexpected Token: {self.curr_token.datatype} at end (Only one Object Allowed)")
                except Exception as e:
                        self.error_list.append(str(e))
            
            i+=1
            # Print to parse_tree_i.txt files
            
            with open(f'abstract_syntax_tree_{i}.txt', 'w') as file:
                if len(self.error_list) != 1:
                        for error in self.error_list:
                            file.write(error+'\n')
                else:
                        file.write("Valid JSON Syntax, No Errors\n")
                if self.semantic_errors<1:
                    file.write('\nABSTRACT SYNTAX TREE: \n')
                    file.write(self.parse_tree.parse_tree)
                else: file.write('\nNO ABSTRACT SYNTAX TREE DUE TO SEMANTIC ERROR(S): \n')

            # Reset initialized values to begin parsing next file
            self.reset()


    def value(self):

        # Find the current JSON element
        if self.curr_token.datatype == TokenType.LBRACE:

            self.parse_tree.add_node('', self.depth)
            self.depth+=1
            self.dict()
            self.depth-=1
            self.coming_from_outer = False

        elif self.curr_token.datatype == TokenType.LBRACKET:

            self.parse_tree.add_node('', self.depth)
            self.depth+=1
            self.list()
            self.depth-=1
            self.coming_from_outer = False

        elif self.curr_token.datatype in [TokenType.STRING, TokenType.NUMBER, TokenType.BOOL, TokenType.NULL]:
            self.validate(self.curr_token)
            self.parse_tree.add_node('', self.depth)
            self.depth+=1
            
            self.parse_tree.add_node(str(self.curr_token.content), self.depth) 
            self.depth-=1
        elif self.curr_token.datatype == 'EOF':
            return
        else:
            try:
                raise Exception(f"Unexpected Token: {self.curr_token.datatype} at Token: {self.position}")
            except Exception as e:
                self.panic(e)

    def list(self):
        self.coming_from_outer = True
        self.parse_tree.add_node('list', self.depth)
        self.depth+=1
        self.remove_token()
        self.get_next_token()
        list_type = self.curr_token.datatype


        # Go through tokens until RBRACKET
        while self.curr_token.datatype != TokenType.RBRACKET and self.curr_token.datatype != TokenType.EOF:
            if self.curr_token.datatype == TokenType.COMMA and self.peek_next_token().datatype == TokenType.RBRACKET:
                # Check for trailing comma before RBRACKET
                self.handle_trailing_comma_before_sync_token()

            elif self.curr_token.datatype == TokenType.COMMA:
                if self.peek_next_token().datatype != TokenType.COMMA:
                        self.remove_token()
                self.get_next_token()

                # Check for Trailing comma(s)
                if self.curr_token.datatype == TokenType.COMMA:
                        while self.peek_next_token().datatype == TokenType.COMMA:
                            self.handle_trailing_commas()

            # Handle check that the list is consistent in type
            elif self.curr_token.datatype == list_type:
                self.value()
                self.get_next_token()
            else:
                try:
                        self.semantic_errors+=1
                        if self.curr_token.datatype==TokenType.LBRACKET:
                            raise Exception(f"Error type 6 at {self.curr_token.content} : Only one type allowed in lists")
                        elif self.curr_token.datatype==TokenType.LBRACE:
                            raise Exception(f"Error type 6 at {self.curr_token.content} : Only one type allowed in lists")
                        else:    
                            raise Exception(f"Error type 6 at {self.curr_token.content} : Only one type allowed in lists")
                except Exception as e:
                        self.error_list.append(str(e))
                        self.value()
                        self.get_next_token()

                 
        # Check for unterminated list if no RBRACKET is read before EOF
        if self.position==len(self.sc_output) or self.curr_token.datatype == TokenType.EOF:
            try:
                raise Exception("List not terminated")
            except Exception as e:
                self.panic(e)
                return
            
        if self.curr_token.datatype == TokenType.RBRACKET:
            self.remove_token()
        self.depth-=1

    def dict(self):
        self.used_keys = []
        self.coming_from_outer = True
        self.parse_tree.add_node('dict', self.depth)
        self.depth+=1
        self.remove_token()
        self.get_next_token()

        # Go through tokens until RBRACE
        while self.curr_token.datatype != TokenType.RBRACE:
            # Check for unterminated Dict if no RBRACE is read before EOF
            if self.position==len(self.sc_output) or self.curr_token.datatype == TokenType.EOF:
                try:
                        raise Exception("Dict not terminated")
                except Exception as e:
                        self.panic(e)
                        return
                
            # Check for comma that's not right before a RBRACE Otherwise if comma is before RBRACE raise error
            # If not a comma then go into pair
            elif self.curr_token.datatype == TokenType.COMMA and self.peek_next_token().datatype != TokenType.RBRACE:
                if self.peek_next_token().datatype != TokenType.COMMA:
                        self.remove_token()
                self.get_next_token()

                # Check for Trailing comma(s)
                if self.curr_token.datatype == TokenType.COMMA:
                        while self.peek_next_token().datatype == TokenType.COMMA:
                            self.handle_trailing_commas()

            elif self.curr_token.datatype == TokenType.COMMA and self.peek_next_token().datatype == TokenType.RBRACE:
                if self.peek_next_token().datatype == TokenType.RBRACE:
                        # Check for trailing comma before RBRACE
                        self.handle_trailing_comma_before_sync_token()
            else:
                self.pair()


        if self.curr_token.datatype == TokenType.RBRACE:
            self.remove_token()
        self.depth-=1

    # Panic mode error recovery
    def handle_trailing_comma_before_sync_token(self):
        try:
            raise Exception(f"Trailing comma(s) at Token: {self.position}")
        except Exception as e:
            self.panic(e)

    # Panic mode error recovery
    def handle_trailing_commas(self):
        try:
            raise Exception(f"Trailing comma(s) at Token: {self.position}")
        except Exception as e:
            self.get_next_token()
            self.panic(e)

    def pair(self):
        self.parse_tree.add_node('pair', self.depth)
        self.depth+=1
        # Get STRING
        if self.curr_token.datatype == TokenType.STRING:
            if self.curr_token.content in self.used_keys:
                try:
                    self.semantic_errors+=1
                    raise Exception(f"Error type 5 at {self.curr_token.content} : No Duplicate Keys")
                except Exception as e:
                    self.error_list.append(str(e))
                    self.value()
                    self.get_next_token()
            else:           
                self.used_keys.append(self.curr_token.content)      
                self.value()
                self.get_next_token()
        else:
            try:
                raise Exception(f"Expected token {TokenType.STRING}, got {self.curr_token.datatype} at Token: {self.position}")
            except Exception as e:
                self.panic(e)
        
        # Phrase Level Recovery for Unfinished Pair
        if self.curr_token.datatype == TokenType.RBRACE:
            self.depth-=1
            self.error_list.append(f"Error: Expected token {TokenType.COLON}, got {self.curr_token.datatype} at Token: {self.position} (Incomplete Pair)")
            return
        # Get COLON if no error
        if self.curr_token.datatype == TokenType.COLON:
            self.remove_token()
            self.get_next_token()
        else:
            try:
                raise Exception(f"Expected token {TokenType.COLON}, got {self.curr_token.datatype} at Token: {self.position}")
            except Exception as e:
                self.panic(e)
                
        # Phrase Level Recovery for Unfinished Pair
        if self.curr_token.datatype == TokenType.RBRACE:
            self.depth-=1
            self.error_list.append(f"Error: Unxpected token {self.curr_token.datatype} at Token: {self.position} (Incomplete Pair)")
            return
        
        # Get value if no error
        self.value()
        self.depth-=1

        # Check for comma
        self.get_next_token()
        if self.curr_token.datatype == TokenType.COMMA:
            if self.peek_next_token().datatype not in [TokenType.COMMA, TokenType.RBRACE] :      
                self.remove_token()
                self.get_next_token()
            # Handle Trailing comma(s)
            elif self.peek_next_token().datatype == TokenType.COMMA:
                while self.peek_next_token().datatype == TokenType.COMMA:
                        self.handle_trailing_commas()
            # Handle comma before RBRACE
            elif self.peek_next_token().datatype == TokenType.RBRACE:
                        try:
                            raise Exception(f"Expected token {TokenType.RBRACE}, got {self.curr_token.datatype} at Token: {self.position} (Trailing Comma(s))")
                        except Exception as e:
                            self.panic(e)
        elif self.curr_token.datatype != TokenType.RBRACE:
            return
                
    # Turns strings collected from the input text into tokens
    def str_to_token(self, str):
        i=1
        j=0
        last = 0
        token_type = ''
        token_content = ''

        while i<len(str) and str[i] != ',':
            token_type+=str[i]
            i+=1

        # Skip space and comma
        i+=2

        # Find the index of the last char of str in order to be able to accept 
        # string token such as <STRING, J>MM>ohn>
        while j<len(str) and str[j] != '\n':
            if str[j] == '>':
                last = j
            j+=1

        while i<len(str) and str[i] != '\n':
            if str[i] == '>' and i==last:
                break
            token_content+=str[i]
            i+=1    

        return [token_type, token_content]
    
    def get_next_token(self):
        if self.position < len(self.sc_output):
            token_info = self.str_to_token(self.sc_output[self.position])
            self.curr_token = Token(token_info[0], token_info[1])
            self.position+=1

    def peek_next_token(self):
        if self.position < len(self.sc_output):
            token_info = self.str_to_token(self.sc_output[self.position])
            return Token(token_info[0], token_info[1])

    def remove_token(self):
        pass
        # self.parse_tree.add_node(self.curr_token.content, self.depth)

if __name__ == "__main__":
    input_files = []

    input_file1 = open('inputs/input_1.txt', 'r')
    input_files.append(input_file1)

    input_file2 = open('inputs/input_2.txt', 'r')
    input_files.append(input_file2)

    input_file3 = open('inputs/input_3.txt', 'r')
    input_files.append(input_file3)

    input_file1 = open('inputs/valid_input_1.txt', 'r')
    input_files.append(input_file1)

    input_file2 = open('inputs/valid_input_2.txt', 'r')
    input_files.append(input_file2)

    input_file3 = open('inputs/valid_input_3.txt', 'r')
    input_files.append(input_file3)

    my_parser = Parser(input_files)
    my_parser.parse()
    