import random
import math
import statistics
import collections
import matplotlib.pyplot as plt

# function to create exp distribution
def create_exp_distribution(lambda_var):
  U = random.uniform(0, 1)
  delta_t = (-1/lambda_var) * math.log(1-U)

  return delta_t

# simulation function takes inputs and returns an array of arrival, departure, 
# and observer event which are sorted by timestamp
# C -> network speed (bits/sec)
# L -> avg packet length (bits)
# p -> traffic intensity
# K -> max queue size
# T -> max simulation time
def simulation(C, L, p, T, K): # simulation function
  lambda_var = (C/L) * p 
  cur_time = 0
  # 2 queues to store events and easily access the last departure time
  arrival_queue = []
  departure_queue = []
  # queue len to simulate how many packets are in the queue
  queue_len = 0

  # simulate the max time, T
  while cur_time < T:
    # generating random arrival time and packet length
    arrival_time_interval = create_exp_distribution(lambda_var)
    packet_length = create_exp_distribution(1/L)
    service_time = packet_length/C

    # simulate the current time 
    cur_time += arrival_time_interval

    # check if departure q has items
    if len(departure_queue) > 0:
      if cur_time < departure_queue[-1][0]: # if current time < last departure time, packet is in q
        queue_len += 1
      else:
        queue_len -= 1

    departure_time = 0 # determine departure time
    if queue_len == 0: # queue is empty 
      departure_time = cur_time + service_time
    else: # queue contains packets
      departure_time = departure_queue[-1][0] + service_time

    if cur_time > departure_time: # if generated departure time is before arrival time
      departure_time = cur_time + service_time

    # append events to respective queues
    arrival_queue.append((cur_time, "arrival"))
    departure_queue.append((departure_time, "departure"))

  # create observer events
  cur_time = 0
  observer_queue = []
  while cur_time < T:
    observer_time_interval = create_exp_distribution(lambda_var*5)
    cur_time += observer_time_interval
    observer_queue.append((cur_time, "observer"))

  # combine into 1 queue and sort
  queue = arrival_queue + departure_queue + observer_queue
  queue.sort()

  return queue

# function to process the queue and calculate the performance metrics
# also contains the logic to distinguish MM1 and MM1K
# queue -> the list of events with timestamps (timestamp, event_type)
# returns [E[n], P_idle] if MM1, or [E[n], P_loss] if MM1K
def process_queue(queue, T, K):
  arrival_count = 0
  departure_count = 0
  observer_count = 0
  idle_count = 0
  packet_loss_count = 0
  packets_in_queue_sum = 0

  # check each event in queue
  for time, event in queue:
    if time < T:
      if event == "arrival":
        arrival_count += 1
      elif event == "departure":
        departure_count += 1
      else:
        observer_count += 1
        # calculate the number of packets in queue 
        packets_in_queue = arrival_count - departure_count

        if K != -1: # packet loss in M/M/1/K queue
          if packets_in_queue > K: # if number of packets in q > max q size there is packet lost
            packet_loss_count += 1
            packets_in_queue_sum += K
          else:
            packets_in_queue_sum += packets_in_queue
        else: # idle time in MM1 queue
          packets_in_queue_sum += packets_in_queue
          if packets_in_queue == 0: # if no packets in queue, then it is idle
            idle_count += 1

  res = [round(packets_in_queue_sum/observer_count, 5)]
  if K != -1:
    # res = [avg packets in queue, P_loss] if MM1K
    res.append(round(100*packet_loss_count/observer_count, 5))
  else:
    # res = [avg packets in queue, P_idle] if MM1
    res.append(round(100*idle_count/observer_count, 5))

  return res

# Q1 -> testing exp distribution
sample = []
for i in range(1000):
  sample.append(create_exp_distribution(75))

print("Mean: ", statistics.mean(sample))
print("Variance: ", statistics.variance(sample))

# parameters
C = 1000000 # network speed (bits/sec)
L = 2000 # avg packet length (bits)
p = 0.25 # traffic intensity
K = -1 # max queue size
T = 1000 # max simulation time

# Q3 -> M/M/1
p_data_1 = []
E_data_1 = []
P_idle_data_1 = []
for i in range(25, 96, 10): # loop for values of p, increment by 0.1
  p = round(i * 0.01, 2) 
  q = simulation(C, L, p, T, K)
  sim_res = process_queue(q, T, K)
  
  # create datasets
  p_data_1.append(p)
  E_data_1.append(sim_res[0])
  P_idle_data_1.append(sim_res[1])

plt.figure()
plt.plot(p_data_1, E_data_1)
plt.xlabel('p (Utilization of queue)')
plt.ylabel('E[n] (Avg number of packets in queue)')
plt.title('E[n] vs p for M/M/1')
plt.show()

plt.figure()
plt.plot(p_data_1, P_idle_data_1)
plt.xlabel('p (Utilization of queue)')
plt.ylabel('P_idle (Percentage of time server is idle)')
plt.title('P_idle vs p for M/M/1')
plt.show()

# Q4
p = 1.2
event_queue_Q4 = simulation(C, L, p, T, K)
data_Q4 = process_queue(event_queue_Q4, T, K)
print("Question 4: ")
print("E[n] with p = 1.2: ", data_Q4[0])
print("P_idle with p = 1.2: ", data_Q4[1], "%")

# Q6 -> M/M/1/K
K_list = [10, 25, 50]
p_data_2 = []
E_data_2 = []
P_loss_data_2 = []

for i in range(len(K_list)): # for each value of K required [10,25,50]
  K = K_list[i]
  p_arr = []
  E_arr = []
  P_loss_arr = []
  
  for j in range(50, 151, 10): # loop through values of p
    p = round(j * 0.01, 2)
    q = simulation(C, L, p, T, K)
    sim_res = process_queue(q, T, K)
    
    # append to datasets
    p_arr.append(p)
    E_arr.append(sim_res[0])
    P_loss_arr.append(sim_res[1])

  p_data_2 = p_arr
  E_data_2.append(E_arr)
  P_loss_data_2.append(P_loss_arr)

plt.figure()
plt.plot(p_data_2, E_data_2[0], 'r', label='K = 10')
plt.plot(p_data_2, E_data_2[1], 'b', label='K = 25')
plt.plot(p_data_2, E_data_2[2], 'g', label='K = 50')
plt.xlabel('p (Utilization of queue)')
plt.ylabel('E[n] (Avg number of packets in queue)')
plt.title('E[n] vs p for M/M/1/K')
plt.legend()
plt.show()

plt.figure()
plt.plot(p_data_2, P_loss_data_2[0], 'r', label='K = 10')
plt.plot(p_data_2, P_loss_data_2[1], 'b', label='K = 25')
plt.plot(p_data_2, P_loss_data_2[2], 'g', label='K = 50')
plt.xlabel('p (Utilization of queue)')
plt.ylabel('P_loss (Percentage of time server is idle)')
plt.title('P_loss vs p for M/M/1/K')
plt.legend()
plt.show()

quit
