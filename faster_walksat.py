#!/usr/bin/python3

import random
import sys


def read_file(filename):
    clauses = []
    count = 0

    for line in open(filename):
        if line[0] == 'c':
            # skip comment lines
            continue
        elif line[0] == 'p':
            # save number of variables of the problem and create a list that stores the index numbers of clauses where the literal appears
            num_vars = int(line.split()[2])
            lit_clause = [[] for _ in range(num_vars * 2 + 1)]
            continue
        else:
            # read clause and for each literal in the clause record the index of the clause in which it appears
            clause = []
            for literal in line[:-2].split():
                literal = int(literal)
                clause.append(literal)
                lit_clause[literal].append(count)

            clauses.append(clause)
            count += 1

    return clauses, num_vars, lit_clause


def get_random_interpretation(num_vars):
    # generate a list with random positive and negative values for each variable in the problem 
    # note that lenth of the list is num_vars + 1, so variable 1 corresponds to position 1 in the list
    return [i if random.random() < 0.5 else -i for i in range(num_vars + 1)]


def get_true_sat_lit(clauses, interpretation):
    # given an interpretation, for each clause of the problema check how many literals satisfy that clause
    # returns a list with the length of the clauses in the problem, where each position stores the satisfied literals of the clause 
    # index of this list = index of clause from the problem -> true_sat_lit[0] = clauses[0]
    true_sat_lit = [0] * len(clauses) # [0 for _ in clauses]

    for index, clause in enumerate(clauses):
        for lit in clause:
            if interpretation[abs(lit)] == lit:
                true_sat_lit[index] += 1

    return true_sat_lit


def update_tsl(literal_to_flip, true_sat_lit, lit_clause):
    # get index of clauses where the literal to flip appears
    # in true_sat_lit[index] increase by 1 
    for clause_index in lit_clause[literal_to_flip]:
        true_sat_lit[clause_index] += 1

    # get index of clauses where the negated literal to flip appears
    # in true_sat_lit[index] decrease by 1 
    for clause_index in lit_clause[-literal_to_flip]:
        true_sat_lit[clause_index] -= 1


def compute_broken(clause, true_sat_lit, lit_clause, p=0.4):
    break_min = sys.maxsize
    best_literals = []
    
    for literal in clause:
        break_score = 0
        
        # to compute the break_score of a literal, we check how many clauses where the negated literal appers has true_sat_lit = 1
        # meaning that if we flipped this variable that clause could be unsatisfied in the new solution 
        for clause_index in lit_clause[-literal]:
            if true_sat_lit[clause_index] == 1:
                break_score += 1
        
        # update the best break_score and save its corresponding literal
        if break_score < break_min:
            break_min = break_score
            best_literals = [literal]
        elif break_score == break_min:
            best_literals.append(literal)

    # with a probability of p, choose a random literal from the unsatisfied clause to flip if the break_min is not 0 
    if break_min != 0 and random.random() < p:
        best_literals = clause

    # return a random literal of the list
    return random.choice(best_literals)


def walksat(clauses, num_vars, lit_clause, max_flips_proportion=4):
    max_flips = num_vars * max_flips_proportion

    while 1:
        interpretation = get_random_interpretation(num_vars)
        
        true_sat_lit = get_true_sat_lit(clauses, interpretation)
        
        for _ in range(max_flips):
            unsat_clauses_index = [index for index, true_lit in enumerate(true_sat_lit) if not true_lit]

            if not unsat_clauses_index:
                return interpretation

            clause_index = random.choice(unsat_clauses_index)
            unsatisfied_clause = clauses[clause_index]

            lit_to_flip = compute_broken(unsatisfied_clause, true_sat_lit, lit_clause)

            update_tsl(lit_to_flip, true_sat_lit, lit_clause)

            interpretation[abs(lit_to_flip)] *= -1


def print_results(solution):
    print('s SATISFIABLE')
    print('v ' + ' '.join(map(str, solution[1:])) + ' 0')


clauses, num_vars, lit_clause = read_file(sys.argv[1])
solution = walksat(clauses, num_vars, lit_clause)
print_results(solution)