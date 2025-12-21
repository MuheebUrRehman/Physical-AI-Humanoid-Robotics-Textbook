#!/usr/bin/env python3
import rclpy  # type: ignore
from rclpy.node import Node  # type: ignore
from std_msgs.msg import String  # type: ignore

class HeartbeatPublisher(Node):
    """
    A simple ROS 2 node that publishes a heartbeat message every second.
    """
    def __init__(self):
        super().__init__('heartbeat_publisher')
        self.publisher_ = self.create_publisher(String, 'heartbeat', 10)
        self.timer_period = 1.0  # seconds
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.get_logger().info('Heartbeat publisher node has been started.')

    def timer_callback(self):
        msg = String()
        msg.data = f'Pulse from {self.get_name()} at {self.get_clock().now().to_msg()}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    
    heartbeat_publisher = HeartbeatPublisher()
    
    try:
        rclpy.spin(heartbeat_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        # Destroy the node explicitly
        # (optional - Done automatically when node is garbage collected)
        heartbeat_publisher.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
