from multiprocessing import Process, Queue
import time
import sys

def f(q):
    while True:
        if q.empty():
            print "empty..."
        else:
            print q.get()        
        time.sleep(2)

def g(q):
    x=0.0
    while True:
        x=time.time()
        print x        
        q.put(x)
        time.sleep(1)

if __name__ == '__main__':
    q=Queue()
    q.put(1.1)
    p2=Process(target=g,args=(q,))
    p=Process(target=f,args=(q,))
    time.sleep(3)
    p2.start()
    p.start()
    p2.join()
    p.join()
