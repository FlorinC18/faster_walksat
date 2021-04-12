#!/usr/bin/python3

# Algorith made by:
#   Florin Camara
#   Pau Taló López

# walksat implementation: FiaauunSat
# name origin: faster than Francesco Virgolinii meme: https://www.youtube.com/watch?v=iE3kD4X_Fwg


import random
import sys

# -------------------------------- VARIABLES EXPLANATION --------------------------------
# lit_clause: 
#   type: list (length = num_vars * 2 + 1)
#   description: each position corresponds to a literal and contains the index of the clauses in the problem where that literal appears:
#                   - position 0 will always be empty,
#                   - positions from 1 to num_vars corresponds to the positive literals of the problem
#                   - positions from num_vars + 1 to end corresponds to the negative literals of the problem in reverse order
#   example: 
#       num_vars = 2
#       lit_clause : [[],[clauses index where lit 1 appears],[clauses index where lit 2 appears],[clauses index where lit -2 appears],[clauses index where lit -1 appears]]
# 
# true_sat_lit:
#   type: list (length = number of clauses of the problem)
#   description: given a model M, each position contains the number of literals satisfied by M of the corresponding clause in the problem
#   example:
#       model: 1 2 3
#       problem file:               true_sat_lit:
#           p cnf 3 3
#           1 -3 2 0                    2
#           1 -2 3 0                    2
#           2 -1 3 0                    2
# ---------------------------------------------------------------------------------------

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
            for lit in line[:-2].split():
                lit = int(lit)
                clause.append(lit)
                lit_clause[lit].append(count)

            clauses.append(clause)
            count += 1

    return clauses, num_vars, lit_clause


def get_random_model(num_vars):
    # generate a list with random positive and negative values for each variable in the problem 
    # note that lenth of the list is num_vars + 1, so variable 1 corresponds to position 1 in the list
    return [i if random.random() < 0.5 else -i for i in range(num_vars + 1)]


def get_true_sat_lit(clauses, model):
    # given a model, for each clause of the problem check how many literals satisfy that clause
    # returns a list with the length of the clauses in the problem, where each position stores the satisfied literals of the clause 
    # index of this list = index of clause from the problem -> true_sat_lit[0] = clauses[0]
    true_sat_lit = [0] * len(clauses) # [0 for _ in clauses]

    for index, clause in enumerate(clauses):
        for lit in clause:
            if model[abs(lit)] == lit:
                true_sat_lit[index] += 1

    return true_sat_lit


def update_tsl(lit_to_flip, true_sat_lit, lit_clause):
    # get index of clauses where the literal to flip appears
    # in true_sat_lit[index] increase by 1 
    for clause_index in lit_clause[lit_to_flip]:
        true_sat_lit[clause_index] += 1

    # get index of clauses where the negated literal to flip appears
    # in true_sat_lit[index] decrease by 1 
    for clause_index in lit_clause[-lit_to_flip]:
        true_sat_lit[clause_index] -= 1


def compute_broken(clause, true_sat_lit, lit_clause, p=0.4):
    break_min = sys.maxsize
    best_lits = []
    
    for lit in clause:
        break_score = 0
        
        # to compute the break_score of a literal, we check how many clauses where the negated literal appers has true_sat_lit = 1
        # meaning that if we flipped this variable that clause could be unsatisfied in the new solution 
        for clause_index in lit_clause[-lit]:
            if true_sat_lit[clause_index] == 1:
                break_score += 1
        
        # update the best break_score and save its corresponding literal
        if break_score < break_min:
            break_min = break_score
            best_lits = [lit]
        elif break_score == break_min:
            best_lits.append(lit)

    # with a probability of p, choose a random literal from the unsatisfied clause to flip if the break_min is not 0 
    if break_min != 0 and random.random() < p:
        best_lits = clause

    # return a random literal of the list
    return random.choice(best_lits)


def walksat(clauses, num_vars, lit_clause, flips_proportion=4):
    max_flips = num_vars * flips_proportion

    while 1:
        model = get_random_model(num_vars)
        
        true_sat_lit = get_true_sat_lit(clauses, model)
        
        for _ in range(max_flips):
            unsat_clauses_index = [index for index, true_lit in enumerate(true_sat_lit) if not true_lit]

            if not unsat_clauses_index:
                return model

            clause_index = random.choice(unsat_clauses_index)
            unsatisfied_clause = clauses[clause_index]

            lit_to_flip = compute_broken(unsatisfied_clause, true_sat_lit, lit_clause)

            update_tsl(lit_to_flip, true_sat_lit, lit_clause)

            model[abs(lit_to_flip)] *= -1


def print_results(solution):
    print('s SATISFIABLE')
    print('v ' + ' '.join(map(str, solution[1:])) + ' 0')


clauses, num_vars, lit_clause = read_file(sys.argv[1])
solution = walksat(clauses, num_vars, lit_clause)
print_results(solution)