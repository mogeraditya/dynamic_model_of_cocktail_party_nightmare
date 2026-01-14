import matplotlib.pyplot as plt
import numpy as np

matrix = np.random.randint(0, 11, (6, 12))
max_val = np.max(matrix)

# Create colormap with black for 0
colors = plt.cm.viridis(np.linspace(0, 1, max_val + 1))
colors[0] = [0, 0, 0, 1]
cmap = plt.cm.colors.ListedColormap(colors)

fig, ax = plt.subplots(subplot_kw={"projection": "polar"})

for i in range(6):
    for j in range(12):
        ax.bar(
            j * np.pi / 6,
            0.002,
            np.pi / 6,
            bottom=0.002 + i * 0.002,
            color=cmap(matrix[i, j]),
            align="edge",
        )

ax.set_theta_zero_location("N")

# Colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, max_val))
sm.set_array([])
fig.colorbar(sm, ax=ax, label="Value (0=black)")

plt.show()
