import sys
sys.path.append("..")
print(sys.path)

import bin
import h261

fn = "video.261"
data = open(fn, "rb").read()
pic = h261.Picture(data)
print(pic)
pic.dump()
