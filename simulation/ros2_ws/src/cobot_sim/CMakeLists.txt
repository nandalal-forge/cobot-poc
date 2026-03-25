cmake_minimum_required(VERSION 3.8)
project(cobot_sim)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

install(DIRECTORY launch urdf worlds config nodes maps
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  nodes/mqtt_bridge.py
  nodes/waypoint_executor.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()