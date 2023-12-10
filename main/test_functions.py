def reverse_list_in_lists(list_of_list):
	for list in list_of_list:
		list.sort(reverse=True)
		while len(list) > 1:
			list.pop()


def binary_search_insert(l, insert_n):
	start = 0
	end = len(l) - 1
	while start + 1 < end:
		mid = (start + end) // 2
		if l[mid] <= insert_n:
			start = mid
		else:
			end = mid
	if start == 0:
		l.insert(0, insert_n)
	elif end == len(l) - 1:
		l.append(insert_n)
	else:
		l.insert(start + 1, insert_n)

# class A:
#
# 	def a():
# 		print('s')
# 		return 's'
#
# 	def b():
# 		b = 'a' + A.a()
# 		return b
#
# 	c = b()

def main():
	l = [1,3,5,7,9]
	l_1= [3, 7, 1, 5, 9]
	# # insert_n = 10
	# # binary_search_insert(l, insert_n)
	# # print(l)
	# l_a = l[:3]
	# print(l_a)
	# l_b = l[3:]
	# l_a = [2, 4, 6]
	# print(l)
	# print(l_a)
	# obj_a = A()
	l_1.sort(reverse=True)
	print(l_1.pop())
	while len(l) > 2:
		l.pop()
	print(l)
if __name__ == '__main__':
	main()

