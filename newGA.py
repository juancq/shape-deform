import operator
import math
import random
import gplib
from deap import base, creator, gp, tools

def clean_expr(expr):
    expr = expr.replace('add', '+')
    expr = expr.replace('mul', '*')
    expr = expr.replace('sub', '-')
    expr = expr.replace('neg', '-')
    expr = expr.replace('protectedDiv', '/')
    expr = expr.replace('mod', '%')
    return expr

def protectedDiv(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 1

pset = gplib.PrimitiveSet("MAIN", arity=4)
pset.addEphemeralConstant("rand101a", lambda: random.uniform(-1,1))
pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(operator.neg, 1)
pset.addPrimitive(protectedDiv, 2)
pset.addPrimitive(math.cos, 1)
pset.addPrimitive(math.sin, 1)
pset.addPrimitive(math.sqrt, 1)
pset.addPrimitive(math.floor, 1)
pset.addPrimitive(math.ceil, 1)

pset.renameArguments(ARG0='x')
pset.renameArguments(ARG1='y')
pset.renameArguments(ARG2='z')
pset.renameArguments(ARG3='time')

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gplib.PrimitiveTree, fitness=creator.FitnessMin, pset=pset)

toolbox = base.Toolbox()
toolbox.register("expr", gplib.genHalfAndHalf, pset=pset, min_=1, max_=2)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutUniform", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
toolbox.register("nodeReplacement", gp.mutNodeReplacement, pset=pset)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

class newGA:

    def __init__(self):

        self.population = None

    def start(self, size):

        self.population = toolbox.population(n=size)

    def mutate(self, selection):

        selected = self.population[selection]
        offspring = [toolbox.clone(selected) for _ in range(len(self.population))]

        for i in range(1, len(offspring)):
            # add more mutations here
            if random.random() < 0.5:
                offspring[i], = toolbox.mutUniform(offspring[i])
            else:
                offspring[i], = toolbox.nodeReplacement(offspring[i])

        self.population = offspring

        #return toolbox.mutate(self.population[selection])

    def get_expressions(self):
        exprs = [clean_expr(ind.js_str()) for ind in self.population]
        return exprs

