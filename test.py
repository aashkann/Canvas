from PIL import Image as im
import numpy as np
width = int(14.0)
height = int(14.0)

np_results = np.zeros((width, height))

print(np_results)


data = im.fromarray(np_results)
data = data.convert('RGB')

data.save("results.png")
