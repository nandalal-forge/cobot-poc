cmake_minimum_required(VERSION 3.8)
project(cobot_sim)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch urdf worlds config nodes
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
