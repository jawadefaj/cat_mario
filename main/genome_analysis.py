import os
import pickle
import datetime

GENOMES_PATH = 'best_genomes_pickles'

def save_genome(genome_filename, folder_name, genome):
	genome_path = os.path.join(GENOMES_PATH, folder_name, genome_filename)

	file_handle = open(genome_path, 'wb')
	pickle.dump(genome, file_handle)
	print('genome_saved: ')
	print(genome)
	file_handle.close()


def timestamp_naming():
	Date = str(datetime.datetime.now())[:10]
	Hour = str(datetime.datetime.now())[11:13]
	Minute = str(datetime.datetime.now())[14:16]
	Second = str(datetime.datetime.now())[17:19]
	return Date + '_' + Hour + '_' + Minute + '_' + Second

def create_folder_name():
	folder_name = timestamp_naming()
	folder_path = os.path.join(GENOMES_PATH, folder_name)
	os.makedirs(folder_path)
	return folder_name


def load_genome(genome_filename, folder_name):
	genome_path = os.path.join(GENOMES_PATH, folder_name, genome_filename)
	file_handle = open(genome_path, 'rb')
	genome = pickle.load(file_handle)
	print(genome.__str__())
	file_handle.close()
	return genome


def main():
	foler_number = 3
	genome_numbers = [7, 17, 19, 22, 24, 25]
	for genome_number in genome_numbers:
		# genome_number = 18
		print(genome_number)
		folder_name = 'run_' + str(foler_number)
		genome_filename = str(genome_number) + r'.pkl'
		genome = load_genome(genome_filename, folder_name)

if __name__ == '__main__':
	main()