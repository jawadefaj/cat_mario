import csv
import os
import cv2
import datetime
from shutil import copy

#csvData = [['Person', 'Age'], ['Peter', '22'], ['Jasmine', '21'], ['Sam', '24']]
count = 0

def create_file(month, day, hour, _min):
	# file_name = str(month) + '_' + str(day) + '_' + str(hour) + '_' + str(_min) + '.csv'
	# https://stackoverflow.com/questions/9828311/how-to-get-min-seconds-and-milliseconds-from-datetime-now-in-python
	Date = str(datetime.datetime.now())[:10]
	Hour = str(datetime.datetime.now())[11:13]
	Minute = str(datetime.datetime.now())[14:16]
	Second = str(datetime.datetime.now())[17:19]

	file_name = 'log\\' + Date + '_' + Hour + '_' + Minute + '_' + Second + '.csv'
	config_file_name = 'config' + Date + '_' + Hour + '_' + Minute + '_' + Second
	cwd = os.getcwd()
	log_dir = 'log'
	config_dir = 'config'
	if not os.path.exists(cwd):
		os.makedirs(cwd)
	copy(config_dir, log_dir)
	os.chdir(log_dir)
	# print ("The dir is: " , os.listdir(os.getcwd()))
	os.rename("config", config_file_name)
	os.chdir(cwd)
	with open(file_name, 'w+') as csvFile:
		csvData = [['Generation', 'ID', 'fitness', 'max_fitness', 'mean_fitness']]
		# print("creating file.....")
		writer = csv.writer(csvFile)
		writer.writerows(csvData)
		csvFile.close()

	return file_name


def log_csv(file_name,generation, ID, fitness, maxfitness, meanfitness):
	csvData = [[str(generation), str(ID), str(fitness), str(maxfitness), str(meanfitness)]]
	global count
	count += 1
	# print("file name .............",file_name)
	with open(file_name, 'a') as csvFile:
	    writer = csv.writer(csvFile)
	    print("Writing", count)
	    writer.writerows(csvData)

	csvFile.close()
