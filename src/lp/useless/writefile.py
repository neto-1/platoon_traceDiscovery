file = open('testfile.txt', 'w')

file.write('HelloWorld\n')
file.write('This is our new text file\n')
file.write(' and this is another line.\n')
file.write('Why? Because we can.\n')
file.close()


file = open('testfile.txt', 'a')

file.write('APPEND')

file.close()