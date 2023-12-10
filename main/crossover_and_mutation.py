from neat_core import Genome
from neat_core import Gene
import random
import numpy as np

P_W_MUTATION = 0.5
P_ADD_NODE = 0.5
P_ADD_CONN = 1 - P_ADD_NODE
assert(P_W_MUTATION < 1)
W_MUTATE_MEAN = 0
W_MUTATE_STD = 1
W_MUTATE_RATE = 0.5


def weight_mutate(new_species):
	from neat_core import Neat
	for spec in new_species:
		for genome in spec:
			for gene in genome.genes:
				if random.random() <= 0.5:
					new_weight = gene.weight + np.random.normal(W_MUTATE_MEAN, W_MUTATE_STD)
					if new_weight > Neat.WEIGHT_MAX:
						gene.weight = Neat.WEIGHT_MAX
					elif new_weight < Neat.WEIGHT_MIN:
						gene.weight = Neat.WEIGHT_MIN
					else:
						gene.weight = new_weight


def get_crossover_list(parents_tuples, n_parents):
	l_parents = []
	for i in range(n_parents):
		for j in range(i + 1, n_parents):
			parent_1 = parents_tuples[i][2]
			parent_2 = parents_tuples[j][2]
			parent_1_fitness = parents_tuples[i][0]
			parent_2_fitness = parents_tuples[j][0]
			sum_fitness = parents_tuples[i][0] + parents_tuples[j][0]
			same_fitness = bool(parent_1_fitness == parent_2_fitness)
			l_parents.append((sum_fitness, (parent_1, parent_2, same_fitness)))
	l_parents.sort(reverse=True)
	return l_parents


def crossover(genome_1, genome_2, same_fitness):
	# by the way we pick parents, genome_1 always has larger or equal fitness
	new_genes = []
	genes_1 = genome_1.genes
	genes_2 = genome_2.genes
	i, j = 0, 0
	while i < len(genes_1) and j < len(genes_2):
		gene_1 = genes_1[i]
		conn_inno_1 =gene_1.conn_inno
		while j < len(genes_2) and genes_2[j].conn_inno < conn_inno_1:
			if same_fitness:
				new_genes.append(genes_2[j])
			j += 1
		if genes_2[j].conn_inno == conn_inno_1:
			if random.random() <= 0.5:
				new_genes.append(gene_1)
			else:
				new_genes.append(genes_2[j])
			i += 1
			j += 1
		else:
			new_genes.append(gene_1)
			i += 1
	if i < len(genes_1):
		new_genes += genes_1[i:]
	if same_fitness and j < len(genes_2):
		new_genes += genes_2[j:]

	new_genome = Genome(new_genes)
	return new_genome

def insert_new_gene(new_gene, genes):
	start = 0
	end = len(genes) - 1
	while start + 1 < end:
		mid = (start + end) // 2
		gene = genes[mid]
		if gene.conn_inno <= new_gene.conn_inno:
			start = mid
		else:
			end = mid
	if start == 0:
		genes.insert(0, new_gene)
	elif end == len(l) - 1:
		genes.append(new_gene)
	else:
		gens.insert(start + 1, new_gene)

def add_node_mutate(genome):
	# from neat_core.Neat import node_inno_nums
	# from neat_core.Neat import bias_weight
	from neat_core import Neat


	new_genes = genome.genes[:]
	active_genes = [gene for gene in genome.genes if not gene.disabled]
	random_i = random.randint(0, len(active_genes) - 1)
	mutate_gene = active_genes[random_i]
	old_conn = mutate_gene.connection # old_conn is the pair for the key of new_node as well
	from_node, to_node = old_conn
	update_inno_nums = False
	if Neat.node_inno_nums.get(old_conn):
		# then we don't need to find the connections as they are definitely created
		new_node_inno = Neat.node_inno_nums[old_conn]
	else:
		# we can't find the new node so update the node/conn innovation numbers first
		new_node_inno = len(Neat.node_inno_nums) # innovation number for new node
		Neat.node_inno_nums[old_conn] = new_node_inno
		conn_inno_size = len(Neat.conn_inno_nums)
		Neat.conn_inno_nums[(new_node_inno, to_node)] = conn_inno_size
		Neat.conn_inno_nums[(from_node, new_node_inno)] = conn_inno_size + 1
		update_inno_nums = True

		weight_tuples = (Neat.WEIGHT_MIN, Neat.WEIGHT_MAX, Neat.WEIGHT_MEAN, Neat.WEIGHT_DEVIATION)
		Neat.bias_weight[new_node_inno] = Neat.randomize_weight(weight_tuples)
	conn_1, w_1 = (from_node, new_node_inno), 1
	conn_2, w_2 = (new_node_inno, to_node), mutate_gene.weight
	new_gene_1 = Gene(conn_1, w_1)
	new_gene_2 = Gene(conn_2, w_2)
	if update_inno_nums:
		new_genes.append(new_gene_1)
		new_genes.append(new_gene_2)
	else:
		# use binary search to find place for these two genes(order by inno_num)
		insert_new_gene(new_gene_1, new_genes)
		insert_new_gene(new_gene_2, new_genes)
	new_genome = Genome(new_genes)
	return new_genome

def add_conn_mutate(genome):
	# from neat_core.Neat import randomize_weight
	# from neat_core.Neat import conn_inno_nums
	from neat_core import Neat
	weight_tuples = (Neat.WEIGHT_MIN, Neat.WEIGHT_MAX, Neat.WEIGHT_MEAN, Neat.WEIGHT_DEVIATION)

	new_genes = genome.genes[:]
	active_connections = [gene.connection for gene in genome.genes if not gene.disabled]
	disabled_connections = [gene.connection for gene in genome.genes if gene.disabled]
	active_connections_set = set(active_connections)
	while True:
		from_node_1, to_node_1 = random.choice(active_connections)
		from_node_2, to_node_2 = random.choice(active_connections)
		if (from_node_1, to_node_2) not in active_connections_set:
			new_connection = (from_node_1, to_node_2)
			break
		if (from_node_2, to_node_1) not in active_connections_set:
			new_connection = (from_node_2, to_node_1)
			break
	if new_connection in disabled_connections:
		for gene in new_genes:
			if gene.connection == new_connection:
				gene.disabled = False

				gene.weight = Neat.randomize_weight(weight_tuples)
				break
	else:
		update_inno_num = False
		if not Neat.conn_inno_nums.get(new_connection):
			new_conn_inno = len(Neat.conn_inno_nums)
			Neat.conn_inno_nums[new_connection] = new_conn_inno
			update_inno_num = True
		new_gene = Gene(new_connection)
		if update_inno_num:
			new_genes.append(new_gene)
		else:
			insert_new_gene(new_genes, new_gene)
	return new_genes

def structure_mutate(genome):
	if random.random() < P_ADD_NODE:
		new_genome = add_node_mutate(genome)
	else:
		new_genome = add_conn_mutate(genome)
	return new_genome


def mutation_loop(parents_tuples, n_baby, spec_offsprings):
	# it changes spec_offspring so doesn't return anything
	n_parent = len(parents_tuples)
	for i in range(n_baby):
		parent_index = n_baby % n_parent
		parent_genome = parents_tuples[parent_index][2]
		spec_offsprings.append(structure_mutate(parent_genome))


def mutate_and_crossover(parents_tuples, n_baby):

	# this function is an algorithm decision so I write a function for possible future change
	def get_probability_mutation(rank):
		# rank starts from 0
		probability = 0.1 * rank if rank < 10 else 1
		return probability

	# notice that parents are already ordered in keep_top function
	spec_offsprings = []
	n_parents = len(parents_tuples)
		# we prefer crossover over pure mutation
	if n_parents >= 2:
		l_parents = get_crossover_list(parents_tuples, n_parents)
		n_parents_pair = len(l_parents)
		print(n_parents_pair)
		print(n_baby)
		loop_stop_point = min(n_parents_pair, n_baby)
		print(loop_stop_point)
		for k in range(loop_stop_point):
			probability_mutation = get_probability_mutation(k)
			parent_1, parent_2, same_fitness = l_parents[k][1]  # parents are genomes here
			offspring = crossover(parent_1, parent_2, same_fitness)
			if random.random() < probability_mutation:
				offspring = structure_mutate(offspring)
			spec_offsprings.append(offspring)

			if n_parents_pair < n_baby:
				n_baby -= n_parents_pair
				mutation_loop(parents_tuples, n_baby, spec_offsprings)
	else:
		# only one parent
		mutation_loop(parents_tuples, n_baby, spec_offsprings)
	return spec_offsprings


def extract_genomes_from_tuple(spec_adjusted_fitness_tuples):
	new_species = []
	for spec in spec_adjusted_fitness_tuples:
		l_genomes = []
		for genome_tuple in spec:
			genome = genome_tuple[2]
			l_genomes.append(genome)
		new_species.append(l_genomes)
	return new_species

def produce_offsprings(new_species_tuple, baby_quota):
	offsprings = []
	n = len(new_species_tuple)
	for i in range(n):
		spec_tuple = new_species_tuple[i]
		n_baby = baby_quota[i]
		spec_offsprings = mutate_and_crossover(spec_tuple, n_baby)
		offsprings += spec_offsprings
	return offsprings
