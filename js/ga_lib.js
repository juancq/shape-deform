var Gene = function(chromosome) {
    if (chromosome) this.chromosome = chromosome;
    else
        this.chromosome = [];
    this.score = 0;
};
//Gene.prototype.chromosome = []
Gene.prototype.random = function(length) {
    while (length--) {
        this.chromosome.push(Math.floor(Math.random() * 2));
    }
};

Gene.prototype.mutate = function(chance) {
    if (Math.random() > chance) return;

    var index = Math.floor(Math.random() * this.chromosome.length);
    this.chromosome[index] = 1 - this.chromosome[index];
};

Gene.prototype.mate = function(parent2) {
    var pivot = Math.floor(Math.random() * (this.chromosome.length-2)) + 1;

    var child1 = this.chromosome.slice(0, pivot).concat(parent2.chromosome.slice(pivot));
    var child2 = parent2.chromosome.slice(0, pivot).concat(this.chromosome.slice(pivot));
    return [new Gene(child1), new Gene(child2)];
};
Gene.prototype.fitness = function() {
    /*
    var total = 0;
    for (i = 0; i < this.chromosome.length; i++) {
        total += this.chromosome[i];
    }
    this.score = total;
    */

    //this.score = this.chromosome.reduce(function(a, b) { return a + b; }, 0);
    this.score = 0;
};

//var Population = function(goal, size) {
var Population = function(params) {
    this.members = [];
    this.goal = "";
    this.generationNumber = 0;
    this.size = params.size;
    this.xoRate = params.xoRate;
    this.mutRate = params.xoRate;
    this.generations = params.generations;
    this.fitness = params.fitness;
    var i = params.size;
    while (i--) {
        var gene = new Gene();
        gene.random(params.length);
        this.members.push(gene);
    }
};


Population.prototype.sort = function() {
    this.members.sort(function(a, b) {
        return a.score - b.score;
    });
};

Population.prototype.selectParent = function(totalFitness) {
    var pick = Math.random() * totalFitness;

    var roulette = 0;
    for (var i = 0; i < this.members.length; i++)
    {
        roulette += this.members[i].score;
        if (roulette >= pick) {
            return i;
        }
    }
    return this.members.length-1;
};

Population.prototype.selection = function() {

    var totalFitness = this.members.reduce(function(a, b){ return a + b.score; }, 0);

    var newPop = [];
    var N = this.members.length / 2;
    for (var i = 0; i < N; ++i)
    {
        var parent1 = this.selectParent();
        var parent2 = this.selectParent();
        var children = this.members[parent1].mate(this.members[parent2]);
        newPop.push(children[0], children[1]);
    }

    return newPop;
};

Population.prototype.stats = function() {
    var len = this.members.length;
    var best = this.members[len-1].score;
    var avg = this.members.reduce(function(a, b) { return a + b.score; }, 0);
    avg /= len;
    return {best: best, avg: avg};
};

Population.prototype.getSample = function(N) {
    N = typeof N !== 'undefined' ? N: 1;
    this.selectedSize = N;

    //var ret = this.getBest(N);
    var ret = this.getRandom(N);
    this.sampleIndexes = ret[0];
    this.sample = ret[1];
    return this.sample;
};

Population.prototype.getBest = function(N) {
    var indexes = [];
    for (var i = 0; i < N; ++i){
        indexes.push(this.size - N - i);
    }
    return [indexes, this.members.slice(this.size - N)];
};

Population.prototype.getRandom = function(N) {
    var indexes = [];
    var inds = [];
    var index;
    for (var i = 0; i < N; ++i)
    {
        index = Math.floor(Math.random() * this.size) + 1;
        indexes.push(index);
        inds.push(this.members[index]);
    }
    return [indexes, inds];
};

Population.prototype.fitnessIga = function(individual, best) 
{
    var score = 0.0;
    for (var i = 0; i < individual.chromosome.length; ++i)
    {
        score += individual.chromosome[i] == best.chromosome[i] ? 1 : 0;
    }
    individual.score = score;
};

Population.prototype.stepIga = function(bestIndex) {

    // get best individual
    var index = this.sampleIndexes[bestIndex];
    this.best = this.members[index];

    for (var i = 0; i < this.members.length; i++) {
        this.fitnessIga(this.members[i], this.best);
    }

    this.sort();

    var newPop = this.selection();
    this.members = newPop;

    for (var i = 0; i < this.members.length; i++) {
        this.members[i].mutate(this.xoRate);
        this.fitnessIga(this.members[i], this.best);
    }
    this.generationNumber++;

};

Population.prototype.step = function() {
    for (var i = 0; i < this.members.length; i++) {
        this.fitness(this.members[i]);
    }

    this.sort();

    var newPop = this.selection();
    this.members = newPop;

    for (var i = 0; i < this.members.length; i++) {
        this.members[i].mutate(this.xoRate);
        this.fitness(this.members[i]);
    }
    this.generationNumber++;
};
    
Population.prototype.generation = function() {
    for (var i = 0; i < this.members.length; i++) {
        //this.members[i].fitness();
        this.fitness(this.members[i]);
    }

    this.sort();

    var newPop = this.selection();
    this.members = newPop;

    for (var i = 0; i < this.members.length; i++) {
        this.members[i].mutate(this.xoRate);
        this.fitness(this.members[i]);
    }
    this.generationNumber++;

};

