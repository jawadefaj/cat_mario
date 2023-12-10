# calculate the adjusted fitness, decide the proportion of removed
# genomes in each species and allocate each new_born genomes
# species(could be a new one)
import numpy as np

# compatibility parameters
COEFF_EXC = 0.3
COEFF_DIS = 0.4
COEFF_W = 0.3
COMP_TH = 3.0

def get_species_sizes(species):
	l_species_size = []
	for s in species:
		l_species_size.append(len(s))
	return l_species_size


def adjusted_n_total_fitness(species):
	spec_ajusted_fitness_tuples = []  # list of list of adjusted fitness
	spec_mean_fitness = []
	for spec_id, species in enumerate(species):
		size = len(species)
		l_adjusted_fitness_tuples = []
		spec_fitness_sum = 0
		for genome in species:
			spec_fitness_sum += genome.fitness
			adjusted_fitness = genome.fitness/size
			# tuple format is here:
			adjusted_fitness_tuple = (adjusted_fitness, spec_id, genome)

			l_adjusted_fitness_tuples.append(adjusted_fitness_tuple)
		spec_ajusted_fitness_tuples.append(l_adjusted_fitness_tuples)
		# species fitness = mean fitness of species'genomes
		spec_mean_fitness.append(spec_fitness_sum / size)
	return spec_ajusted_fitness_tuples, spec_mean_fitness


def keep_top(spec_adjusted_fitness_tuples, n_top_keep):
	kill_candidates = []
	for spec in spec_adjusted_fitness_tuples:
		spec.sort(reverse=True)
		while len(spec) > n_top_keep:
			kill_candidates.append(spec.pop())
	return kill_candidates


def kill_worst_genomes(spec_adjusted_fitness_tuples, n_top_keep, n_kill):
	# the n_top_keep has priority when killing quota is not met
	species_sizes = get_species_sizes(spec_adjusted_fitness_tuples)
	species_number = len(species_sizes)
	pop_size = sum(species_sizes)
	kill_candidates = keep_top(spec_adjusted_fitness_tuples, n_top_keep)
	if pop_size - n_top_keep * species_number <= n_kill:
		return spec_adjusted_fitness_tuples
	else:
		kill_candidates.sort(reverse=True)
		while n_kill > 0:
			kill_candidates.pop()
			n_kill -= 1
		# ‘go home' to their own species
		for genome_tuple in kill_candidates:
			species_id = genome_tuple[1]
			spec_adjusted_fitness_tuples[species_id].append(genome_tuple)
		# extract the genomes for species list
		return spec_adjusted_fitness_tuples


def remove_n_baby_quota(species, n_top_keep, n_kill):
	species_sizes = get_species_sizes(species)
	pop_size = sum(species_sizes)
	spec_adjusted_fitness_tuples, spec_mean_fitness = adjusted_n_total_fitness(species)
	new_species_tuple = kill_worst_genomes(spec_adjusted_fitness_tuples, n_top_keep, n_kill)

	n_baby = pop_size - sum(get_species_sizes(new_species_tuple))
	mean_fitness_sum = sum(spec_mean_fitness)
	baby_proportion = np.array(spec_mean_fitness) / mean_fitness_sum
	baby_quota = np.floor(baby_proportion * n_baby)

	# assign the number loss by floor in the order of total fitness of species
	baby_assigned = np.sum(baby_quota)
	if baby_assigned < n_baby:
		id_spec_fitness_pair = []
		for spec_i, mean_fitness in enumerate(spec_mean_fitness):
			# the spec_fitness here should be mean not total
			id_spec_fitness_pair.append((spec_i, mean_fitness))
		id_spec_fitness_pair.sort(key=lambda x: x[1])
		index = 0
		while baby_assigned < n_baby:
			assign_id = id_spec_fitness_pair[index][0]
			baby_quota[assign_id] += 1
			baby_assigned += 1
			index += 1

	l_baby_quota = [int(quota) for quota in baby_quota.tolist()]

	return new_species_tuple, l_baby_quota

#----------------------------------------------------------------------------


def calculate_compatibility(n_disjoint, n_excess, mean_w_diff):
	return n_disjoint * COEFF_DIS + n_excess * COEFF_EXC + mean_w_diff * COEFF_W


def is_compatible(genome, spec_represent):
	n_excess = 0
	n_disjoint = 0
	long_weight_sum = 0
	short_weight_sum = 0
	if genome.genes[-1].conn_inno >= spec_represent.genes[-1].conn_inno:
		long_genome = genome
		short_genome = spec_represent
	else:
		long_genome = spec_represent
		short_genome = genome
	i, j = 0, 0
	long_genes = long_genome.genes
	short_genes = short_genome.genes
	excess_th = short_genes[-1].conn_inno
	while i < len(long_genes) and j <= len(short_genes):
		long_gene = long_genes[i]
		long_inno = long_gene.conn_inno
		long_weight = long_gene.weight
		if j == len(short_genes):
			if long_inno < excess_th:
				n_disjoint += 1
			elif long_inno > excess_th:
				n_excess += 1
			# doesn't do anything when they have same inno
			long_weight_sum += long_weight
			i += 1
			continue  # only run this block when j == len(short_genome)

		while j < len(short_genes) and short_genes[j].conn_inno < long_inno:
			short_weight_sum += short_genes[j].weight
			j += 1
			n_disjoint += 1

		if j == len(short_genes):
			continue  # leave the problem to the next loop, enter iterate-i-only state

		# now short_gene's inno >= long_gene's inno
		if long_inno == short_genes[j].conn_inno:
			long_weight_sum += long_weight
			i += 1
			short_weight_sum += short_genes[j].weight
			j += 1
		else:
			long_weight_sum += long_weight
			i += 1
			n_disjoint += 1
	mean_w_diff = abs(short_weight_sum / len(short_genes) - long_weight_sum / len(long_genes))
	if calculate_compatibility(n_disjoint, n_excess, mean_w_diff) <= COMP_TH:
		return True
	else:
		return False


def respeciate(offspring, species):
	new_species = []
	assigned = False
	for genome in offspring:
		for spec in species:
			spec_represent = spec[0]
			if is_compatible(genome, spec_represent):
				spec.append(genome)
				assigned = True
				break
		if not assigned:
			new_species.append([genome])
		assigned = False
	species += new_species
