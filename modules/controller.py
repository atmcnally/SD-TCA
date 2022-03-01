#!/usr/bin/env python3

# the controller:
# - discovers the topology of the network
# - establishes TCP connections with any end devices that want to make a reservation request
# - manages a queue that contains requests sent from end devices via their TCP connection
# - requests are sent into the queue, then processed via a producer-consumer setup
# - this processing involves establishing the request, then sending out a confirmation to the end device involved
# - "show my reservations" command to see reservation requests per end device

from importsAndGlobal import queue, establishedRequests, datetime, RACK, username, base_password, ips
from random import randint
import networkx as nx
import matplotlib
import ssl
import jsonrpclib
import queueManager

class ReservationRequest:
  def __init__(self, senderIp, destIp, bandwidth, duration):
    self.senderIp = senderIp
    self.destIp = destIp
    self.bandwidth = bandwidth
    self.duration = duration # duration is measured from when the request is established on the controller, scale is in seconds
    self.expirationTime = None
    self.id = None # id is added when reservation is established

def createMockReqs():
    global queue
    for _ in range(5):
        tmpIp1 = ".".join(str(randint(0, 255)) for _ in range(4))
        tmpIp2 = ".".join(str(randint(0, 255)) for _ in range(4))
        tmpReq = ReservationRequest(tmpIp1, tmpIp2, randint(1, 5), randint(100, 1000))
        queue.append(tmpReq)

def discoverTopology(): # rerun this as needed
    return

def establishTcp(): # run on demand from end devices
    return 0

def cleanReservations():
    for entry in establishedRequests.values():
        currentTime = datetime.datetime.utcnow()
        if entry.expirationTime < currentTime:
            establishedRequests.popitem(entry)

createMockReqs()

# create threads
discoverer = queueManager.Discoverer()
# producer = queueManager.Producer()
# consumer = queueManager.Consumer()

# start threads
discoverer.start()
# consumer.start()
# producer.start()
discoverer.join()

G = nx.Graph()

for name, ip in ips.items():
    print("==== " + name + " lldp info ====")
    sw_num = name[2:4]
    password = base_password + sw_num
    url = 'https://{}:{}@{}/command-api'.format(username, password, ip)

    # SSL certificate check keeps failing; only use HTTPS verification if possible
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context


    eapi_conn = jsonrpclib.Server(url)

    payload = ["show lldp neighbors"]
    response = eapi_conn.runCmds(1, payload)[0]

    G.add_node(name)
    neighbors = response['lldpNeighbors']

    # print(neighbors)

    for n in neighbors:
        print(n['port'])

        payload[0] = "show interfaces " + n['port'] + " status"
        response = eapi_conn.runCmds(1, payload)[0]

        neighbor_name = n["neighborDevice"]
        neighbor_ip = ips[neighbor_name]

        G.add_edge(name, neighbor_name)
        bandwidth = response['interfaceStatuses'][n['port']]['bandwidth']
        G[name][neighbor_name]['bandwidth'] = bandwidth
        print(neighbor_name + " : " + neighbor_ip)

    # print("-" * 30)
    print("\n")

labels = nx.get_edge_attributes(G, "bandwidth")
pls = nx.spring_layout(G)
nx.draw_networkx(G, pls)
nx.draw_networkx_edge_labels(G, pls, labels)

matplotlib.pyplot.show()

# wait for threads to complete
# producer.join()
# consumer.join()

cleanReservations() # this needs to be run consistently
