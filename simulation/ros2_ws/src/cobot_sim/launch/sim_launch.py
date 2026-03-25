from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg = get_package_share_directory('cobot_sim')
    return LaunchDescription([
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
                'robot_description': open(
                    os.path.join(pkg, 'urdf', 'cobot.urdf.xacro')).read()
            }]),
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            parameters=[
                os.path.join(pkg, 'config', 'slam_params.yaml'),
                {'use_sim_time': True}
            ],
            output='screen'),
    ])