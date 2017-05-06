import sys
import operator
import math
import random
import numpy as np
from deap import base
from deap import creator
from deap import tools
from deap import gp
from deap import algorithms
import gplib

# Define new functions
#----------------------------#
def protectedDiv(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 1

#----------------------------#
def compile(expr, pset):
    """Compile the expression *expr*.
    :param expr: Expression to compile. It can either be a PrimitiveTree,
                 a string of Python code or any object that when
                 converted into string produced a valid Python code
                 expression.
    :param pset: Primitive set against which the expression is compile.
    :returns: a function if the primitive set has 1 or more arguments,
              or return the results produced by evaluating the tree.
    """
    code = str(expr)
    if len(pset.arguments) > 0:
        # This section is a stripped version of the lambdify
        # function of SymPy 0.6.6.
        #print code
        args = ",".join(arg for arg in pset.arguments)
        code = "lambda {args}: {code}".format(args=args, code=code)
        #print '#####################################'
        #print args
        #print code
    try:
        return eval(code, pset.context, {})
    except MemoryError:
        _, _, traceback = sys.exc_info()
        raise MemoryError, ("DEAP : Error in tree evaluation :"
                            " Python cannot evaluate a tree higher than 90. "
                            "To avoid this problem, you should use bloat control on your "
                            "operators. See the DEAP documentation for more information. "
                            "DEAP will now abort."), traceback

#----------------------------#
pset = gplib.PrimitiveSet("MAIN", 4)
pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(protectedDiv, 2)
pset.addPrimitive(operator.neg, 1)
pset.addPrimitive(math.cos, 1)
pset.addPrimitive(math.sin, 1)
#pset.addPrimitive(math.pow, 2)
#pset.addPrimitive(operator.mod, 2)
pset.addPrimitive(math.sqrt, 1)
pset.addPrimitive(math.floor, 1)
pset.addPrimitive(math.ceil, 1)
pset.addEphemeralConstant("rand101", lambda: random.uniform(-1,1))
pset.renameArguments(ARG0='x')
pset.renameArguments(ARG1='y')
pset.renameArguments(ARG2='z')
pset.renameArguments(ARG3='time')

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gplib.PrimitiveTree, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("expr", gplib.genHalfAndHalf, pset=pset, min_=1, max_=4)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
#toolbox.register("compile", gp.compile, pset=pset)
toolbox.register("compile", compile, pset=pset)

#samples = [np.linspace(-10, 10, 1000) for i in range(3)]
samples = [np.linspace(-20, 20, 10000), np.linspace(0, 100, 1000)]

vpoints = np.linspace(-10, 10, 1000)
time_samples = np.linspace(0, 10, 20)


#--------------------------------------#
def evalEquation(individual, points, best_func):
    # Transform the tree expression in a callable function
    func = toolbox.compile(expr=individual)
    # Evaluate the mean squared error between the expression
    # and the real function : x**4 + x**3 + x**2 + x
    errors = 0.
    try:
        for x, time in zip(points[0], points[1]):
            #print x, time
            errors += (func(x, x, x, time) - best_func(x, x, x, time))**2
    except:
        print 'value error in function'
        errors = 100000.

    return errors / len(points),

#--------------------------------------#
def evalEquation_timeintervals(individual, points, time, best_func):
    # Transform the tree expression in a callable function
    func = toolbox.compile(expr=individual)
    # Evaluate the mean squared error between the expression
    # and the real function : x**4 + x**3 + x**2 + x
    errors = 0.
    try:
        for t in time:
            error_arr = [(func(x, x, x, t) - best_func(x, x, x, t))**2 for x in points]
            errors += math.fsum(error_arr)
    except:
        print 'value error in function'
        errors = 100000.

    return errors / len(points),

#def evalSymbReg(individual, points):
#    # Transform the tree expression in a callable function
#    func = toolbox.compile(expr=individual)
#    # Evaluate the mean squared error between the expression
#    # and the real function : x**4 + x**3 + x**2 + x
#    sqerrors = ((func(x, y, z, w) - best_func)**2 for x in points)
#    return math.fsum(sqerrors) / len(points),

#toolbox.register("evaluate", evalSymbReg, points=[x/10. for x in range(-10,10)])
toolbox.register("evaluate", evalEquation, points=samples)
toolbox.register("evaluate", evalEquation_timeintervals, points=vpoints, time=time_samples)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))


#--------------------------------------#
class Container:

    def __init__(self):

        self.subset_size = None
        self.population = None
        self.subset = None
        self.gen = 0
        self.cxpb = 0.5
        self.mutpb = 0.10

        self.popsize = 100
        self.subset_size = 9

#----------------------------#
    def on_start(self, popsize, subset_size):
        self.popsize = popsize
        self.subset_size = subset_size

        self.population = toolbox.population(n=popsize)
        
#----------------------------#
    def clean_expr(self, expr):
        expr = expr.replace('add', '+')
        expr = expr.replace('mul', '*')
        expr = expr.replace('sub', '-')
        expr = expr.replace('neg', '-')
        expr = expr.replace('protectedDiv', '/')
        expr = expr.replace('mod', '%')
        return expr

#----------------------------#
    def pre_process(self, sample):

        exprs = [self.clean_expr(ind.js_str()) for ind in sample]
        #exprs = [ind.js_str() for ind in sample]

        return exprs

#----------------------------#
    def random_subset(self):
        #return random.sample(self.population, self.subset_size)
        return tools.selRandom(self.population, self.subset_size)

#----------------------------#
    def get_subset(self):
        if self.population:

            # random selection
            #sample = tools.selRandom(self.population, self.subset_size)

            # best selection
            #sample = tools.selBest(self.population, self.subset_size)

            # worst selection
            #sample = tools.selWorst(self.population, self.subset_size)

            # bestish selection
            sample = tools.selTournament(self.population, self.subset_size, 3)

            self.subset = sample
            sample = self.pre_process(sample)
        else: 
            sample = self.get_default()


        return sample

#----------------------------#
    def get_default(self):
        shader = '''
            uniform float time;

            void main() {
                vec3 newPos = position;// - cos(time * -3.0);
                gl_Position = projectionMatrix * modelViewMatrix * vec4(newPos, 1.0);
            }
        '''


        result = {}
        for i in range(self.subset_size):
            result[str(i)] = shader

        #return result

        return [shader for i in range(self.subset_size)]

#----------------------------#
    def evaluate(self, pop, best):

        best_func = toolbox.compile(expr=best)
        fitnesses = [toolbox.evaluate(ind, best_func=best_func) for ind in pop]
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
        

#----------------------------#
    def iga_step(self, selection):

        self.gen += 1

        best = self.subset[selection]

        self.evaluate(self.population, best)

        offspring = toolbox.select(self.population, len(self.population))
        offspring = algorithms.varAnd(offspring, toolbox, self.cxpb, self.mutpb)
        self.evaluate(offspring, best)
        self.population[:] = offspring
#----------------------------#
