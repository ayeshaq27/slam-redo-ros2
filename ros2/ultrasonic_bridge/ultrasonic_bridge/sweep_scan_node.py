import math
import socket

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

# Must match the sweep settings in sweep_wifi.ino
MIN_SERVO = 30      # servo angle pointing right
MAX_SERVO = 150     # servo angle pointing left
STEP = 15
NO_ECHO_CM = 300.0  # Freenove's Get_Sonar() returns 300 when nothing echoes back


class SweepScanNode(Node):
    def __init__(self):
        super().__init__('sweep_scan_node')

        # --- Parameters: settings you can change at launch with --ros-args -p name:=value ---
        self.declare_parameter('pico_ip', '10.105.52.74')
        self.declare_parameter('pico_port', 4002)
        pico_ip = self.get_parameter('pico_ip').value
        pico_port = self.get_parameter('pico_port').value

        # --- TCP connection to the Pico ---
        self.get_logger().info(f'Connecting to Pico at {pico_ip}:{pico_port}...')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((pico_ip, pico_port))
        self.sock.setblocking(False)  # so recv() doesn't freeze the node
        self.get_logger().info('Connected to Pico!')

        self.buffer = ''     # holds partial lines between reads
        self.readings = {}   # servo angle -> range in metres, for the sweep in progress

        # --- ROS2 publisher ---
        self.publisher_ = self.create_publisher(LaserScan, '/scan', 10)
        self.timer = self.create_timer(0.05, self.read_socket)

    def read_socket(self):
        try:
            data = self.sock.recv(1024).decode('utf-8')
        except BlockingIOError:
            return  # nothing new yet
        if not data:
            return

        self.buffer += data
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            self.handle_line(line.strip())

    def handle_line(self, line):
        if not line:
            return
        try:
            angle_str, dist_str = line.split(',')
            servo_angle = int(angle_str)
            distance_cm = float(dist_str)
        except ValueError:
            self.get_logger().warn(f'Could not parse: {line}')
            return

        # 300 cm (or a bad reading) means "nothing in range" -> infinity, the LaserScan convention
        if distance_cm >= NO_ECHO_CM or distance_cm <= 0:
            range_m = float('inf')
        else:
            range_m = distance_cm / 100.0
        self.readings[servo_angle] = range_m

        # Reaching either end of the sweep completes a scan
        if servo_angle in (MIN_SERVO, MAX_SERVO):
            if len(self.readings) > 1:
                self.publish_scan()
            # The end reading is also the first reading of the next sweep
            self.readings = {servo_angle: range_m}

    def publish_scan(self):
        # LaserScan lists ranges from angle_min to angle_max, i.e. right to left.
        # Servo 30 (right) -> -60 deg, servo 150 (left) -> +60 deg, so ascending servo order works
        # for both sweep directions.
        servo_angles = range(MIN_SERVO, MAX_SERVO + 1, STEP)
        ranges = [self.readings.get(a, float('nan')) for a in servo_angles]  # nan = no reading taken

        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'ultrasonic_sensor'
        msg.angle_min = math.radians(MIN_SERVO - 90)   # -60 deg
        msg.angle_max = math.radians(MAX_SERVO - 90)   # +60 deg
        msg.angle_increment = math.radians(STEP)       # 15 deg
        msg.time_increment = 0.0
        msg.scan_time = 0.0
        msg.range_min = 0.02
        msg.range_max = NO_ECHO_CM / 100.0             # 3.0 m
        msg.ranges = ranges

        self.publisher_.publish(msg)
        hits = sum(1 for r in ranges if math.isfinite(r))
        self.get_logger().info(f'Published scan: {hits}/{len(ranges)} readings hit something')


def main(args=None):
    rclpy.init(args=args)
    node = SweepScanNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.sock.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
