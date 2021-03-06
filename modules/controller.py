#!/usr/bin/env python3

# the controller:
# - discovers the topology of the network
# - establishes TCP connections with any end devices that want to make a reservation request
# - manages a queue that contains requests sent from end devices via their TCP connection
# - requests are sent into the queue, then processed via a producer-consumer setup
# - this processing involves establishing the request, then sending out a confirmation to the end device involved
# - "show my reservations" command to see reservation requests per end device

import argparse
import json
import datetime
import threading
import queue
import importsAndGlobal as glob
from random import randint
import queueManager


parser = argparse.ArgumentParser(
    description="A resource reservation controller. (SD-TCA)"
)
parser.add_argument(
    "address", metavar="A.B.C.D", type=str, help="Controller IP address."
)
parser.add_argument("port", metavar="Port", type=str, help="Controller Port number.")
args = parser.parse_args()
args = json.dumps(vars(args))  #    JSON FORMATTED ARGUMENTS
args = json.loads(args)
glob.CONTROLLER_IP = args["address"]
glob.CONTROLLER_PORT = int(args["port"])

# def createMockReqs():
#     # Temporary for testing
#     #   To be removed
#     global queue
#     for _ in range(5):
#         tmpIp1 = ".".join(str(randint(0, 255)) for _ in range(4))
#         tmpIp2 = ".".join(str(randint(0, 255)) for _ in range(4))
#         tmpReq = ReservationRequest(tmpIp1, tmpIp2, randint(1, 5), randint(100, 1000), "234.234.23.4.2", 3454)
#         queue.put(tmpReq)

# def discoverTopology(): # rerun this as needed
#     return


def cleanReservations():
    for entry in glob.establishedRequests.values():
        currentTime = datetime.datetime.utcnow()
        if entry.expirationTime < currentTime:
            glob.establishedRequests.popitem(entry)


# createMockReqs()

# CREATE THREADS
switchHandler = queueManager.SwitchHandler()
hostManager = queueManager.HostManager()

print("threads starting")
lock = threading.Lock()
reservationHandler = threading.Thread(
    target=queueManager.consumer, args=(glob.queue, lock), daemon=True
)
# START THREADS
switchHandler.start()
hostManager.start()
reservationHandler.start()

# WAIT FOR THREADS TO COMPLETE
switchHandler.join()
hostManager.join()
reservationHandler.join()
# hostManager.kill()

cleanReservations()  # this needs to be run consistently
