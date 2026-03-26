#!/usr/bin/env python3

import numpy as np
from shapely.geometry import Polygon, LineString

def generate_coverage_path(
    room_coords: list,
    exclusion_coords_list: list = None,
    robot_width: float = 0.4
) -> list:
    """
    Returns list of (x, y) waypoints in lawnmower pattern.
    room_coords: list of [x, y] in metres
    exclusion_coords_list: list of polygons to avoid (benches etc)
    robot_width: cleaning width in metres
    """
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


if __name__ == '__main__':
    # Test with our lab room and 3 benches
    room = [[0,0],[10,0],[10,8],[0,8]]
    benches = [
        [[1.5,1.5],[3.5,1.5],[3.5,2.5],[1.5,2.5]],
        [[-2.5,-2.5],[-.5,-2.5],[-.5,-1.5],[-2.5,-1.5]],
        [[2.5,-3.5],[4.5,-3.5],[4.5,-2.5],[2.5,-2.5]]
    ]
    wps = generate_coverage_path(room, benches)
    print(f'Generated {len(wps)} waypoints')

    import matplotlib.pyplot as plt
    from shapely.geometry import Polygon as P
    from shapely.plotting import plot_polygon
    fig, ax = plt.subplots(figsize=(12, 9))
    plot_polygon(P(room), ax=ax, facecolor='#E8F5E9', edgecolor='#333', linewidth=2)
    for b in benches:
        plot_polygon(P(b), ax=ax, facecolor='#FFCDD2', edgecolor='#D32F2F')
    xs, ys = zip(*wps)
    ax.plot(xs, ys, 'b-', linewidth=0.6, alpha=0.8)
    ax.scatter(xs[::3], ys[::3], s=8, c='blue', zorder=5)
    ax.set_title(f'Coverage path — {len(wps)} waypoints, robot width 0.4m')
    plt.savefig('/tmp/coverage_path.png', dpi=150, bbox_inches='tight')
    print('Saved: /tmp/coverage_path.png')