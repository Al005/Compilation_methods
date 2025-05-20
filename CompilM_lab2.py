from collections import defaultdict


productions = {
    'A': [['!', 'B', '!']],
    'B': [['T'], ['B', '+', 'T'], ['B', '-', 'T']],
    'T': [['M'], ['T', '*', 'M'], ['T', '/', 'M']],
    'M': [['a'], ['b'], ['c'], ['d'], ['x'], ['y'], ['(', 'B', ')']],
}

terminals = sorted({'!', '+', '-', '*', '/', '(', ')', 'a', 'b', 'c', 'd', 'x', 'y'})

nonterminals = set(productions.keys())

# Построение множеств L(U) и R(U)
def createLR():
    L = defaultdict(set)
    R = defaultdict(set)

    # Шаг 1: первые и последние символы правил
    for head, bodies in productions.items():
        for body in bodies:
            if body:
                L[head].add(body[0])
                R[head].add(body[-1])

    # Шаг 2
    changed = True
    while changed:
        changed = False
        for head in productions:
            new_L = set()
            new_R = set()

            # Для каждого sym in L(U), если sym - нетерминал и sym != U
            for sym in L[head]:
                if sym in nonterminals and sym != head:
                    new_L |= L[sym]

            for sym in new_L:
                if sym not in L[head]:
                    L[head].add(sym)
                    changed = True


            for sym in R[head]:
                if sym in nonterminals and sym != head:
                    new_R |= R[sym]

            for sym in new_R:
                if sym not in R[head]:
                    R[head].add(sym)
                    changed = True

    return dict(L), dict(R)


# Построение множеств Lt(U) и Rt(U)
def createLtRt(L, R):
    Lt = defaultdict(set)
    Rt = defaultdict(set)

    # Шаг 1
    for head, bodies in productions.items():
        for body in bodies:
                
            # Самые левые с точностью до нетерминала
            if body[0] in terminals:
                Lt[head].add(body[0])
            elif len(body) >= 2 and body[0] in nonterminals and body[1] in terminals:
                Lt[head].add(body[1])
            
            # Самые правые с точностью до нетерминала
            if body[-1] in terminals:
                Rt[head].add(body[-1])
            elif len(body) >= 2 and body[-2] in terminals and body[-1] in nonterminals:
                Rt[head].add(body[-2])


    # Шаг 2
    changed = True
    while changed:
        changed = False
        for head in productions:
            # пробегаемся по L
            for sym in L[head]: 
                if sym in nonterminals and sym != head: 
                    for t in Lt[sym]: # добавляем в Lt(U) терминалы из Lt(U')
                        if t not in Lt[head]:
                            Lt[head].add(t)
                            changed = True
                            
            # пробегаемся по R
            for sym in R[head]:
                if sym in nonterminals and sym != head:
                    for t in Rt[sym]:
                        if t not in Rt[head]:
                            Rt[head].add(t)
                            changed = True

    return dict(Lt), dict(Rt)


# Создание матрицы операторного предшествования
def build_matrixOP(Lt, Rt):
    matrix = defaultdict(dict)

    for head, bodies in productions.items():
        for body in bodies:
            n = len(body)
            for i in range(n - 1):
                a, b = body[i], body[i+1]

                # Правило 1: t_i =· t_j
                if a in terminals and b in terminals:
                    matrix[a][b] = '='

                # Правило 1 через нетерминал: t_i C t_j
                if i+2 < n and a in terminals and b in nonterminals and body[i+2] in terminals:
                    matrix[a][body[i+2]] = '='

                # Правило 2: t_i <· t_j (если t_i перед нетерминалом)
                if a in terminals and b in nonterminals:
                    for t in Lt[b]:
                        matrix[a][t] = '<'

                # Правило 3: t_i >· t_j (если t_j после нетерминала)
                if a in nonterminals and b in terminals:
                    for t in Rt[a]:
                        matrix[t][b] = '>'

    return matrix


rules = [
    (['!', 'N', '!'], 'A', [], 1),
    (['N', '+', 'N'], 'B', ['+'], 2),
    (['N', '-', 'N'], 'B', ['-'], 3),
    (['N', '*', 'N'], 'T', ['*'], 4),
    (['N', '/', 'N'], 'T', ['/'], 5),
    (['a'], 'M', ['a'], 6),
    (['b'], 'M', ['b'], 7),
    (['c'], 'M', ['c'], 8),
    (['d'], 'M', ['d'], 9),
    (['x'], 'M', ['x'], 10),
    (['y'], 'M', ['y'], 11),
    (['(', 'N', ')'], 'M', [], 12)
]


# Анализатор
def analyze(input_str, matrix):
    input_str += '#'
    stack = ['#']
    pos = 0
    poliz = []
    trace = []

    def top_term():
        for sym in reversed(stack):
            if sym in terminals or sym == '#':
                return sym
        return None

    while True:
        a = top_term()
        b = input_str[pos]

        # Специальная обработка символа '#' 
        if a == '#' and b != '#':
            rel = '<'
        elif a != '#' and b == '#':
            rel = '>'
        elif a == '#' and b == '#':
            rel = '='
        else:
            if a not in matrix or b not in matrix[a]:
                raise SyntaxError(f"Нет отношения между '{a}' и '{b}'")
            rel = matrix[a][b]

        # Перенос
        if rel in ('<', '='):
            stack.append(b)
            pos += 1

        # Свертка 
        elif rel == '>':
            matched = False
            for pattern, lhs, plz, num in rules:
                len_pattern = len(pattern)
                if len(stack) < len_pattern:
                    continue
                window = stack[-len_pattern:]

                # проверка соответствия pattern и window
                ok = True
                for ps, ws in zip(pattern, window):
                    if ps == 'N':
                        if ws not in {'M', 'T', 'B'}:
                            ok = False
                            break
                    elif ps != ws:
                        ok = False
                        break
                if not ok:
                    continue

                # свертка
                del stack[-len_pattern:]
                stack.append(lhs)
                trace.append(num)
                poliz.extend(plz)
                matched = True
                break

            if not matched:
                raise SyntaxError(f"Невозможно выполнить свёртку: стек = {stack}")

        else:
            raise SyntaxError(f"Неверное отношение: {rel}")

        # Завершение анализа
        if stack == ['#', 'A'] and input_str[pos] == '#':
            break

    return trace, poliz


def main():

    L, R = createLR()
    Lt, Rt = createLtRt(L, R)
    MOP = build_matrixOP(Lt,Rt)
    gramm, poliz = analyze('!a-(b-c)!', MOP)

    # print("\nМножество Lt(U):")
    # for nt in sorted(nonterminals):
    #     print(f"{nt}: {sorted(Lt[nt])}")

    # print("\nМножество Rt(U):")
    # for nt in sorted(nonterminals):
    #     print(f"{nt}: {sorted(Rt[nt])}")

    # print("\nМатрица операторного предшествования (ФОП):\n")
    # header = "     " + " ".join(f"{t:>2}" for t in terminals)
    # print(header)
    # print("    " + "-" * (len(header)-4))

    # for row in terminals:
    #     line = f"{row:>2} |"
    #     for col in terminals:
    #         rel = MOP.get(row, {}).get(col, ' ')
    #         line += f" {rel:>2}"
    #     print(line)

    print("Номера правил:", gramm)
    print("ПОЛИЗ:", poliz)


    variables = {'a': 5, 'b': 3, 'c': 2, 'x': 5, 'y': 6}

    stack_poliz = []
    for i in poliz:
        if i in variables:
            stack_poliz.append(variables[i])
        elif i in {'+', '-', '*', '/'}:
            if len(stack_poliz) < 2:
                raise ValueError("Недостаточно операндов в стеке")

            b = stack_poliz.pop()
            a = stack_poliz.pop()

            if i == '+':
                stack_poliz.append(a + b)
            elif i == '-':
                stack_poliz.append(a - b)
            elif i == '*':
                stack_poliz.append(a * b)
            elif i == '/':
                if b == 0:
                    raise ZeroDivisionError("Деление на ноль")
                stack_poliz.append(a / b) 
        else:
            raise ValueError(f"Неизвестный элемент: {i}")

    if len(stack_poliz) != 1:
        raise ValueError("Ошибка в выражении: стек содержит больше одного элемента")

    print(stack_poliz[0])


if __name__ == "__main__":
    main()  
