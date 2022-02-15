#!/usr/bin/python

import threading
import time

# Shared Memory variables
CAPACITY = 10
buffer = [-1 for i in range(CAPACITY)]
in_index = 0
out_index = 0

# Declaring Semaphores
mutex = threading.Semaphore()
empty = threading.Semaphore(CAPACITY)
full = threading.Semaphore(0)

queue = [7, 2, 3, 5, 6, 2, 8] # global array of requests as they come in

# Producer Thread Class
class Producer(threading.Thread):
    def run(self):
     
        global CAPACITY, buffer, in_index, out_index
        global mutex, empty, full
    
        itemsInQueue = len(queue)
        
        while itemsInQueue > 0:
            empty.acquire()
            mutex.acquire()
            nextItem = queue.pop()
            buffer[in_index] = nextItem
            in_index = (in_index + 1) % CAPACITY
            print("request produced : ", nextItem)
            
            mutex.release()
            full.release()
            
            time.sleep(1)
            
            itemsInQueue = len(queue)
 
# Consumer Thread Class
class Consumer(threading.Thread):
    def run(self):
     
        global CAPACITY, buffer, in_index, out_index
        global mutex, empty, full
     
        itemsInQueue = len(queue)
        while itemsInQueue > 0:
            full.acquire()
            mutex.acquire()
        
            item = buffer[out_index]
            out_index = (out_index + 1) % CAPACITY
            print("request accepted : ", item)
        
            mutex.release()
            empty.release()
        
            time.sleep(0.5)
        
            itemsInQueue = len(queue)
 
# Creating Threads
producer = Producer()
consumer = Consumer()
 
# Starting Threads
consumer.start()
producer.start()
 
# Waiting for threads to complete
producer.join()
consumer.join()