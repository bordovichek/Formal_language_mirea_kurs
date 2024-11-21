from Lexer_by_me import *

class SemanthicError(Exception):
    pass

class Syntax:
    def __init__(self, tokens: list[tuple[int, int]], n_str: int):
        self.tokens = tokens # Список с токенами
        self.curr_pos = 0# Текущая позиция
        self.token_ordering = list(enumerate(self.tokens))# Пронумерованные токены
        self.n_str = n_str# Количество строк
        self.current_line = -1# Текущая строка
        self.program_vars = []# Переменные программы


    def parse_assignment(self):
        'парсинг "выражений" вида присваения'
        if self.token_ordering[self.curr_pos + 1][1][0] in [1, 2, 5] and self.token_ordering[self.curr_pos + 2][1] not in [(3, 17), (3, 18), (3, 27), (5, 1), (5, 8)]:
            self.curr_pos += 1 # если следующий после ':=' символ подходящий для присвоения, и при этом он не является конечным символом, то обрабатываем дополнительно
            return self.parse_operand()
        if not self.token_ordering[self.curr_pos + 1][1][0] in [1, 2, 5]:
            return False
        self.curr_pos += 1
        return True


    def parse_operand(self):
        'парсинг "операндов" вида "слагаемое, отношение/сложение/умножение, слагаемое"'
        i = 0 # Счетчик для отслеживания идентификаторов и терминалов, так как они чередуются
        while self.token_ordering[self.curr_pos][1] not in [(3, 18), (3, 27), (3, 17)]:
            if i % 2 == 0:
                if not self.token_ordering[self.curr_pos][1][0] in [1, 2]:
                    if not (self.token_ordering[self.curr_pos][1][0] == 5 and self.token_ordering[self.curr_pos][1][0] in [2, 3]): # Если на месте для идентификаторов нет идентификатора, то ошибка
                        return False
            else:
                if not (self.token_ordering[self.curr_pos][1][0] == 3 and self.token_ordering[self.curr_pos][1][1] in list(range(1, 12))): # Если на метсе для терминалов не стоит подходящий, то ошибка
                    if i > 2: # Если уже есть 2 идентификатора, то выходим
                        return True
                    return False
            self.curr_pos += 1
            i += 1
        return True # Выход для случая наличия символов окончаний в виде скобок, ";" и ":"


    def parse_if(self):
        'парсинг if-ов'
        # Парсер скобочек и выражения в них
        if not self.token_ordering[self.curr_pos][1] == (3, 26): # Если после if не стоит скобочка
            return False
        if self.token_ordering[self.curr_pos + 1][1] == (5, 4): # Если внутри скобок составной оператор
            self.curr_pos += 1
            if self.parse_sost_op():
                self.curr_pos += 1
                if self.token_ordering[self.curr_pos][1] != (3, 27):
                    raise SyntaxError("Неправильное объявление блока if, закройте скобку")
        else:
            self.curr_pos += 1
            if not self.parse_operand():
                return False
            if not self.token_ordering[self.curr_pos][1] == (3, 27):
                raise SyntaxError("Неправильное объявление блока if, закройте скобку")
        self.curr_pos += 1
        # парсер части после условия
        if self.token_ordering[self.curr_pos][1] == (5, 4):  # если первый оператор составной
            if self.parse_sost_op():
                self.curr_pos += 1
                if self.token_ordering[self.curr_pos][1]  in [(3, 17), (3, 18)]:  # если после end для if идет завершение строки
                    return True
                elif self.token_ordering[self.curr_pos][1] == (5, 6):  # если есть блок else
                    if not self.parse_else():
                        raise SyntaxError("Ошибка при составлении блока else")
                else:
                    raise SyntaxError("Ошибка при составлении оператора if")
        else:  # первый оператор обычный
            current_token = self.curr_pos # Создаем переменную для запоминания позиции, так как при парсинге она сдвинется, а нам надо будет парсить именно с определенной позиции
            if self.parse_operand():
                self.curr_pos += 1
                if self.token_ordering[self.curr_pos] == (3, 18):
                    return True
                else:
                    if not self.parse_else():
                        raise SyntaxError("Ошибка при составлении блока else")
            else:
                self.curr_pos = current_token
                if self.parse_io():
                    self.curr_pos += 1
                    if self.token_ordering[self.curr_pos] == (3, 18):
                        return True
                    else:
                        if not self.parse_else():
                            raise SyntaxError("Ошибка при составлении блока else")
                else:
                    raise SyntaxError("Ошибка при составлении оператора if")
        return True


    def parse_else(self):
        'вспомогательная функция для парсинга блока else'
        if self.token_ordering[self.curr_pos + 1][1] == (5, 4):  # если есть составной оператор
            self.curr_pos += 1
            if self.parse_sost_op():
                self.curr_pos += 1
                if self.token_ordering[self.curr_pos] == (3, 11):  # если после end для else идет завершение строки
                    return True
                else:
                    raise SyntaxError("Ошибка при составлении блока else оператора if")
        else:  # если else обычный
            if self.token_ordering[self.curr_pos][1][0] != 1:
                self.curr_pos += 1
            if self.token_ordering[self.curr_pos + 1][1] == (3, 14):  # если у нас присваивающая операция
                self.curr_pos += 1
                if self.parse_assignment():
                    self.curr_pos += 1
                    if not self.token_ordering[self.curr_pos][1] == (3, 18):
                        raise SyntaxError("Ошибка при составлении блока else оператора if")
            elif self.parse_operand():  # если у нас обычная операция
                self.curr_pos += 1
                if self.token_ordering[self.curr_pos] == (3, 11):
                    return True
                else:
                    raise SyntaxError("Ошибка при составлении блока else оператора if")
            else:
                raise SyntaxError("Ошибка при составлении блока else оператора if")
        return True


    def parse_for(self):
        'парсинг циклов вида for'
        if self.token_ordering[self.curr_pos][1][0] != 1 or self.token_ordering[self.curr_pos+1][1] != (3, 14):
            return False  # Если после for идет не присваивание
        if self.token_ordering[self.curr_pos][1] not in self.program_vars:
            raise  SemanthicError("Попытка присвоения необъявленной переменной")
        self.curr_pos += 1
        if not self.parse_assignment():
            raise  SyntaxError("Присваивание для for оформлено неправильно")
        self.curr_pos += 1
        if self.token_ordering[self.curr_pos][1] != (5, 8):
            raise SyntaxError("Пропущено слово to")
        self.curr_pos += 1
        if not self.pars_exsp():
            raise SyntaxError("Неправильно составлено выражение после to")
        while self.token_ordering[self.curr_pos][1] == (5, 9): # Так как у нас может быть много условий, то ждем, пока они все не будут перечислены
            self.curr_pos += 1
            if self.pars_exsp():
                continue
            raise SyntaxError("Неправильно составлено выражение после step")
        if self.token_ordering[self.curr_pos][1] == (5, 4): # Если оператор составной
            if not self.parse_sost_op():
                raise SyntaxError("Ошибка в операторе цикла for")
        elif not self.parse_sost_vars():
            raise SyntaxError("Ошибка в операторе в цикле")
        if self.token_ordering[self.curr_pos-1][1] == (3,18):  # Костыль для случая вылета за пределы ":"
            self.curr_pos -= 1
        if not self.token_ordering[self.curr_pos][1] != (5, 10):
            raise SyntaxError("Отсутствует ключевое слово next")
        if self.token_ordering[self.curr_pos][1] != (3, 18):
            raise SyntaxError("Отсутствует символ конца строки после next")
        return True


    def parse_while(self):
        'Парсинг циклов вида while'
        if not self.token_ordering[self.curr_pos][1] == (3, 26):
            return False # Скобочка после while
        self.curr_pos += 1
        if not self.pars_exsp():
            raise SyntaxError("Ошибка в выражении внутри условия while")
        if self.token_ordering[self.curr_pos][1] != (3, 27):
            raise SyntaxError("Скобка для выражения внутри while не была закрыта")
        self.curr_pos += 1
        if self.token_ordering[self.curr_pos][1] == (5, 4): # Если составной
            if not self.parse_sost_op():
                raise SyntaxError("Ошибка в операторе после объявления while")
        else:
            if not self.parse_sost_vars():
                raise  SyntaxError("Ошибка в операторе после объявления while")
        if self.token_ordering[self.curr_pos][1] != (3, 18):
            raise SyntaxError("Отсутствует символ окончания строки после цикла while")
        return True



    def find_semicolon(self):
        'вспомогательная функция для поиска ";" в составных операторах'
        if self.token_ordering[self.curr_pos][1] in [(3, 17), (5, 1)]:
            return True
        elif self.token_ordering[self.curr_pos - 1][1] in [(3, 17), (5, 1)]:
            self.curr_pos -= 1
            return True
        elif self.token_ordering[self.curr_pos + 1][1] in [(3, 17), (5, 1)]:
            self.curr_pos += 1
            return True
        else:
            raise SyntaxError("Ошибка в составлении составного оператора")


    def parse_sost_op(self):
        'парсинг состовных операторов'
        if self.token_ordering[self.curr_pos][1] == (5,1):
            raise SyntaxError("Составной оператор пуст")
        while self.token_ordering[self.curr_pos][1] != (5, 1): # Пока не дойдем до end
            self.curr_pos += 1
            current_pos = self.curr_pos  # Сохраняем текущую позицию, так как нас предстоит проверить все вариации операторов
            oper1 = self.parse_sost_vars()
            if oper1: # Если внутри блоков begin end есть оператор, то запоминаем это и смотри на наличие ";" или end
                if self.find_semicolon():
                    continue
            self.curr_pos = current_pos
            oper2 = self.parse_operand()
            if oper2:
                if self.find_semicolon():
                    continue
            self.curr_pos = current_pos + 1
            oper3 = self.parse_if()
            if oper3:
                if self.find_semicolon():
                    continue
            self.curr_pos = current_pos
            oper4 = self.parse_io()
            if oper4:
                if self.find_semicolon():
                    continue
            self.curr_pos = current_pos
            oper5 = self.parse_for()
            if oper5:
                if self.find_semicolon():
                    continue
            self.curr_pos = current_pos
            oper6 = self.parse_while()
            if oper6:
                if self.find_semicolon():
                    continue
            else: # Если не найдено никаких операторов
                raise SyntaxError("Ошибка при составлении составного оператора")
        return True


    def parse_vars(self):
        'парсер объявления переменных'
        while self.token_ordering[self.curr_pos][1][0] != 4:
            if self.token_ordering[self.curr_pos][1][0] != 1 and self.token_ordering[self.curr_pos][1] != (3, 15): # Проверка, что текущий символ идентификатор, а следующий - запятая
                if self.token_ordering[self.curr_pos][1] == (3, 18) and (
                        self.token_ordering[self.curr_pos + 1][1][0] == 4 or self.token_ordering[self.curr_pos + 1][1] == (3, 13)):
                    # Если это не так, то смотрим, текущий ли символ ":" и даем ли мы идетификаторам тип данных
                    self.curr_pos += 1
                    return True
                else:
                    return False
            else:
                if self.token_ordering[self.curr_pos][1][0] == 1 and self.token_ordering[self.curr_pos+1][1] in [(3, 15), (3, 18)]:
                    if self.token_ordering[self.curr_pos][1] in self.program_vars:
                        raise SemanthicError("Объявление переменной второй раз")
                    else:
                        self.program_vars.append(self.token_ordering[self.curr_pos][1])
                self.curr_pos += 1


    def parse_sost_vars(self):
        'парсинг видов операторов и классификация'
        if self.token_ordering[self.curr_pos][1][0] == 3 and self.token_ordering[self.curr_pos][1][1] in list(range(1, 7)):
            # Поиск начала "выражения"
            self.curr_pos -= 1
            return self.pars_exsp()
        if self.token_ordering[self.curr_pos + 1][1] == (3, 14):  # Если у нас состояние "присвоения"
            self.curr_pos += 1
            if self.parse_assignment():
                if self.token_ordering[self.curr_pos][1] != (3, 18):
                    self.curr_pos += 1
                return True
            else:
                return False
        elif self.parse_vars():  # Состояние объяаления переменных
            self.curr_pos += 1
            return True
        else:
            return False


    def parse_io(self):
        'парсер операторов ввода и вывода'
        if self.token_ordering[self.curr_pos][1] == (5, 12): # Если read, то просто смотрим, чтобы после него были идентификаторы и окончание строки/скобок/условия
            i = 0
            self.curr_pos += 1
            while self.token_ordering[self.curr_pos][1] not in [ (3, 27), (5, 1), (5, 6),(3, 18)]:
                if i % 2 == 0:
                    if self.token_ordering[self.curr_pos][1][0] != 1:
                        return False
                    i += 1
                    self.curr_pos += 1
                else:
                    if self.token_ordering[self.curr_pos][1] != (3, 15):
                        return False
            return True
        elif self.token_ordering[self.curr_pos][1] == (5, 13): # Если write, то смотрим чтобы после него было "выражение"
            self.curr_pos += 1
            return self.pars_exsp()


    def pars_exsp(self):
        'парсинг "выражений" согласно методичке'
        if self.token_ordering[self.curr_pos][1][0] in [1, 2] or (
                self.token_ordering[self.curr_pos][1][0] == 5 and self.token_ordering[self.curr_pos][1][1] in [2, 3]
        ):
            if self.token_ordering[self.curr_pos][1] not in [(3, 11), (3, 27)]:
                return self.parse_operand()
            else:
                return True
        return False


    def step_by_step_pars(self):
        'основной проход парсера с последующей обработкой и вызовом остальных функций'
        for line in range(self.n_str): # Запоминаем номер обрабатываемой строки
            self.current_line = line + 1
            for token_info in self.token_ordering[self.curr_pos:]:
                if self.curr_pos > token_info[0]: # Так как в функциях выше мы сдвигаемся, то нужно пропускать уже обработанные токены
                    continue
                if token_info[1][0] == 1: # Если идентификатор, то обрабатываем соответствующе
                    if self.parse_sost_vars():
                        continue
                if token_info[1] == (5, 5): # Если условие
                    self.curr_pos = token_info[0] + 1
                    if self.parse_if():
                        continue
                    else:
                        raise SyntaxError("Отсутствует открывающаяся скобка после ключевого слова if")
                if token_info[1] == (5, 7): # Если цикл for
                    self.curr_pos += 1
                    if self.parse_for():
                        continue
                    else:
                        raise SyntaxError("Отсутствует открывающаяся скобка после ключевого слова for")
                if token_info[1] == (5, 11): # Если цикл while
                    self.curr_pos += 1
                    if self.parse_while():
                        continue
                    else:
                        raise SyntaxError("Отсутствует открывающаяся скобка после ключевого слова while")
                if token_info[1] in [(5, 12), (5, 13)]: # Если оператор вида IO
                    if self.parse_io():
                        continue
                    else:
                        raise  SyntaxError("Ошибка в операторе чтения/записи")
                if token_info[1] == (3, 18): # Если символ окончания строки, то запоминаем текущую позицию и переходим на новую строку
                    self.curr_pos = token_info[0] + 1
                    break
                if token_info[1] == (5, 4): # Если составной оператор
                    self.curr_pos += 1
                    if self.parse_sost_op():
                        continue
                if token_info[1] != (5, 1) and token_info[1][0] != 6: # Если в конце не стоит end, и при этом это не спецсивол EOF, то ошибка, так как не можем обработать токен
                    raise SyntaxError("Ошибка в структуры программы")
        return "Анализируемый код не содержит синтаксических ошибок" # Если мы прошлись по всем строкам и не подняли исключений, то все хорошо


if __name__ == "__main__":
    with open('test_1_1.txt', 'r') as file:
        text = file.read()
    lexer = Lexer(text)
    try:
        tokens = lexer.lex()
        list_of_tokens = lexer.token_positions
    except Exception as e:
        print(e)
    else:
        try:
            synt_parse = Syntax(list_of_tokens, lexer.num_str) # Создаем объект синтаксического анализатора вместе с токенами и количеством строк в программе
            print(synt_parse.step_by_step_pars())
        except Exception as SE:
            print(f'В строке {synt_parse.current_line} содержится ошибка {repr(SE)}')