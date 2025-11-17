import numpy as np


class CompactHistoryManager:
    def __init__(self):
        self.times = []
        self.positions = []

    def add_frame(self, time_elapsed, bats):
        self.times.append(time_elapsed)
        # Store all bat positions as flat array: [x1, y1, x2, y2, ...]
        frame_positions = []
        for bat in bats:
            frame_positions.extend([bat.position.x, bat.position.y])
        self.positions.append(frame_positions)

    def save_compressed(self, filename):
        # Convert to efficient numpy arrays
        times_array = np.array(self.times, dtype="f4")

        # Find maximum number of bats to create fixed-size array
        max_bats = max(len(frame) // 2 for frame in self.positions)
        positions_array = np.full(
            (len(self.positions), max_bats * 2), np.nan, dtype="f4"
        )

        # Fill the array with position data
        for i, frame in enumerate(self.positions):
            positions_array[i, : len(frame)] = frame

        np.savez_compressed(filename, times=times_array, positions=positions_array)


class CompactHistoryLoader:
    def __init__(self, filename):
        self.data = np.load(filename)
        self.times = self.data["times"]
        self.positions = self.data["positions"]

    def reconstruct_frame(self, frame_idx):
        frame_data = self.positions[frame_idx]
        # Remove NaN values and pair x,y coordinates
        valid_positions = frame_data[~np.isnan(frame_data)]
        bat_positions = [
            (valid_positions[i], valid_positions[i + 1])
            for i in range(0, len(valid_positions), 2)
        ]

        return {"time": float(self.times[frame_idx]), "bat_positions": bat_positions}

    def reconstruct_all(self):
        return [self.reconstruct_frame(i) for i in range(len(self.times))]

    def get_frame_count(self):
        return len(self.times)
