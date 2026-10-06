import socket
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range

class UltrasonicBridge(Node):
    def __init__(self):
        super().__init__('ultrasonic_bridge')

        # --- TCP connection to the Pico 2 W ---
        self.pico_ip = '192.168.0.31'
        self.pico_port = 4002
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.get_logger().info(f'Connecting to Pico at {self.pico_ip}:{self.pico_port}...')
        self.sock.connect((self.pico_ip, self.pico_port))
        self.get_logger().info('Connected to Pico!')

        self.buffer = ''  # holds partial lines between reads

        # --- ROS2 publisher ---
        self.publisher_ = self.create_publisher(Range, '/ultrasonic_distance', 10)

        # Poll the socket regularly to check for new data
        self.timer = self.create_timer(0.05, self.read_and_publish)

    def read_and_publish(self):
        try:
            data = self.sock.recv(1024).decode('utf-8')
        except BlockingIOError:
            return
        if not data:
            return

        self.buffer += data
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            line = line.strip()
            if not line:
                continue
            try:
                distance_cm = float(line)
            except ValueError:
                self.get_logger().warn(f'Could not parse: {line}')
                continue

            msg = Range()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = 'ultrasonic_sensor'
            msg.radiation_type = Range.ULTRASOUND
            msg.field_of_view = 0.26  # ~15 degrees, adjust if you know the sensor's actual FOV
            msg.min_range = 0.02      # meters, adjust to your sensor's spec
            msg.max_range = 4.0       # meters, adjust to your sensor's spec
            msg.range = distance_cm / 100.0  # convert cm to meters

            self.publisher_.publish(msg)
            self.get_logger().info(f'Published: {distance_cm} cm')


def main(args=None):
    rclpy.init(args=args)
    node = UltrasonicBridge()
    node.sock.setblocking(False)  # so recv() doesn't hang the node
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
