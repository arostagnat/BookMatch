from alive_progress import alive_bar

def compute():
    for i in range(1000):
        ... # process items as usual.
        yield  # insert this :)

with alive_bar(1000) as bar:
        for i in compute():
            bar()
