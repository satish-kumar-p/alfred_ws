
# ROS 2 Commands Reference for Robot Operations

## 1. Reset Base Location

**Command:**
```bash
ros2 topic pub /reset_base_loc std_msgs/Empty "{}" --once
```

**Check Acknowledgement:**
```bash
ros2 topic echo /reset_base_loc_ack std_msgs/String
```

**Set ACK Value:**
```bash
ros2 topic pub /set_parameter std_msgs/String '{data: "{\"param\":\"reset_base_ack\",\"value\":\"Success\"}"}' --once
```

## 2. Return to Base

**Command:**
```bash
ros2 topic pub /return_base std_msgs/Empty "{}" --once
```

**Check Acknowledgement:**
```bash
ros2 topic echo /return_base_ack std_msgs/String
```

**Set ACK Value:**
```bash
ros2 topic pub /set_parameter std_msgs/String '{data: "{\"param\":\"return_base_ack\",\"value\":\"Success\"}"}' --once
```

## 3. Add Table

**Command:**
```bash
ros2 topic pub /save_point std_msgs/Int32 "{data: 1}" --once
```

**Check Acknowledgement:**
```bash
ros2 topic echo /add_table_ack std_msgs/String
```

**Set ACK Value:**
```bash
ros2 topic pub /set_parameter std_msgs/String '{data: "{\"param\":\"add_table_ack\",\"value\":\"Success\"}"}' --once
```

## 4. View Table List

**Command:**
```bash
ros2 topic echo /table_list std_msgs/String
```

## 5. Set Operation Mode

**Command:**
```bash
ros2 topic pub /set_mode std_msgs/String "{data: \"delivery\"}" --once
```

**Check Current Mode:**
```bash
ros2 topic echo /current_mode std_msgs/String
```

**Set ops_mode Parameter:**

*training:*
```bash
ros2 topic pub /set_parameter std_msgs/String '{data: "{\"param\":\"ops_mode\",\"value\":\"training\"}"}' --once
```

*delivery:*
```bash
ros2 topic pub /set_parameter std_msgs/String '{data: "{\"param\":\"ops_mode\",\"value\":\"delivery\"}"}' --once
```

## 6. Boot Check

**View Boot Check Result:**
```bash
ros2 topic echo /boot_check std_msgs/String
```

**Set Boot Status Parameter:**

*SUCCESS:*
```bash
ros2 topic pub /set_parameter std_msgs/String '{data: "{\"param\":\"last_boot_status\",\"value\":\"{\\\"checks\\\":[] ,\\\"overall_status\\\":\\\"OK\\\",\\\"message\\\":\\\"Success\\\"}\"}"}' --once
```

*FAIL:*
```bash
ros2 topic pub /set_parameter std_msgs/String '{data: "{\"param\":\"last_boot_status\",\"value\":\"{\\\"checks\\\":[] ,\\\"overall_status\\\":\\\"FAIL\\\",\\\"message\\\":\\\"Some systems failed\\\"}\"}"}' --once
```

*NOT READY:*
```bash
ros2 topic pub /set_parameter std_msgs/String '{data: "{\"param\":\"last_boot_status\",\"value\":\"{\\\"checks\\\":[] ,\\\"overall_status\\\":\\\"NOT READY\\\",\\\"message\\\":\\\"Initializing\\\"}\"}"}' --once
```

## 7. Delivery Status (Example Values)

- `moving`
- `delivered`

*moving:*
```bash
ros2 topic pub /set_parameter std_msgs/String '{data: "{\"param\":\"delivery_status\",\"value\":\"moving\"}"}' --once
```

*delivered:*
```bash
ros2 topic pub /set_parameter std_msgs/String '{data: "{\"param\":\"delivery_status\",\"value\":\"delivered\"}"}' --once
```

---

## List of Parameters

- `reset_base_ack`
- `add_table_ack`
- `return_base_ack`
- `last_boot_status`
- `ops_mode`
- `delivery_status` (values: `moving`, `delivered`)
