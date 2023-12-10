# import neat
from game_running_howard import run_game
from game_running_howard import start_game
import time
import log
import genome_analysis

# DO NOT remove the two program names here, comment out the one you don't need

# PROGRAM_NAME = 'Syobon Action (??????????)'
PROGRAM_NAME = 'Syobon Action (しょぼんのアクション)'


def eval_genomes(genomes, config):
	for genome_id, genome in genomes:
		network = neat.nn.FeedForwardNetwork.create(genome, config)
		genome.fitness = run_game(PROGRAM_NAME, network)


def run_library(config_file='config'):
	start_game()
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
						 neat.DefaultSpeciesSet, neat.DefaultStagnation,
						 config_file)

	population = neat.Population(config)

	# Run for up to n generations.
	winner = population.run(eval_genomes, 2)


	winner_net = neat.nn.FeedForwardNetwork.create(winner, config)


# def load_parameters(config_file_name):
# 	"""
#
# 	:param config_file_name: filename
# 	:type config_file_name: str
# 	:return: parameters
# 	:rtype: dict
# 	"""
#
# 	return parameters


from neat_core import Neat


def run_non_library():
	start_game()
	# time.sleep(2.0)

	# #todo: we need to find a way to load parameters
	# parameters = load_parameters(config_file_name)
	max_gen = 3
	max_pop = 5
	top_n_spec = 2
	kill_off_n = 3

	n = Neat(max_gen, max_pop, top_n_spec, kill_off_n)

	# csv_folder_name = genome_analysis.create_folder()
	# l_row_csv = []
	log_filename = log.create_file()
	while n.generation < n.MAX_GEN:
		index = 0
		# l_row_csv.append([index + 1])
		time.sleep(1.0)
		max_fitness = 0
		total_fitness = 0
		for genome in n.population:
			print(index + 1)
			time.sleep(1.0)
			fitness = run_game(PROGRAM_NAME, genome, False)
			genome.fitness = fitness
			# l_row_csv[index].append(fitness)
			log.log_csv(log_filename, n.generation, index + 1, int(fitness), 0, 0)
			max_fitness = max(fitness, max_fitness)
			total_fitness += fitness
			index += 1
		mean_fitness = total_fitness / max_pop
		# l_row_csv[index].append(mean_fitness)
		# l_row_csv[index].append(max_fitness)

		log.log_csv(log_filename, n.generation, 0, 0, int(max_fitness), int(mean_fitness))
		n.evolve()
		n.generation += 1

	# csv_writer_reader.write_csv(l_row_csv, genome_analysis.timestamp_naming())




def run(lib=True):
	run_library() if lib else run_non_library()


def main():
	lib = False
	run(lib)


if __name__ == '__main__':
	main()

