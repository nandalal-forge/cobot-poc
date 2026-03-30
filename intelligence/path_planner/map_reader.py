import yaml
import numpy as np
from PIL import Image
from scipy import ndimage
import os

def load_slam_map(yaml_path: str):
    with open(yaml_path, 'r') as f:
        meta = yaml.safe_load(f)

    resolution = meta['resolution']
    origin = meta['origin']

    pgm_path = meta['image']
    if not os.path.isabs(pgm_path):
        pgm_path = os.path.join(os.path.dirname(yaml_path), meta['image'])

    img = np.array(Image.open(pgm_path).convert('L'))
    img = np.flipud(img)
    height, width = img.shape

    def pixel_to_metres(px, py):
        x = origin[0] + px * resolution
        y = origin[1] + py * resolution
        return round(x, 3), round(y, 3)

    free_mask = img > 200
    occupied_mask = img < 50

    free_rows = np.any(free_mask, axis=1)
    free_cols = np.any(free_mask, axis=0)
    row_min = np.argmax(free_rows)
    row_max = len(free_rows) - np.argmax(free_rows[::-1]) - 1
    col_min = np.argmax(free_cols)
    col_max = len(free_cols) - np.argmax(free_cols[::-1]) - 1

    room_corners = [
        pixel_to_metres(col_min, row_min),
        pixel_to_metres(col_max, row_min),
        pixel_to_metres(col_max, row_max),
        pixel_to_metres(col_min, row_max),
    ]

    labeled, num_features = ndimage.label(occupied_mask)
    obstacle_polygons = []

    for i in range(1, num_features + 1):
        blob = labeled == i
        blob_size = np.sum(blob)
        if blob_size < 20:
            continue
        if blob_size > (height * width * 0.05):
            continue
        rows = np.any(blob, axis=1)
        cols = np.any(blob, axis=0)
        r_min = np.argmax(rows)
        r_max = len(rows) - np.argmax(rows[::-1]) - 1
        c_min = np.argmax(cols)
        c_max = len(cols) - np.argmax(cols[::-1]) - 1
        pad = 2
        corners = [
            pixel_to_metres(max(0, c_min-pad), max(0, r_min-pad)),
            pixel_to_metres(min(width, c_max+pad), max(0, r_min-pad)),
            pixel_to_metres(min(width, c_max+pad), min(height, r_max+pad)),
            pixel_to_metres(max(0, c_min-pad), min(height, r_max+pad)),
        ]
        obstacle_polygons.append(corners)

    print(f'Map loaded: {width}x{height}px, resolution={resolution}m/px')
    print(f'Room bounds: {room_corners[0]} to {room_corners[2]}')
    print(f'Obstacles found: {len(obstacle_polygons)}')

    return room_corners, obstacle_polygons


if __name__ == '__main__':
    room, obstacles = load_slam_map('/tmp/lab_map.yaml')
    print(f'Room: {room}')
    for i, o in enumerate(obstacles):
        print(f'Obstacle {i+1}: {o[0]} → {o[2]}')