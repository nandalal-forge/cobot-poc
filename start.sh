#!/bin/bash
set -e

echo "=========================================="
echo " Cobot POC — Full System Start"
echo "=========================================="

export DISPLAY=:0
export PYTHONPATH=$PYTHONPATH:/home/forge/cobot-poc

COBOT_DIR=/home/forge/cobot-poc
WS_DIR=$COBOT_DIR/simulation/ros2_ws
LOG_DIR=$COBOT_DIR/logs
mkdir -p $LOG_DIR

# Source ROS
source /usr/share/gazebo/setup.bash
source /opt/ros/humble/setup.bash
source $WS_DIR/install/setup.bash

echo "[1/6] Starting Docker services..."
cd $COBOT_DIR/infra && docker compose up -d
sleep 5
echo "      Docker services up"

echo "[2/6] Starting Gazebo simulation..."
gnome-terminal --title="SIM" -- bash -c "
  source /usr/share/gazebo/setup.bash
  source /opt/ros/humble/setup.bash
  source $WS_DIR/install/setup.bash
  export DISPLAY=:0
  export PYTHONPATH=$PYTHONPATH:/home/forge/cobot-poc
  ros2 launch cobot_sim sim_launch.py 2>&1 | tee $LOG_DIR/sim.log
" &
echo "      Waiting 20s for Gazebo + robot spawn..."
sleep 20

echo "[3/6] Starting Nav2..."
gnome-terminal --title="NAV2" -- bash -c "
  source /opt/ros/humble/setup.bash
  ros2 launch nav2_bringup navigation_launch.py \
    use_sim_time:=true \
    params_file:=$COBOT_DIR/simulation/ros2_ws/src/cobot_sim/config/nav2_params.yaml \
    2>&1 | tee $LOG_DIR/nav2.log
" &
echo "      Waiting 15s for Nav2..."
sleep 15

echo "[4/6] Starting MQTT bridge..."
gnome-terminal --title="MQTT" -- bash -c "
  source /opt/ros/humble/setup.bash
  source $WS_DIR/install/setup.bash
  export PYTHONPATH=$PYTHONPATH:/home/forge/cobot-poc
  ros2 run cobot_sim mqtt_bridge.py 2>&1 | tee $LOG_DIR/mqtt.log
" &
sleep 3

echo "[5/6] Starting waypoint executor..."
gnome-terminal --title="WAYPOINTS" -- bash -c "
  source /opt/ros/humble/setup.bash
  source $WS_DIR/install/setup.bash
  ros2 run cobot_sim waypoint_executor.py 2>&1 | tee $LOG_DIR/waypoints.log
" &
sleep 3

echo "[6/6] Starting FastAPI backend..."
gnome-terminal --title="API" -- bash -c "
  cd $COBOT_DIR
  export PYTHONPATH=$PYTHONPATH:/home/forge/cobot-poc
  uvicorn backend.app.main:app --reload --port 8000 2>&1 | tee $LOG_DIR/api.log
" &
sleep 3

echo ""
echo "=========================================="
echo " All systems started!"
echo "=========================================="
echo " Gazebo:   Running (check SIM terminal)"
echo " Nav2:     Running (check NAV2 terminal)"
echo " API:      http://localhost:8000"
echo " Docs:     http://localhost:8000/docs"
echo " Grafana:  http://localhost:3001"
echo ""
echo " To start cleaning session:"
echo " curl -X POST http://localhost:8000/api/sessions/start \\"
echo "   -H 'Content-Type: application/json' \\"
echo "   -d '{\"cobot_id\": \"cobot_01\"}'"
echo ""
echo " To view camera:"
echo " ros2 run cobot_sim camera_viewer.py"
echo "=========================================="