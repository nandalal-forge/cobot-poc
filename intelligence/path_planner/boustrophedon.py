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


def generate_coverage_path_from_map(
    yaml_path: str,
    robot_width: float = 0.4
) -> list:
    import sys, os
    sys.path.insert(0, '/home/forge/cobot-poc')
    from intelligence.path_planner.map_reader import load_slam_map
    from shapely.geometry import Polygon as P

    room_corners, all_obstacles = load_slam_map(yaml_path)
    filtered = [o for o in all_obstacles if 0.1 < P(o).area < 30.0]
    print(f'Using {len(filtered)} obstacles after filtering')
    return generate_coverage_path(room_corners, filtered if filtered else None, robot_width)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/home/forge/cobot-poc')
    wps = generate_coverage_path_from_map('/tmp/lab_map.yaml')
    print(f'Generated {len(wps)} waypoints from SLAM map')