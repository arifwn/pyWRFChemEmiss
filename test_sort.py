from random import randint

class PointData():
    def __init__(self, x, y, value):
        self.x     = x
        self.y     = y
        self.value = value
    
    def __str__(self):
        return '{0}:{1}'.format(self.x, self.y)
    
def compare_pointdata(a, b):
    if (a.x == b.x) and (a.y == b.y):
        return 0
    if (a.y < b.y):
        return -1
    if (a.y == b.y) and (a.x < b.x):
        return -1
    return 1

def compare_pointdata_f(a, b):
    err = 0.0001
    if (abs(a.x - b.x) <= err) and (abs(a.y - b.y) <= err):
        return 0
    if ((b.y - a.y) >= err):
        return -1
    if (abs(a.y - b.y) <= err) and ((b.x - a.x) >= err):
        return -1
    return 1


list_data = []
for i in range(100):
    for j in range(100):
        list_data.append(PointData(randint(1,100), randint(1,100), i + j))

list_data.sort(compare_pointdata_f)
for el in list_data:
    print el
