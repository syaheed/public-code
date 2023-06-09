# Let's play around with AdaBoost in scikit-learn

# Imports
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import AdaBoostRegressor
from sklearn.tree import DecisionTreeRegressor

# Parameters
np.random.seed(13)
max_num_estimators = 600
num_samples = 100
noise_mu = 0
noise_sigma = 0.1 

# Data generation
x = np.linspace(0, 1, num_samples)
y = x + np.sin(1*x) + np.sin(20*x + 12) + np.random.normal(noise_mu, noise_sigma, num_samples)

## Regressions
X = x.reshape(-1, 1)
regr1 = DecisionTreeRegressor(max_depth=4)
regr1.fit(X, y)
y1 = regr1.predict(X)

loss = np.empty((max_num_estimators,1))
for ne in range(max_num_estimators):
  print(ne)
  regr2 = AdaBoostRegressor(DecisionTreeRegressor(max_depth=4), n_estimators=ne+1)
  regr2.fit(X, y)
  y2 = regr2.predict(X)
  loss[ne] = np.sum((y2-y)**2)


# Plot
fig, axs = plt.subplots(2)
fig.suptitle('Boosted Decision Trees on Sinunoidal Data')

axs[0].scatter(X, y, color = "blue", label="Data")
axs[0].plot(X, y1, color="green", label="Decision Tree", linewidth=2)
axs[0].plot(X, y2, color="red", label="Boosted Tree", linewidth=2)
axs[0].set_xlabel("X")
axs[0].set_ylabel("Y")
axs[0].set_title("Model Comparison")
axs[0].legend()

axs[1].plot(range(1,max_num_estimators+1), loss, color = "black", linewidth=2)
axs[1].set_xlabel("num_estimators")
axs[1].set_ylabel("loss")
plt.show()

# End
print("Done!")