import matplotlib.pyplot as plt
import numpy as np

data = [
    [14962, 11733, 8508],
    [10063, 7521, 5179],
    [10253, 7974, 5693],
    [10602, 7663, 5480],
    [10884, 7754, 5350]
]

X = np.array([300, 400, 500])

barWidth = 14

ax = plt.subplot()
ax.bar(X, data[0], color = 'b', width = barWidth, label = 'All traffic handled by the service with the lowest latency')
ax.bar(X + barWidth, data[1], color = 'g', width = barWidth, label = 'Equally distributed traffic to all 5 services')
ax.bar(X + 2 * barWidth, data[2], color = 'r', width = barWidth, label = 'Distributed traffic to all 5 services weighted by base latency')
ax.bar(X + 3 * barWidth, data[3], color = 'fuchsia', width = barWidth, label = 'Randomly distributed traffic to all 5 services')
ax.bar(X + 4 * barWidth, data[4], color = 'orange', width = barWidth, label = 'Equally distributed traffic to all 3 regions, but randomly distributed to region services')

ax.set_xticks(X + (barWidth * 2))
ax.set_xticklabels(X)

plt.xlabel("Number of concurrent requests", fontweight='bold')
plt.ylabel("Elapsed time(ms)", fontweight='bold')
plt.title("Load balancer policies performances (Lower is better)", fontweight='bold')

ax.legend()
plt.gcf().set_size_inches(barWidth, barWidth / 2)
plt.show()