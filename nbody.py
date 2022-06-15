import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation
import BarnesHut as bh


class universe:
    def __init__(self, positions, velocities, mass):
        self.positions = positions
        self.velocities = velocities
        self.mass = mass

    def calc_acceleration(self):
        acceleration = []

        for i in range(self.positions.shape[0]):
            new_positions = new_mass = []
            positions_temp = positions
            mass_temp = self.mass
            positions_temp = np.delete(positions_temp, i, 0)
            mass_temp = np.delete(mass_temp, i, 0)
            new_positions, new_mass = bh.main(positions_temp, mass_temp, positions[i], 1)

            temp = []
            for j in range(new_positions.shape[0]):
                if np.linalg.norm(new_positions[j] - positions[i]) < 1:
                    temp.append(
                        (mass_temp[j] / 1) * (
                                    new_positions[j] - positions[i]))
                else:
                    temp.append(
                        (mass_temp[j] / np.linalg.norm(new_positions[j] - positions[i]) ** 3) * (
                                    new_positions[j] - positions[i]))
            acceleration.append(np.sum(temp, axis=0))
        return np.array(acceleration)

    def simulate(self, timestep):
        accel = self.calc_acceleration()
        self.velocities = self.velocities + (timestep * accel)
        self.positions = self.positions + (self.velocities * timestep)


def randrange(n, vmin, vmax):
    return (vmax - vmin) * np.random.rand(n) + vmin


if __name__ == '__main__':
    np.random.seed(19680801)

    zlow, zhigh = -5, 5
    ylow, yhigh = 0, 5
    xlow, xhigh = 0, 5
    mlow, mhigh = 1, 10
    n = 20
    global positions
    positions = np.array([randrange(n, xlow, xhigh), randrange(n, ylow, yhigh), randrange(n, zlow, zhigh)]).T
    mass = np.array(randrange(n, mlow, mhigh))
    global uni
    uni = universe(positions, np.zeros((n, 3)), mass)
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set(xlim=[xlow, xhigh], ylim=[ylow, yhigh], zlim=[zlow, zhigh])


    def animate(i, j):
        ax.clear()
        fig = plt.figure()
        # ax = fig.add_subplot(projection='3d')
        uni.simulate(0.02)
        ax.scatter(uni.positions[:, 0], uni.positions[:, 1], uni.positions[:, 2])
        # plt.waitforbuttonpress()


    # debug_text = fig.text(0, 1, "TEXT", va='top')  # for debugging
    # annots = [ax.text2D(0,0,"POINT") for _ in range(N_points)]

    # Creating the Animation object
    ani = matplotlib.animation.FuncAnimation(fig, animate, fargs=[ax], frames=150)
    ani.save('continuousSineWave.mp4', writer='ffmpeg', fps=15)
