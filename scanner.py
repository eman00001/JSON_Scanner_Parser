# Emmanuel Yusuff 
# B00959108
# Some code adapted from tutorial scanner

class TokenType:
    LBRACE = 'LBRACE'  # '{'
    RBRACE = 'RBRACE'  # '}'
    COMMA = 'COMMA'  # ','
    COLON = 'COLON'  # ':'
    STRING = 'STRING'  # 
    NUMBER = 'NUMBER'  # 
    BOOL = 'BOOL'
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

class LexerError(Exception):
    def __init__(self, position, character):
        super().__init__(f"Invalid character '{character}' at position {position}")

class Lexer:
    def __init__(self, input):
        self.errors = 0
        self.stream = list(input)
        self.position = 0
        self.curr_char = self.stream[self.position]
        self.symbol_table = {}
        self.q_counter = 0
        self.last_char_was_digit = False
        self.consecutive_lbraces = 0
        self.end_chars = [']', '}', ',']

    def buffer(self):
        if self.position+1 < len(self.stream):
            self.position += 1
            self.curr_char = self.stream[self.position]
        else:
            self.curr_char = None

    # Recognize string
    def handle_string(self):
        res_str = ''
        while (self.curr_char != '"' and (self.curr_char.isalnum() or self.curr_char in ['_', ' '] or self.curr_char == '\\' or self.curr_char in ['$','&','+',',',':', ';', '=', '?', '@', '#', '\'', '<','>', '.', '^', '*', '(', ')', '%', '!', '-', '/'] )):
            if  self.curr_char == '\\':
                res_str+=self.curr_char
                self.buffer()
                res_str+=self.curr_char
                self.buffer()
            else:
                res_str+=self.curr_char
                self.buffer()
       
        if self.curr_char == '"':
            self.q_counter+=1
            self.buffer()
     
        # Store string in symbol table
        self.symbol_table[res_str] = 'STRING'
        return Token(TokenType.STRING, res_str)

    def handle_number(self):
        self.last_char_was_digit = True
        res_num = ''

        while self.curr_char.isdigit() or self.curr_char in ['.', 'e', 'E', '-', '+']:
            res_num+=self.curr_char
            self.buffer()
        try:
            return Token(TokenType.NUMBER, float(res_num))
        except ValueError as e:
            raise LexerError(self.position, self.curr_char)

    def handle_bool(self):
        res_str = ''
        while self.curr_char not in self.end_chars and self.curr_char not in ['\n','\r','\t','\s', ' ']:
            res_str+=self.curr_char
            self.buffer()
        if res_str == 'true':
            return Token(TokenType.BOOL, 'true')
        elif res_str == 'false':
            return Token(TokenType.BOOL, 'false')
        else:
            self.errors+=1
            raise LexerError(self.position, self.curr_char)
        
    def handle_null(self):
        res_str = ''
        while self.curr_char not in self.end_chars and self.curr_char not in ['\n','\r','\t','\s', ' ']:
            res_str+=self.curr_char
            self.buffer()
        if res_str == 'null':
            return Token(TokenType.NULL, 'null')
        else:
            self.errors+=1
            raise LexerError(self.position, self.curr_char)
    
    # DFA here    
    def get_next_token(self):
        while self.curr_char != None:
            # Whitespace state
            if self.curr_char in ['\n','\r','\t','\s', ' ']:
                self.buffer()
                continue
            # LBRACE state       
            if self.curr_char == '{':
                self.consecutive_lbraces+=1
                self.buffer()
                return Token(TokenType.LBRACE, '{')
            # RBRACE state
            if self.curr_char == '}':
                self.consecutive_lbraces+=0
                self.buffer()
                return Token(TokenType.RBRACE, '}')
            # COMMA state
            if self.curr_char == ',':
                self.last_char_was_digit = False
                self.buffer()
                return Token(TokenType.COMMA, ',')
            # COLON State
            if self.curr_char == ':':
                self.buffer()
                return Token(TokenType.COLON, ':')
            # STRING state
            if self.curr_char == '"' and self.q_counter%2==0:
                self.q_counter+=1
                self.buffer()
                return self.handle_string()
            # NUMBER state
            if (self.curr_char.isdigit() or self.curr_char in ['-', '+']) and not self.last_char_was_digit:
                return self.handle_number()
            # BOOL state
            if self.curr_char == 't' or self.curr_char == 'f':
                return self.handle_bool()
            # NULL state
            if self.curr_char == 'n':
                return self.handle_null()
            # LBRACKET state
            if self.curr_char == '[':
                self.buffer()
                return Token(TokenType.LBRACKET, '[')
            # RBRACKET state
            if self.curr_char == ']':
                self.buffer()
                return Token(TokenType.RBRACKET, ']')
            self.errors+=1
            raise LexerError(self.position, self.curr_char)
        return Token(TokenType.EOF, 'EOF')
    
    def tokenize(self):
        tokens = []
        curr_token = self.get_next_token()
        tokens.append(curr_token)
        while curr_token.content != 'EOF':
            try:    
                curr_token = self.get_next_token()
            except LexerError as L:
                print(f"Lexical Error: {L}")
                break
            if curr_token.content != 'EOF':
                tokens.append(curr_token)
        return tokens
        
if __name__ == "__main__":
    with open('C:/Users/emiyu/Documents/Vscode work/CSCI2115/finalproject_2/yusuff/input2.json', 'r') as json_file:
        input = json_file.read()
    my_lexer = Lexer(input)
    tokens = my_lexer.tokenize()
    for token in tokens:
        print(token)