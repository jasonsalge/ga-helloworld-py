#!/usr/bin/env python

import sys
import random
import string
import functools
import argparse
import pdb

parser = argparse.ArgumentParser(description='Genetic algorithms to match strings')
parser.add_argument('words', nargs='*', help='words in the string')
parser.add_argument('--population', dest='pop_size', type=int, action='store', default=5, help='population size')
parser.add_argument('--mutation', dest='mutate', type=float, action='store', default=0.01, help='mutation rate')
parser.add_argument('--retain', dest='retain', type=float, action='store', default=0.20, help='percentage of most fit to reproduce')
parser.add_argument('--lucky', dest='lucky', type=float, action='store', default=0.01, help='random chance for less fit to reproduce')

args = parser.parse_args()
print("ARGS is {0}".format(args))

target = ''.join(args.words) if len(args.words) else "Hello world!"

print(target)

def individual(strlen, gene_pool):
    return ''.join(random.SystemRandom().choice(gene_pool) for _ in range(strlen))

def population(count, strlen, gene_pool):
    return [ individual(strlen, gene_pool) for i in range(count) ]

def matches(accum, it):
    return accum + 1 if it[0] == it[1] else accum

def make_fitness_1(tgt):
    return lambda x: functools.reduce(matches, zip(x, tgt), 0)

fitness_fn = make_fitness_1(target)

print('{0}\t{1}'.format(target, fitness_fn(target)))

#for i in population(args.pop_size, len(target)):
    #print('{0}\t{1}'.format(i, fitness_fn(i)))

def replace_char(orig, index, new_char):
    first_part = orig[:index] if index > 0 else ''
    second_part = orig[index+1:]
    return first_part + new_char + second_part

def evolve(pop, fitness_fn, gene_pool, retain=0.2, random_select=0.5, mutate=0.01):
    
    sys_rand = random.SystemRandom()
    # http://lethain.com/genetic-algorithms-cool-name-damn-simple/
    graded = [ (fitness_fn(x), x) for x in pop]
    #pdb.set_trace()
    graded = [ x[1] for x in sorted(graded, reverse=True)]
    #pdb.set_trace()
    retain_length = int(len(graded)*retain)
    parents = graded[:retain_length]

    # randomly add other individuals to promote genetic diversity
    for individual in graded[retain_length:]:
        if random_select > sys_rand.random():
            parents.append(individual)
    
    # mutate some individuals
    for individual in parents:
        chance = sys_rand.random()
        if mutate > chance:
            individual = replace_char(individual, random.randint(0, len(individual)-1), sys_rand.choice(gene_pool))

    print ("Mutations are done")

    # crossover parents to create children
    parents_length = len(parents)
    desired_length = len(pop) - parents_length
    children = []
    while len(children) < desired_length:
        male = sys_rand.randint(0, parents_length-1)
        female = sys_rand.randint(0, parents_length-1)
        if male != female:
            male = parents[male]
            female = parents[female]
            child = ''.join(sys_rand.choice(x) for x in zip(male, female))
            #half = len(male) / 2
            #child = male[:half] + female[half:]
            children.append(child)

    parents.extend(children)
    return parents

generation = 0

ascii_gene_pool = string.ascii_letters + string.punctuation + string.digits + ' ' + string.ascii_letters + string.digits + string.ascii_letters 

pop = population(args.pop_size, len(target), ascii_gene_pool)
target_fitness = fitness_fn(target)

for i in range(100):
    pop = evolve(pop, fitness_fn, ascii_gene_pool, mutate=args.mutate, retain=args.retain, random_select=args.lucky)
    best_fitness = fitness_fn(pop[0])
    print("Generation {generation}: best='{best}' (fitness={fitness}/{target_fitness})".format(generation=i, best=pop[0], fitness=best_fitness, target_fitness=target_fitness ))
    if best_fitness == target_fitness:
        print("Target reached!")
        break

print("Done!")

