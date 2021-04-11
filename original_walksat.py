#!/usr/bin/python3

import random
import sys


def parse(filename):
    clauses = []
    count = 0
    for line in open(filename):

        if line[0] == 'c':
            continue
        if line[0] == 'p':
            n_vars = int(line.split()[2])
            lit_clause = [[] for _ in range(n_vars * 2 + 1)]
            continue

        clause = []
        for literal in line[:-2].split():
            literal = int(literal)
            clause.append(literal)
            lit_clause[literal].append(count)
            # print("lit: ", literal, " lit_clause: ", lit_clause[literal])
        clauses.append(clause)
        count += 1
    return clauses, n_vars, lit_clause


def get_random_interpretation(n_vars):
    return [i if random.random() < 0.5 else -i for i in range(n_vars + 1)]


def get_true_sat_lit(clauses, interpretation):
    true_sat_lit = [0 for _ in clauses]
    for index, clause in enumerate(clauses):
        for lit in clause:
            if interpretation[abs(lit)] == lit:
                true_sat_lit[index] += 1
    return true_sat_lit


def update_tsl(literal_to_flip, true_sat_lit, lit_clause):
    for clause_index in lit_clause[literal_to_flip]:
        true_sat_lit[clause_index] += 1
    for clause_index in lit_clause[-literal_to_flip]:
        true_sat_lit[clause_index] -= 1


def compute_broken(clause, true_sat_lit, lit_clause, omega=0.4):
    break_min = sys.maxsize
    best_literals = []
    # print("Unsat clause: ", clause, "\n")
    for literal in clause:

        break_score = 0
        # print("\n")
        # print("literal: ", literal)
        # print("lit_clause[-literal]: ", lit_clause[-literal])
        
        for clause_index in lit_clause[-literal]:
            # print("clause_index: ", clause_index)
            # print("true_sat_lit[clause_index]: ", true_sat_lit[clause_index])
            if true_sat_lit[clause_index] == 1:
                break_score += 1
        # print("breake_score: ", break_score)
        if break_score < break_min:
            break_min = break_score
            best_literals = [literal]
        elif break_score == break_min:
            best_literals.append(literal)

    # print("\n best_literals before omega: ", best_literals)
    if break_min != 0 and random.random() < omega:
        best_literals = clause
    print("best_literals AFTER omega: ", best_literals)

    return random.choice(best_literals)


def run_sat(clauses, n_vars, lit_clause, max_flips_proportion=4):
    max_flips = n_vars * max_flips_proportion
    while 1:
        interpretation = get_random_interpretation(n_vars)
        print("interp: ", interpretation, "\n")
        true_sat_lit = get_true_sat_lit(clauses, interpretation)
        print("true_sat_lit: ", true_sat_lit, "\n")
        for _ in range(max_flips):

            unsatisfied_clauses_index = [index for index, true_lit in enumerate(true_sat_lit) if
                                         not true_lit]
            # print(unsatisfied_clauses_index)

            if not unsatisfied_clauses_index:
                return interpretation

            clause_index = random.choice(unsatisfied_clauses_index)
            unsatisfied_clause = clauses[clause_index]

            lit_to_flip = compute_broken(unsatisfied_clause, true_sat_lit, lit_clause)
            print("lit_to_flip: ", lit_to_flip)

            update_tsl(lit_to_flip, true_sat_lit, lit_clause)
            # print("\n true_sat_lit UPDATE: ", true_sat_lit, "\n")
            interpretation[abs(lit_to_flip)] *= -1
            # print("inter FLIPED: ", interpretation)


def print_results(solution):
    print('s SATISFIABLE')
    print('v ' + ' '.join(map(str, solution[1:])) + ' 0')


clauses, n_vars, lit_clause = parse(sys.argv[1])
# print("lit_clause: ", lit_clause, "\n")
solution = run_sat(clauses, n_vars, lit_clause)
print_results(solution)