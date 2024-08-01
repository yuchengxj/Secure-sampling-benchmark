import random 
import sys

m = int(sys.argv[1])
n = int(1e8)
print('n', n)
print('m', m)
dest_dir = 'Player-Data/biased-input-P'

for j in range(m):
    output_file = dest_dir + str(j) + '-0'
    with open(output_file, 'a+') as f:
        for i in range(n):
            f.write(str(random.randint(0,1)) + ' ')
    f.close()


