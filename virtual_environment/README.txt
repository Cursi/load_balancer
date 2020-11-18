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

    ??????????????????
    I measured that by doing 10 requests to the local hosted forwarding unit, and 10 request to 
    the heroku URL directly, computing the averages and substracting them.
    Results: 150ms emea,
    ??????????????????

6. How many requests must be given in order for the forwarding unit to become the bottleneck of the system? 
   How would you solve this issue?

   ???????????????????

7. What is your estimation regarding the latency introduced by Heroku?

   ???????????????????

8. What downsides do you see in the current architecture design?

   ???????????????????