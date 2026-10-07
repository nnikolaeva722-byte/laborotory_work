def load_data():
    return [3, 17, 8, 25, 6, 12, 25, 9, 14]

def filter_above(values, threshold):
    f=[]
    for i in values:
        if i>threshold:
            f.append(i)
    return f
def mean_data(values):
    return sum(values)/len(values)
