#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, HistoryPolicy
from std_msgs.msg import Float32, String, Int32, Empty
import json
import os
import random

# ────────────────────────────────────────────────────────────────────────────────
# Change here: point to your “sample” JSON file
TABLE_DATA_FILE = "sample-table-json.txt"
# ────────────────────────────────────────────────────────────────────────────────


class SimulationManagerNode(Node):
    def __init__(self):
        super().__init__('simulation_manager')

        # ─── State Variables ────────────────────────────────────────────────────────
        self.current_mode       = ""
        self.table_locations    = {}     # loaded from TABLE_DATA_FILE
        self.last_boot_status   = {"checks": [], "overall_status": "NOT READY", "message": ""}
        self.reset_base_ack     = ""
        self.add_table_ack      = ""
        self.return_base_ack    = ""
        self.delivery_status    = ""

        # ─── QoS for transient-local (latched) publishers ───────────────────────────
        latched_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )

        # ─── Publishers ─────────────────────────────────────────────────────────────
        self.battery_pub          = self.create_publisher(String, '/battery_status',    10)
        self.boot_pub             = self.create_publisher(String,   '/boot_check',        latched_qos)
        self.mode_pub             = self.create_publisher(String,   '/set_mode',          latched_qos)
        self.table_list_pub       = self.create_publisher(String,   '/table_list',        latched_qos)
        self.reset_base_ack_pub   = self.create_publisher(String,   '/reset_base_loc_ack', latched_qos)
        self.add_table_ack_pub    = self.create_publisher(String,   '/add_table_ack',      latched_qos)
        self.return_base_ack_pub  = self.create_publisher(String,   '/return_base_ack',    latched_qos)
        self.delivery_status_pub  = self.create_publisher(String,   '/delivery_status',    latched_qos)

        # ─── Timers ───────────────────────────────────────────────────────────────────
        self.create_timer(1.0, self._battery_timer_callback)
        self.create_timer(1.0, self._publish_mode_callback)
        self.create_timer(5.0, self._publish_last_boot_status)
        self.create_timer(1.0, self._publish_reset_base_ack)
        self.create_timer(1.0, self._publish_add_table_ack)
        self.create_timer(1.0, self._publish_return_base_ack)

        # ─── Override Parameters ─────────────────────────────────────────────────────
        for comp in ("lidar","camera","imu","motors"):
            self.declare_parameter(f"boot_check_override_{comp}", "")

        # ─── Subscribers ──────────────────────────────────────────────────────────────
        self.create_subscription(String, '/set_parameter',   self._set_parameter_callback,     10)
        self.create_subscription(String, '/set_mode',        self._set_mode_callback,          10)
        self.create_subscription(String, '/save_point',      self._add_table_callback,         10)
        self.create_subscription(String, '/goto_point',      self._move_to_table_callback,     10)
        self.create_subscription(String, '/reset_base_loc',  self._reset_base_loc_callback,    10)
        self.create_subscription(String, '/return_base',     self._return_base_callback,       10)
        self.create_subscription(Empty,  '/get_table_list', self._get_table_list_callback,    10)

        # ─── Initial Actions ─────────────────────────────────────────────────────────
        # 1) Publish the initial mode so that any late-joining subscriber can latch it:
        self.mode_pub.publish(String(data=self.current_mode))

        # 2) Load existing table data (if the file exists)
        self._load_table_data()

        self.get_logger().info("SimulationManagerNode initialized.")

    # ─── Timer Callbacks ───────────────────────────────────────────────────────────
    def _battery_timer_callback(self):
        # Battery state: 0 = discharging, 1 = charging
        if not hasattr(self, 'battery_state'):
            self.battery_state = 0  # initialize
            self.battery_level = 100.0

        # Simulate charging/discharging
        if self.battery_state == 0:
            self.battery_level -= 0.5
            if self.battery_level <= 0.0:
                self.battery_level = 0.0
                self.battery_state = 1  # switch to charging
        else:
            self.battery_level += 0.5
            if self.battery_level >= 100.0:
                self.battery_level = 100.0
                self.battery_state = 0  # switch to discharging

        # Simulated voltage and current based on percentage
        voltage = round(24.0 + (self.battery_level / 100.0) * 2.0, 2)
        current = round(-0.6 if self.battery_state == 0 else 0.8, 2)

        battery_msg = {
            "percentage": round(self.battery_level, 1),
            "state": self.battery_state,
            "voltage": voltage,
            "current": current
        }

        self.battery_pub.publish(String(data=json.dumps(battery_msg)))

    def _publish_mode_callback(self):
        self.mode_pub.publish(String(data=self.current_mode))

    def _publish_last_boot_status(self):
        self.boot_pub.publish(String(data=json.dumps(self.last_boot_status)))

    def _publish_reset_base_ack(self):
        self.reset_base_ack_pub.publish(String(data=self.reset_base_ack))

    def _publish_add_table_ack(self):
        self.add_table_ack_pub.publish(String(data=self.add_table_ack))

    def _publish_return_base_ack(self):
        self.return_base_ack_pub.publish(String(data=self.return_base_ack))

    # ─── Parameter Update ──────────────────────────────────────────────────────────
    def _set_parameter_callback(self, msg: String):
        try:
            data = json.loads(msg.data)
            name = data.get("param")
            val  = data.get("value")
            if not name:
                raise ValueError("missing 'param'")

            if name == "reset_base_ack":
                self.reset_base_ack = str(val)
            elif name == "add_table_ack":
                self.add_table_ack = str(val)
            elif name == "return_base_ack":
                self.return_base_ack = str(val)
            elif name == "last_boot_status":
                self.last_boot_status = json.loads(val) if isinstance(val, str) else val
            elif name == "delivery_status":
                self.delivery_status = str(val)
                # publish immediately once
                self.delivery_status_pub.publish(String(data=self.delivery_status))
            elif name == "ops_mode":
                self.current_mode = str(val)
            else:
                # treat everything else as a generic ROS parameter
                self.set_parameters([Parameter(name, Parameter.Type.STRING, val)])

            self.get_logger().info(f"Parameter '{name}' set to '{val}'")
        except Exception as e:
            self.get_logger().error(f"Parameter update failed: {e}")

    # ─── Operation Mode ─────────────────────────────────────────────────────────────
    def _set_mode_callback(self, msg: String):
        self.current_mode = msg.data.strip()

    # ─── Table Management ───────────────────────────────────────────────────────────
    def _add_table_callback(self, msg: String):
        """
        Called when a String message arrives on '/save_point'.  msg.data is expected
        to contain a table ID (e.g. "1" or "2").  We then generate random
        position/orientation (values between 1 and 10), store them under that key,
        and write back to our JSON file.
        """
        tid = msg.data.strip()
        if not tid:
            self.get_logger().warn("Received empty table ID on /save_point.")
            return

        # Generate random payload for position + orientation (all between 1.0 and 10.0)
        rand_pos  = {
            "x": round(random.uniform(1.0, 10.0), 4),
            "y": round(random.uniform(1.0, 10.0), 4),
            "z": round(random.uniform(1.0, 10.0), 4),
        }
        rand_orient = {
            "x": round(random.uniform(1.0, 10.0), 4),
            "y": round(random.uniform(1.0, 10.0), 4),
            "z": round(random.uniform(1.0, 10.0), 4),
            "w": round(random.uniform(1.0, 10.0), 4),
        }

        # Insert/update into our in-memory dict
        self.table_locations[tid] = {
            "position":    rand_pos,
            "orientation": rand_orient,
        }

        # Acknowledge to anyone listening on '/add_table_ack'
        # self.add_table_ack = f"Stored table {tid}"

        # Persist to disk
        self._save_table_data()

    def _get_table_list_callback(self, msg: Empty):
        """
        Triggered on '/get_table_list'.  We simply publish the list of numeric keys
        in self.table_locations to '/table_list'.
        """
        self._load_table_data()
        self._publish_table_list()

    def _publish_table_list(self):
        """
        Build a list of all numeric table IDs currently stored.  (Filters out
        any non-digit keys like "Base".)  Publishes JSON-dumped list of integers
        to '/table_list' (e.g. [1, 2, 5]).
        """
        all_keys = list(self.table_locations.keys())
        # Keep only numeric IDs
        numeric_ids = [int(k) for k in all_keys if k.isdigit()]

        # Sort them (optional, but keeps the output consistent)
        numeric_ids.sort()

        # Publish as JSON array of strings, e.g. ["1","2","5"]
        payload = json.dumps(numeric_ids)
        self.table_list_pub.publish(String(data=payload))

    def _save_table_data(self):
        """
        Write self.table_locations out to TABLE_DATA_FILE in JSON format.
        """
        try:
            with open(TABLE_DATA_FILE, 'w') as f:
                json.dump(self.table_locations, f, indent=2)
        except Exception as e:
            self.get_logger().error(f"Failed saving tables to '{TABLE_DATA_FILE}': {e}")

    def _load_table_data(self):
        """
        On startup, if TABLE_DATA_FILE exists, load it into self.table_locations.
        """
        if os.path.exists(TABLE_DATA_FILE):
            try:
                with open(TABLE_DATA_FILE, 'r') as f:
                    self.table_locations = json.load(f)
            except Exception as e:
                self.get_logger().error(f"Failed loading tables from '{TABLE_DATA_FILE}': {e}")
        else:
            # File does not exist → start with empty dict
            self.table_locations = {}

    # ─── Delivery Logic (unchanged from your original) ─────────────────────────────
    def _move_to_table_callback(self, msg: String):
        tid = msg.data.strip()
        if tid not in self.table_locations:
            self.get_logger().warn(f"Table {tid} not found")
            return
        # (You can add movement logic here if needed.)

    # ─── Reset & Return Base ───────────────────────────────────────────────────────
    def _reset_base_loc_callback(self, msg: String):
        self.reset_base_ack = "Base reset"

    def _return_base_callback(self, msg: String):
        self.return_base_ack = "Returning to base"
        # Example: reset to "At base" after 1 second
        # threading.Thread(
        #     target=lambda: (time.sleep(1.0), setattr(self, "return_base_ack", "At base")),
        #     daemon=True
        # ).start()


def main(args=None):
    rclpy.init(args=args)
    node = SimulationManagerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
