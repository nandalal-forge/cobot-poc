#!/usr/bin/env python3

import numpy as np
from shapely.geometry import Polygon, LineString

def generate_coverage_path(
    room_coords: list,
    exclusion_coords_list: list = None,
    robot_width: float = 0.4
) -> list:
    room = Polygon(room_coords)
    clean_area = room
    if exclusion_coords_list:
        for exc in exclusion_coords_list:
            clean_area = clean_area.difference(Polygon(exc))
    minx, miny, maxx, maxy = clean_area.bounds
    waypoints = []
    y = miny + robot_width / 2
    direction = 1
    while y <= maxy:
        strip = LineString([(minx - 0.1, y), (maxx + 0.1, y)])
        intersection = clean_area.intersection(strip)
        if not intersection.is_empty:
            geoms = (intersection.geoms
                     if intersection.geom_type == 'MultiLineString'
                     else [intersection])
            for line in geoms:
                coords = list(line.coords)
                if direction == -1:
                    coords = coords[::-1]
                waypoints.extend(coords)
        y += robot_width
        direction *= -1
    return [(round(x, 3), round(y, 3)) for x, y in waypoints]


def generate_coverage_path_from_map(yaml_path: str, robot_width: float = 0.4) -> list:
    """
    Loads a SLAM map yaml and generates coverage waypoints automatically.
    Filters out walls and keeps only obstacle-sized blobs.
    """
    from intelligence.path_planner.map_reader import load_slam_map

    room_corners, all_obstacles = load_slam_map(yaml_path)

    # Filter: keep only obstacles smaller than 30m² (benches, not walls)
    from shapely.geometry import Polygon as P
    filtered_obstacles = []
    for obs in all_obstacles:
        poly = P(obs)
        if 0.1 < poly.area < 30.0:
            filtered_obstacles.append(obs)

    print(f'Using {len(filtered_obstacles)} obstacles after filtering')

    waypoints = generate_coverage_path(
        room_corners,
        filtered_obstacles if filtered_obstacles else None,
        robot_width
    )
    return waypoints


if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

    print('=== Generating from SLAM map ===')
    wps = generate_coverage_path_from_map('/tmp/lab_map.yaml')
    print(f'Generated {len(wps)} waypoints from SLAM map')

    import matplotlib.pyplot as plt
    from shapely.geometry import Polygon as P
    from shapely.plotting import plot_polygon
    from intelligence.path_planner.map_reader import load_slam_map

    room, obstacles = load_slam_map('/tmp/lab_map.yaml')
    filtered = [o for o in obstacles if 0.1 < P(o).area < 30.0]

    fig, ax = plt.subplots(figsize=(12, 9))
    plot_polygon(P(room), ax=ax, facecolor='#E8F5E9', edgecolor='#333', linewidth=2)
    for obs in filtered:
        plot_polygon(P(obs), ax=ax, facecolor='#FFCDD2', edgecolor='#D32F2F')
    if wps:
        xs, ys = zip(*wps)
        ax.plot(xs, ys, 'b-', linewidth=0.6, alpha=0.8)
        ax.scatter(xs[::3], ys[::3], s=8, c='blue', zorder=5)
    ax.set_title(f'Coverage from SLAM map — {len(wps)} waypoints')
    plt.savefig('/tmp/coverage_slam.png', dpi=150, bbox_inches='tight')
    print('Saved: /tmp/coverage_slam.png')