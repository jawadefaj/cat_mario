importS csv
# Create a workbook and add a worksheet.
CSV_LOG_DIR = 'csv_log'

def write_csv(l_row_csv, filename):
	file_path = os.path.join(CSV_LOG_DIR, filename)
	with open(file_path, mode='w', newline='') as write_csv_file:
		csv_writer = csv.writer(write_csv_file, delimiter=',')
		for row in l_row_csv:
			csv_writer.writerow(row)


def main():
	ll_writing = []
	col = 3
	for i in range(4):
		read_file_dir = 'elite_' + str(i) + '.csv'
		print(read_file_dir)
		with open(read_file_dir) as read_csv_file:
			read_csv_reader = csv.reader(read_csv_file, delimiter=',')
			write_row_counter = 0
			for row in read_csv_reader:
				print(len(row))
				if len(row) > 0 and row[col] != '0':
					if i == 0:
						ll_writing.append([write_row_counter, row[col]])
					else:
						if len(ll_writing) <= write_row_counter:
							ll_writing.append([write_row_counter, row[col]])
						else:
							ll_writing[write_row_counter].append(row[col])
					write_row_counter += 1

	# writing
	write_filename = 'elite_max_graph.csv'
	with open(write_filename, mode='w', newline='') as write_csv_file:
		csv_writer = csv.writer(write_csv_file, delimiter=',')
		for l in ll_writing:
			csv_writer.writerow(l)

if __name__ == '__main__':
	main()
