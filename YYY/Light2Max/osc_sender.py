from pythonosc.udp_client import SimpleUDPClient


class OSCClient:
    def __init__(self, host="127.0.0.1", port=8000):
        self.client = SimpleUDPClient(host, port)

    def send_light(self, x_norm, y_norm, area_norm, brightness):
        """Send values to address /light: x, y, area, brightness

        All values should be floats (0-1 for normalized).
        """
        try:
            self.client.send_message("/light", [float(x_norm), float(y_norm), float(area_norm), float(brightness)])
        except Exception:
            # Keep tolerant to network errors
            pass
