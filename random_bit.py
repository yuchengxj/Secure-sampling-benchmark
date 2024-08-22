import random 
import sys

n = int(sys.argv[1])
m = int(sys.argv[2])

print('n', n)
print('m', m)
dest_dir = 'Player-Data/biased-input-P'
m = 8

for j in range(m):
    output_file = dest_dir + str(j) + '-0'
    with open(output_file, 'a+') as f:
        for i in range(10**7):
            f.write(str(random.randint(0,1)) + ' ')
    f.close()


