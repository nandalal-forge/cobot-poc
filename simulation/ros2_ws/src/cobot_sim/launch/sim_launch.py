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

    return LaunchDescription([
        # Fix Gazebo environment
        SetEnvironmentVariable('GAZEBO_MODEL_PATH',
            '/usr/share/gazebo-11/models'),
        SetEnvironmentVariable('GAZEBO_PLUGIN_PATH',
            '/usr/lib/x86_64-linux-gnu/gazebo-11/plugins:/opt/ros/humble/lib'),
        SetEnvironmentVariable('DISPLAY', ':0'),

        # Launch Gazebo with lab room world
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                '/opt/ros/humble/share/gazebo_ros/launch/gazebo.launch.py'),
            launch_arguments={
                'world': os.path.join(pkg, 'worlds', 'lab_room.world'),
                'verbose': 'false'
            }.items()),

        # Robot state publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'use_sim_time': True,
                'robot_description': robot_description
            }]),

        # Spawn robot after 5s (Gazebo needs time to load)
        TimerAction(
            period=5.0,
            actions=[
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

        # SLAM toolbox for mapping + localization
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            parameters=[
                os.path.join(pkg, 'config', 'slam_params.yaml'),
                {'use_sim_time': True}
            ],
            output='screen'),

        # Auto-set initial pose after 10s (after SLAM map frame exists)
        TimerAction(
            period=10.0,
            actions=[
                ExecuteProcess(
                    cmd=[
                        'ros2', 'topic', 'pub', '--once',
                        '/initialpose',
                        'geometry_msgs/msg/PoseWithCovarianceStamped',
                        '{"header": {"frame_id": "map"}, "pose": {"pose": {"position": {"x": 0.0, "y": 0.0, "z": 0.0}, "orientation": {"w": 1.0}}}}'
                    ],
                    output='screen'
                )
            ]),
    ])