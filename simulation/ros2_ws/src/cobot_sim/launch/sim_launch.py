#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, TimerAction, SetEnvironmentVariable, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os
import xacro

def generate_launch_description():
    pkg = get_package_share_directory('cobot_sim')
    xacro_file = os.path.join(pkg, 'urdf', 'cobot.urdf.xacro')
    robot_description = xacro.process_file(xacro_file).toxml()
    maps_dir = os.path.join(pkg, 'maps')

    return LaunchDescription([
        SetEnvironmentVariable('GAZEBO_MODEL_PATH', '/usr/share/gazebo-11/models'),
        SetEnvironmentVariable('GAZEBO_PLUGIN_PATH',
            '/usr/lib/x86_64-linux-gnu/gazebo-11/plugins:/opt/ros/humble/lib'),
        SetEnvironmentVariable('DISPLAY', ':0'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                '/opt/ros/humble/share/gazebo_ros/launch/gazebo.launch.py'),
            launch_arguments={
                'world': os.path.join(pkg, 'worlds', 'lab_room.world'),
                'verbose': 'false'
            }.items()),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'use_sim_time': True,
                'robot_description': robot_description
            }]),

        # Spawn robot after Gazebo loads
        TimerAction(period=5.0, actions=[
            Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                arguments=[
                    '-entity', 'cobot',
                    '-topic', 'robot_description',
                    '-x', '0', '-y', '0', '-z', '0.1'
                ],
                output='screen')
        ]),

        # SLAM toolbox — mapping mode
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            parameters=[
                os.path.join(pkg, 'config', 'slam_params.yaml'),
                {'use_sim_time': True}
            ],
            output='screen'),

        # Auto-save map every 30s to both /tmp and maps folder
        TimerAction(period=30.0, actions=[
            ExecuteProcess(
                cmd=[
                    'bash', '-c',
                    f'ros2 run nav2_map_server map_saver_cli -f /tmp/lab_map && '
                    f'cp /tmp/lab_map.pgm {maps_dir}/lab_map.pgm && '
                    f'cp /tmp/lab_map.yaml {maps_dir}/lab_map.yaml && '
                    f'sed -i "s|image: lab_map.pgm|image: {maps_dir}/lab_map.pgm|" {maps_dir}/lab_map.yaml && '
                    f'echo "Map auto-saved to {maps_dir}"'
                ],
                output='screen'
            )
        ]),
    ])