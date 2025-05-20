import re
# Множество терминалов (символы, которые нельзя раскрыть дальше)
T = {'!', '+', '*', '(', ')', 'И'}

# Правила грамматики в формате: [нетерминал, правая часть, номер альтернативы]
grammar_rules = [
    ['A', '!B!', 1],
    ['B', "TB'", 1],
    ["B'", "+TB'", 1],
    ["B'", "", 2],
    ['T', "MT'", 1],
    ["T'", "*MT'", 1],
    ["T'", "", 2],
    ['M', 'И', 1],
    ['M', '(B)', 2]
]

# Максимальное количество альтернатив для каждого нетерминала
max_alternatives = {'A': 1, 'B': 1, 'T': 1, 'M': 2, "T'": 2, "B'" : 2}

def has_more_alternatives(L1):
    return L1[2] < max_alternatives[L1[0]]

# Замена нетерминала на правую часть правила в L2 и добавление правила в L1
def expand_nonterminal(L1, L2):
    current_chain = L2[-1]
    
    # Ищем самый левый нетерминал (может быть из 1 или 2 символов)
    if len(current_chain) >= 2 and current_chain[:2] in max_alternatives:
        # Если первые два символа образуют нетерминал (B' или T')
        current_nt = current_chain[:2]
        remaining = current_chain[2:]
    else:
        # Иначе берем первый символ как нетерминал
        current_nt = current_chain[0]
        remaining = current_chain[1:]
    
    for rule in grammar_rules:
        if rule[0] == current_nt:
            L1.append(rule)
            if rule[1] == "E":
                L2[-1] = remaining
            else:
                L2[-1] = rule[1] + remaining
            break

# Добавление терминала из L2 в L1
def add_terminal(L1, L2):
    L1.append(L2[-1][0])
    L2[-1] = L2[-1][1:]

# Строим массив с результатом (номера правил)
def build_result(L1, res):
    for item in L1:
        if len(item) == 3:
            res.append(grammar_rules.index(item) + 1)

# Откат терминала
def rollback(L1, L2):
    L2[-1] = L1[-1][0] + L2[-1]
    L1.pop()

# Замена правила другой альтернативой 
def next_altern(L1, L2):
    tmp = L1.pop()
    next_rule = grammar_rules[grammar_rules.index(tmp) + 1]
    L1.append(next_rule)
    L2[-1] = L2[-1].replace(tmp[1], next_rule[1], 1)

# Откат на уровень выше
def back_level(L1, L2):
    tmp = L1.pop()
    L2[-1] = L2[-1].replace(tmp[1], tmp[0], 1)

def parser(s):
    if not s:  
        return "Ошибка: пустая входная строка"
    
    state = 'q'
    i = 0
    result = []
    S = 'A'
    L1 = []
    L2 = [S]

    while True:
        if state == 'q':
            if not L2[-1]:
                if not L2[0] and i == len(s):
                    build_result(L1, result)
                    state = 't'
                else:
                    state = 'b'
            elif L2[-1][0] not in T:
                expand_nonterminal(L1, L2)
            elif i < len(s) and L2[-1][0] == s[i]:  # or (L2[-1][0] == "И" and s[i].isalpha())
                add_terminal(L1, L2)
                i += 1
                if i == len(s):
                    if not L2[0]:
                        build_result(L1, result)
                        state = 't'
                    else:
                        state = 'b'
            else:
                state = 'b'

        elif state == 'b':
            if not L1:
                return "Ошибка разбора"
            elif L1[-1][0] in T:
                rollback(L1, L2)
                i -= 1
            elif has_more_alternatives(L1[-1]):
                next_altern(L1, L2)
                state = 'q'
            elif L1[-1][0] == S and i == 0:
                return "Ошибка разбора"
            else:
                back_level(L1, L2)

        elif state == 't':
            return result


def main():
    test_input = "!a+b*c!"
    input = re.sub(r'[a-z]', 'И', test_input)
    result = parser(input)
    if isinstance(result, list):
        print("Номера правил:", " ".join(map(str, result)))
    else:
        print(result)

if __name__ == "__main__":
    main()  

    # "!a+b!"                    { 1 3 4 6 2 4 7 }
    # "!a*b!"                    { 1 2 5 6 4 7 }
    # !(a+b)*(b+a)!              { 1 2 5 8 3 4 6 2 4 7 4 8 3 4 7 2 4 6 }
    # !b*a+a*b!                  { 1 3 5 7 4 6 2 5 6 4 7 }
    # !(a+b)*a+b*a!              { 1 3 5 8 3 4 6 2 4 7 4 6 2 5 7 4 6 }
    # !(a+b*a)*(b*b+a*(a+b+a))!  { 1 2 5 8 3 4 6 2 5 7 4 6 4 8 3 5 7 4 7 2 5 6 4 8 3 4 6 3 4 7 2 4 6 }
    # !a+*b!                     Сообщение об ошибке.
    # a+b*a+b                    Сообщение об ошибке.
    # a!b                        Сообщение об ошибке.
    # !a(b+a()!                  Сообщение об ошибке.

