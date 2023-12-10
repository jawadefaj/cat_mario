import numpy as np


# def randomize_weight():
# 	weight = np.random.normal(Neat.WEIGHT_MEAN, Neat.WEIGHT_DEVIATION)
# 	if weight > Neat.WEIGHT_MAX:
# 		return Neat.WEIGHT_MAX
# 	if weight < Neat.WEIGHT_MIN:
# 		return Neat.WEIGHT_MIN
# 	return weight

class Neat:

	INPUT_NUM = 169
	OUTPUT_NUM = 4
	generation = 1

	##-----------parametres for weight generation--------##
	WEIGHT_MAX = 10
	WEIGHT_MIN = -10
	WEIGHT_MEAN = 0
	WEIGHT_DEVIATION = 4
	##-----------parametres for weight generation--------##	

	max_node_inno = INPUT_NUM + OUTPUT_NUM - 1
	max_conn_inno = OUTPUT_NUM * INPUT_NUM - 1

	def randomize_weight(weight_tuples):
		weight_min, weight_max, weight_mean, weight_dev = weight_tuples
		weight = np.random.normal(weight_mean, weight_dev)
		if weight > weight_max:
			return weight_max
		if weight < weight_min:
			return weight_min
		return weight

	def initialize_nodes(input_num, output_num):
		# I use (a, b) to represent nodes because each new node is created
		# between two old nodes and a,b are the two old nodes that the new node
		# depends. Hence for initial nodes, I just give them (a, a) where a is
		# there node innovation number.

		# In my encoding, output nodes have innovation number 0 to 3(left, right,
		# up, down) and the input node have innovation number 4 to 172

		nodes = {}
		for i in range(input_num + output_num):
			nodes[(i, i)] = i
		return nodes

	def initialize_connections(input_num, output_num):
		# notice that the index of connections IS the innovation number
		connections = {}
		for output_node_i in range(output_num):
			for j in range(input_num):
				input_node_i = j + output_num
				connections[(input_node_i, output_node_i)] = output_node_i * output_num + j
		return connections

	def initialize_bias_weight(output_num, randomize_weight, weight_tuples):
		bias_weight = {}
		for i in range(output_num):
			bias_weight[i] = randomize_weight(weight_tuples)
		return bias_weight

	node_inno_nums = initialize_nodes(INPUT_NUM, OUTPUT_NUM)  # storing existed nodes
	conn_inno_nums = initialize_connections(INPUT_NUM, OUTPUT_NUM)  # storing existed conn
	weight_tuples = (WEIGHT_MIN, WEIGHT_MAX, WEIGHT_MEAN, WEIGHT_DEVIATION)
	bias_weight = initialize_bias_weight(OUTPUT_NUM, randomize_weight, weight_tuples)  # we don't really need bias connection, imagine we
	# have one bias node only. bias_weight[i] represent weight for bias of to_node i

	#------------class variables above-----------------------------------


	def __init__(self, max_gen, max_pop, top_n_spec, kill_off_n):
		self.MAX_GEN = max_gen
		self.MAX_POP = max_pop
		self.population = self.initialize_population()
		self.TOP_N_SPEC = top_n_spec  # how many top genomes keep in the speciation during evolution.
		self.KILL_OFF_N = kill_off_n  # how many genomes kill in each generation
		self.species = self.initialize_speciation()
		# self.dep_weight =
		assert(self.TOP_N_SPEC > 0)
		assert(self.KILL_OFF_N < self.MAX_POP)


	def initialize_population(self):
		population = []
		for i in range(self.MAX_POP):
			genome = Genome()
			population.append(genome)
		return population

	def initialize_speciation(self):

		def w_sum(genome):
			w_sum = 0
			for gene in genome.genes:
				w_sum += gene.weight
			return w_sum

		genes_size = Neat.OUTPUT_NUM * Neat.INPUT_NUM
		species = []
		spec_rep_w_sum = []
		for genome in self.population:
			if not species:
				species.append([genome])
				spec_rep_w_sum.append(w_sum(genome))
				continue
			genome_w_sum = w_sum(genome)
			assigned = False

			from speciation import COMP_TH

			for i, rep_w_sum in enumerate(spec_rep_w_sum):
				if abs((genome_w_sum - rep_w_sum) / genes_size) < COMP_TH:
					species[i].append(genome)
					assigned = True
			if not assigned:
				species.append([genome])
				spec_rep_w_sum.append(genome_w_sum)

		return species



	def evolve(self):

		def extract_genomes_from_tuple(spec_adjusted_fitness_tuples):
			new_species = []
			for spec in spec_adjusted_fitness_tuples:
				l_genomes = []
				for genome_tuple in spec:
					genome = genome_tuple[2]
					l_genomes.append(genome)
				new_species.append(l_genomes)
			return new_species

		self.species = self.pop_to_spec()

		from speciation import remove_n_baby_quota
		new_species_tuple, baby_quota = remove_n_baby_quota(self.species, self.TOP_N_SPEC, self.KILL_OFF_N)

		from crossover_and_mutation import produce_offsprings
		from crossover_and_mutation import weight_mutate

		offsprings = produce_offsprings(new_species_tuple, baby_quota)
		new_species = extract_genomes_from_tuple(new_species_tuple)

		from speciation import respeciate
		respeciate(offsprings, new_species)
		weight_mutate(new_species)
		self.species = new_species
		self.population = self.flat_list(self.species)

	def flat_list(self, list_of_list):
		result_list = []
		for list in list_of_list:
			result_list += list
		return result_list

	def pop_to_spec(self):
		new_species = []

		from speciation import get_species_sizes
		species_sizes = get_species_sizes(self.species)
		current_index = 0
		for spec_size in species_sizes:
			new_index = current_index + spec_size
			new_species.append(self.population[current_index: new_index])
			current_index = new_index
		return new_species


class Genome:

	activation = 'relu'

	def __init__(self, genes=None):
		# self.genes for easier crossover(order by innovation number)
		# self.connections for easier computing outputs, details in reorder function

		if genes:
			self.genes = genes  # after first generation
		else:
			self.genes = self.initialize_genes()  # first generation
		self.fitness = None
		self.conn_w_dict = self.genes_to_dict()  # for computing output
		# self.connections = self.reorder_connections([gene.connection for gene in self.genes])

	# def reorder_connections(self, connections):
	# 	# Todo: connections should be ordered such that the take_value_node's innovation number
	# 	# Todo:	increases e.g. (5, 0), (6, 0), (7, 1), (8, 3)....
	# 	# Todo:	keeping this structure is important for calculating output faster
	# 	return new_connections

	def genes_to_dict(self):
		conn_w_dict = {}
		for gene in self.genes:
			from_node, to_node = gene.connection
			conn_w_tuple = (gene.connection, gene.weight)
			if conn_w_dict.get(to_node):
				conn_w_dict[to_node].append(conn_w_tuple)
			else:
				conn_w_dict[to_node] = [conn_w_tuple]
		return conn_w_dict

	def activate(self, weighted_sum, activation='sigmoid'):

		def sigmoid(x):
			return 1 / (1 + np.e ** -x)

		def ReLU(x):
			return np.maximum(0.0, x)

		if activation == 'sigmoid':
			return sigmoid(weighted_sum)
		if activation == 'relu':
			return ReLU(weighted_sum)
		return weighted_sum

	def get_output(self, input_list):

		def compute_node(to_node_index, conn_w_dict, computed_node, activate):
			l_conn_w = conn_w_dict[to_node_index]
			weighted_sum = 0
			for connection, weight in l_conn_w:
				from_node, to_node = connection
				if from_node in computed_node:
					from_node_v = computed_node[from_node]
				else:
					from_node_v = compute_node(from_node, conn_w_dict, computed_node, activate)
				weighted_sum += from_node_v * weight
			weighted_sum += Neat.bias_weight[to_node_index]
			result = activate(weighted_sum, Genome.activation)
			computed_node[to_node_index] = result
			return result

		# print('input_list: {}'.format(input_list))

		computed_node = {}
		output_list = []
		# initialization
		for j in range(Neat.INPUT_NUM):
			node_index = Neat.OUTPUT_NUM + j
			computed_node[node_index] = input_list[j]
		# print('computed_node: {}'.format(computed_node))

		# compute by recursion with memoization
		for i in range(Neat.OUTPUT_NUM):
			output_list.append(compute_node(i, self.conn_w_dict, computed_node, self.activate))

		print(output_list)
		return output_list



	def initialize_genes(self):
		# for new initial genomes only, not for the ones after first generation
		""""
		:return: list of genes, 4 * 169 connections with random weights within some range
		:rtype: list of genes

		"""
		genes = []
		for to_node_n in range(Neat.OUTPUT_NUM):
			for i in range(Neat.INPUT_NUM):
				from_node_n = i + 4
				gene = Gene((from_node_n, to_node_n))
				genes.append(gene)
		return genes

	def __lt__(self, other):
		return self.fitness < other.fitness

class Gene:
	def __init__(self, connection, weight=None):
		self.connection = connection
		self.conn_inno = Neat.conn_inno_nums[connection] # assume we have checked the gene in mutation
		self.disabled = False
		if weight:
			self.weight = weight
		else:
			weight_tuples = (Neat.WEIGHT_MIN, Neat.WEIGHT_MAX, Neat.WEIGHT_MEAN, Neat.WEIGHT_DEVIATION)
			self.weight = Neat.randomize_weight(weight_tuples)


