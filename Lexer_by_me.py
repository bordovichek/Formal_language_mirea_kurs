import re
import string

letters = list(string.ascii_lowercase + string.ascii_uppercase)
digits = list(string.digits)

class TokenType:
    IDENTIFIER = 1
    NUMBER = 2
    OPERATOR = 3
    DATA_TYPE = 4
    SPECIAL = 5
    EOF = 6

class Token:
    def __init__(self, token_type, value, position):
        self.token_type = token_type
        self.value = value
        self.position = position

    def __repr__(self):
        return f'Токен({self.token_type}, {self.value}) на позиции {self.position}'

SPECIAL = ['end',  'true', 'false', 'begin', 'if', 'else', 'for', 'to', 'step', 'next', 'while', 'readln', 'writeln']
OPERATORS_RELATION = {"= !=": (3, 1), "= =": (3, 2), "<": (3, 3), "<=": (3, 4), ">": (3, 5), ">=": (3, 6)}
OPERATORS_SUM = {"+": (3, 7), "-": (3, 8), "||": (3, 9)}
OPERATORS_MUL = {"*": (3, 10), "/": (3, 11), "&&": (3, 12)}
UNARY_OPERATORS = {"!": (3, 13)}
ASSIGMENT_OPER = {":=": (3, 14)}
DATA_TYPE = {'%': (4, 1), '!': (4, 2), '$': (4, 3)}
OTHER_SYMBOLS = {',': (3, 15), '.': (3, 16), ';': (3, 17), ':': (3, 18), '?': (3, 19), '"': (3, 20), "'": (3, 21), '[': (3, 22), ']': (3, 23), '{': (3, 24), '}': (3, 25), '(': (3, 26), ')': (3, 27),  '@': (3, 28), '#': (3, 29), '^': (3, 30)}

NUMBER_PATTERN = re.compile(
        r"\b(?:"
        r"[01]+[bB]|"                   
        r"[0-7]+[oO]|"                  
        r"\d+(?:\.\d*)?(?:e[+-]?\d+)?|"
        r"[0-9A-F]+[hH]|"               
        r"\d+\.\d+e[+-]?\d+"         
        r")\b"
    ) # регулярное выражение для поиска чисел


class Lexer:
    def __init__(self, text):
        self.text = text  # Весь код проверяеммой программы в виде строки
        self.position = 0 # Текущая позиция
        self.tokens = [] # Список токенов
        self.token_positions = [] # Список с позициями токенов
        self.state = "OTHER" # Состояние анализатора
        self.num_str = text.count('\n') + 1 # Подсчет количество строк (смотри на свой вариант)
        self.vars = [] # Список для переменных
        self.numbers = [] # Список для чисел
        self.flag_space = False # Флаг для пробелов
    def get_char(self):
        'Получение текущего символа'
        if self.position < len(self.text):
            return self.text[self.position]
        return None

    def advance(self):
        'Сдвиг на один сивол'
        self.position += 1

    def skip_whitespace(self):
        'Пропуск пробелов'
        while self.get_char() and self.get_char().isspace(): # Пока получаемый символ пробел, пропускаем
            self.advance()
        self.flag_space = True
        # Флаг нужен для того, чтобы при выходе из функции анализатор продолжил итерироваться,
                                    # а не остановился из=за ошибки

    def is_id(self, name):
        'Проверка возможности строки быть названием переменной'
        naming = bool(name) and name[0] in letters and all(char in letters + digits for char in name[1:]) # Если не пустая строка, первый символ буква, а остальные буквы или цифра, то подходит
        pos = self.text[self.position-len(name)-1].isdigit() # Дополнительная проверка, что позади строки нет чисел
        return naming and (not pos)

    def match_operator(self):
        'Поиск совпадений с оператором'
        for op_group in [ASSIGMENT_OPER,OPERATORS_RELATION, OPERATORS_SUM, OPERATORS_MUL, UNARY_OPERATORS, DATA_TYPE, OTHER_SYMBOLS]: # Перебор нащих загатовленных терминалов
            for op in sorted(op_group.keys(), key=len, reverse=True):
                op_length = len(op)
                text_segment = self.text[self.position:self.position + op_length]
                if text_segment == '(*': # Если нашли начало комментария, то скипаем их
                    self.skip_komment()
                    continue
                if text_segment == op: # Если нашли совпадение, то
                    self.position += op_length # Сдвигаем коретку на длину оператора
                    category, place = op_group[op] # Полуаем его тип и позицию
                    self.token_positions.append((category, place)) # Добавляем в список позиционных токенов
                    self.state = "OPERATOR" if op not in DATA_TYPE.keys() else "DATA_TYPE"  # Ставим подходящее состояние
                    return Token(TokenType.__dict__[self.state], op, self.position) # Возвращаем объект токена
        return None # Ничего не возвращаем, если не нашли совпадений

    def skip_komment(self):
        'Пропуск комментариев'
        while (symb := self.get_char()) != ')': # Пока нет закрывающегося символа комментария, пропускаем
            self.advance()
        self.advance()

    def lex(self):
        'Основной метод класса, посимвольный перебор'
        while self.position < len(self.text): # Пока не кончился текст и символ не пробел
            self.flag_space = False
            current_char = self.get_char()
            if current_char.isspace():
                self.skip_whitespace()
                continue

            value = ""

            if NUMBER_PATTERN.match(self.text[self.position:]): # Ищем совпадение с числовым регулярным выражением
                self.state = "NUMBER"
                match = NUMBER_PATTERN.match(self.text[self.position:])
                value = match.group(0) # Получаем это число
                if value not in self.numbers:
                    self.numbers.append(value)
                self.position += len(value) # Сдвигаемся на длину числа
                self.tokens.append(Token(TokenType.__dict__[self.state], value, self.position)) # Добавляем токен числа
                self.token_positions.append((TokenType.__dict__[self.state], self.numbers.index(value)+1)) # Добавляем кортед в позиционный список токенов
                continue

            while current_char and (current_char.isalpha() or current_char.isdigit() or current_char == '_'):
                #если не число, то собираем строку из сиволов, пока она не станет значащей (т.е. словом или терминалом)
                value += current_char
                self.advance()
                current_char = self.get_char()


            if value in SPECIAL: # Проверка на "специальность" слова
                self.state = "SPECIAL"
                self.tokens.append(Token(TokenType.__dict__[self.state], value, self.position))
                self.token_positions.append((TokenType.__dict__[self.state], SPECIAL.index(value) + 1))
                continue

            if self.is_id(value): # Если строка может быть названием для переменной, то добавляем ее как переменную
                self.state = "IDENTIFIER"
                if value not in self.vars: # Следим за уникальностью имен, чтобы не возникало ошибок и путаницы
                    self.vars.append(value)
                self.tokens.append(Token(TokenType.__dict__[self.state], value, self.position))
                self.token_positions.append((TokenType.__dict__[self.state], self.vars.index(value)+1))
                continue

            operator_token = self.match_operator() # Если строка это терминальный символ
            if operator_token:
                continue
            if self.flag_space:
                self.flag_space =False
                continue
            if value: # Если мы так и не смогли обработать символ, то показываем ошибку
                raise ValueError(f"Ошибка при обработке {value} на позиции {self.position}")

        self.tokens.append(Token(TokenType.EOF, None, self.position))
        self.token_positions.append((TokenType.EOF, 1))
        return self.tokens


def analyze_file(file_path): # Открытие и чтение файла
    with open(file_path, 'r') as file:
        text = file.read()
    lexer = Lexer(text)
    try:
        tokens = lexer.lex()
        a = lexer.token_positions
        print(a)
        print(lexer.num_str)
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    analyze_file('test_1_1.txt')
