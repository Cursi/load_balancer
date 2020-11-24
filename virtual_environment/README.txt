README pentru Tema EP

1. How many requests can be handled by a single machine?
    I will consider 15000ms the maximum time for a good request. (Basically half of the classic 30s timeout)
    Anything above that threshold is just too much for a human to wait.

    I observed as an average of 500 concurent requests on any of the 5 individual machines at a time
    will be just below this 15 seconds threshold.

2. What is the latency of each region?
    By doing 10 requests and averaging the latency obtained from a simple curl command to the 3 regions
    I observed that the latencies are: Emea -> 330ms, US -> 370ms, Asia -> 520ms

3. What is the computation time for a work request?
    For all machine the computation time is around 20ms.

4. What is the the response time of a worker when there is no load?
    Basically the latency - work_time, in the same average manner, so: Emea -> 310ms, US -> 350ms, Asia -> 500ms

5. What is the latency introduced by the forwarding unit?

    I measured that by doing 10 requests to the local hosted forwarding unit, and 10 request to 
    the heroku URL directly, computing the averages and substracting them.
    Results: 160ms emea, 200ms us, asia 350ms
    
    We can observe that although all services are deployed in Europe, forwarding unit is artificially
    adding latency to simulate the distance.

6. How many requests must be given in order for the forwarding unit to become the bottleneck of the system? 
   How would you solve this issue?

   This depends a lot on the machine were the forwarding unit will be run and on its inside implementation.
   Based on the number of operations of the CPU, considering it is an asnyc implementation and the network
   has a infinite bandwidth we can say that the forwarding unit will become the bottleneck when it will
   receive that many requests (+1) that the CPU cand handle, so it will queue requests forwardings and it will
   produce higher latencies than the one artificially added discussed in the question 5.
   
   I will solve this issue by using a distributed system, more like a load balancer for proxies,
   so I when many requests hit at the same time would not be handled by one unique FU.

7. What is your estimation regarding the latency introduced by Heroku?
    I computed that by taking from any of the services instances logs the sum of connect time
    and service time where there was only 1 request to the server.
    Did that 10 times in a row and averaged, resulted in an around 22ms latency added by Heroku, not bad.
   
8. What downsides do you see in the current architecture design?
    The major downside is that all the traffic goes to an unique FU. (More details in question 6).
    Another downisde can be the usage of Heroku:
        - cannot handle too many requests at the same time, in terms that it will stack up response time quite easy.
        - adds a bit of latency described at question 7. 
        - goes idle in 15min if no requests are made.
        - maximum response time is 30 seconds which is small if trying to do huge backend processing like ML
    services for example.