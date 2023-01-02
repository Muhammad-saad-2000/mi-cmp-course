import time

# This speed test approximates PI
# by integrating the arc length of the function sqrt(1 - x^2) over x in [0, 1] to get PI/2

start = time.time()

steps = int(1e7)
arc_length = 0

x, y = 0, 1
for index in range(1, steps+1):
    new_x = index / steps
    new_y = (1 - new_x * new_x) ** 0.5
    
    dx = new_x - x
    dy = new_y - y
    
    arc_length += (dx * dx + dy * dy) ** 0.5
    
    x, y = new_x, new_y

pi = 2 * arc_length

elapsed = time.time() - start

print(f"PI Estimation in {steps} steps: {pi}")
print(f"Done in {elapsed} seconds")