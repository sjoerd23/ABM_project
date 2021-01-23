import numpy as np
from scipy.stats import truncnorm
import matplotlib.pyplot as plt


def get_truncated_normal(mean=0.5, sd=1/6, low=0, upp=1):
    return truncnorm(
        (low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)


# truncutated distribution for in between 0 -1
# i chose sd = 1/6 since only 0.1-0.2 % should be truncuated that way.

x = get_truncated_normal(mean=0.5, sd=1/6, low=0, upp=1)

#creating an array of 1000 random values
data = x.rvs(10000)


# you can print some example values here for fun
# for i in range(100):
#     print(x.rvs())

# # or print the data list
# print(data)

# two ways to plat the data, one used the data list and the other used rvs 10000 times.
# it's evident
fig, ax = plt.subplots(2, sharex=True)
ax[0].hist(x.rvs(100000))
ax[1].hist(data)
plt.show()






print(data)
