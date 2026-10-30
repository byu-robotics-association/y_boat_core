import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


def make_handler(node):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
            self.end_headers()
            try:
                while True:
                    jpg = node.latest_jpeg
                    if jpg:
                        self.wfile.write(
                            b"--frame\r\nContent-Type: image/jpeg\r\n"
                            b"Content-Length: %d\r\n\r\n" % len(jpg)
                        )
                        self.wfile.write(jpg + b"\r\n")
                    time.sleep(0.1)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, *args):
            pass

    return Handler


class ImageViewerNode(Node):
    """Subscribes to an Image topic and shows it as a file, a window, or a web stream."""

    def __init__(self):
        super().__init__("image_viewer_node")
        self.declare_parameter("topic", "camera/image_rect") #camera/image_rect or camera/image_raw
        self.declare_parameter("mode", "file")  # file | window | http
        self.declare_parameter("output_path", "/workspace/src/latest.jpg")
        self.declare_parameter("save_every_sec", 0.5)
        self.declare_parameter("http_port", 8080)

        self._mode = self.get_parameter("mode").value
        if self._mode not in ("file", "window", "http"):
            raise ValueError("mode must be file, window, or http")

        self._bridge = CvBridge()
        self._path = self.get_parameter("output_path").value
        self._period = self.get_parameter("save_every_sec").value
        self._last_save = 0.0
        self.latest_jpeg = None

        if self._mode == "http":
            port = self.get_parameter("http_port").value
            server = ThreadingHTTPServer(("0.0.0.0", port), make_handler(self))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self.get_logger().info(f"Serving stream at http://localhost:{port}")

        topic = self.get_parameter("topic").value
        self.create_subscription(Image, topic, self._on_image, 1)
        self.get_logger().info(f"Viewing '{topic}' in '{self._mode}' mode")

    def _on_image(self, msg: Image) -> None:
        frame = self._bridge.imgmsg_to_cv2(msg, "bgr8")

        if self._mode == "window":
            cv2.imshow("camera", frame)
            cv2.waitKey(1)

        elif self._mode == "http":
            ok, buf = cv2.imencode(".jpg", frame)
            if ok:
                self.latest_jpeg = buf.tobytes()

        else:  # file
            now = time.time()
            if now - self._last_save < self._period:
                return
            self._last_save = now
            tmp = self._path + ".tmp.jpg"
            cv2.imwrite(tmp, frame)
            os.replace(tmp, self._path)  # atomic, so you never open a half-written file


def main():
    rclpy.init()
    node = ImageViewerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()