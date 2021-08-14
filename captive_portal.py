import gc
import network
import ubinascii as binascii
import uselect as select
import utime as time

from captive_dns import DNSServer
from captive_http import HTTPServer
from credentials import Creds


class CaptivePortal:
    AP_IP = "192.168.4.1"
    AP_OFF_DELAY = const(10 * 1000)
    MAX_CONN_ATTEMPTS = 10

    def __init__(self, callback_for_measurements, callback_for_lightlevel, callback_for_update, essid=None):
        self.callback_for_measurements = callback_for_measurements
        self.callback_for_lightlevel = callback_for_lightlevel
        self.callback_for_update = callback_for_update
        self.local_ip = self.AP_IP
        self.sta_if = network.WLAN(network.STA_IF)
        self.ap_if = network.WLAN(network.AP_IF)

        mac = str(binascii.hexlify(self.sta_if.config("mac"))).upper()[2:-1]
        self.mac_address = mac[0:2] + ":" + mac[2:4] + ":" + mac[4:6] + ":" + \
                           mac[6:8] + ":" + mac[8:10] + ":" + mac[10:12]

        if essid is None:
            essid = b"Tegschtuhr-%s" % binascii.hexlify(self.ap_if.config("mac")[-3:])
        self.essid = essid

        self.creds = Creds()

        self.dns_server = None
        self.http_server = None
        self.poller = select.poll()

        self.conn_time_start = None

    def start_access_point(self):
        # sometimes need to turn off AP before it will come up properly
        self.ap_if.active(False)
        while not self.ap_if.active():
            print("Waiting for access point to turn on")
            self.ap_if.active(True)
            time.sleep(1)
        # IP address, netmask, gateway, DNS
        self.ap_if.ifconfig(
            (self.local_ip, "255.255.255.0", self.local_ip, self.local_ip)
        )
        self.ap_if.config(essid=self.essid, authmode=network.AUTH_OPEN)
        print("AP mode configured:", self.ap_if.ifconfig())

    def connect_to_wifi(self):
        print(
            "Trying to connect to SSID '{:s}' with password {:s}".format(
                self.creds.ssid, "*"*len(self.creds.password)
            )
        )

        # initiate the connection
        self.sta_if.active(True)
        self.sta_if.config(dhcp_hostname="tegschtuhr")
        self.sta_if.connect(self.creds.ssid, self.creds.password)

        attempts = 1
        while attempts <= self.MAX_CONN_ATTEMPTS:
            if not self.sta_if.isconnected():
                print("Connection attempt {:d}/{:d} ...".format(attempts, self.MAX_CONN_ATTEMPTS))
                time.sleep(2)
                attempts += 1
            else:
                self.local_ip = self.sta_if.ifconfig()[0]
                print("Connected to {:s} with IP {:s}".format(self.creds.ssid, self.local_ip))
                return True

        print(
            "Failed to connect to {:s} with {:s}. WLAN status={:d}".format(
                self.creds.ssid, self.creds.password, self.sta_if.status()
            )
        )
        # forget the credentials since they didn't work, and turn off station mode
        self.creds.remove()
        self.sta_if.active(False)
        return False

    def check_valid_wifi(self):
        if not self.sta_if.isconnected():
            if self.creds.load().is_valid():
                # have credentials to connect, but not yet connected
                # return value based on whether the connection was successful
                return self.connect_to_wifi()
            # not connected, and no credentials to connect yet
            return False

        if not self.ap_if.active():
            # access point is already off; do nothing
            return False

        # already connected to WiFi, so turn off Access Point after a delay
        if self.conn_time_start is None:
            self.conn_time_start = time.ticks_ms()
            remaining = self.AP_OFF_DELAY
        else:
            remaining = self.AP_OFF_DELAY - time.ticks_diff(
                time.ticks_ms(), self.conn_time_start
            )
            if remaining <= 0:
                self.ap_if.active(False)
                print("Turned off access point")
        return False

    def list_networks(self):
        if self.sta_if.active():
            was_active = True
        else:
            was_active = False
            self.sta_if.active(True)
        networks = self.sta_if.scan()
        if not was_active:
            self.sta_if.active(False)
        print(networks)
        return networks

    def start_http_server(self):
        if self.http_server is None:
            self.http_server = HTTPServer(self.poller, self.local_ip, self.mac_address, self.callback_for_measurements, self.list_networks, self.callback_for_lightlevel, self.callback_for_update)
            print("Configured HTTP server")

    def captive_portal(self, timeout):
        print("Starting captive portal")
        ret = False
        start_time = time.ticks_ms()
        self.start_access_point()

        self.start_http_server()
        if self.dns_server is None:
            self.dns_server = DNSServer(self.poller, self.local_ip)
            print("Configured DNS server")

        try:
            while time.ticks_ms() - start_time < timeout:
                gc.collect()
                # check for socket events and handle them
                if self.handle_socket_events():
                    start_time = time.ticks_ms()  # increase timeout on communication

                if self.check_valid_wifi():
                    print("Connected to WiFi!")
                    self.http_server.set_ip(self.local_ip, self.creds.ssid)
                    self.dns_server.stop(self.poller)
                    ret = True
                    break

        except KeyboardInterrupt:
            print("Captive portal stopped")
        self.cleanup()

        return ret

    def handle_socket_events(self):
        for response in self.poller.ipoll(100):
            sock, event, *others = response
            if self.dns_server is not None and self.handle_dns(sock, event, others):
                return True
            if self.http_server is not None:
                return self.handle_http(sock, event, others)

    def handle_dns(self, sock, event, others):
        if sock is self.dns_server.sock:
            # ignore UDP socket hangups
            if event == select.POLLHUP:
                return True
            self.dns_server.handle(sock, event, others)
            return True
        return False

    def handle_http(self, sock, event, others):
        return self.http_server.handle(sock, event, others)

    def cleanup(self):
        print("Cleaning up")
        if self.dns_server:
            self.dns_server.stop(self.poller)
        gc.collect()

    def try_connect_from_file(self):
        if self.creds.load().is_valid():
            if self.connect_to_wifi():
                self.start_http_server()
                return True

        # WiFi Connection failed - remove credentials from disk
        self.creds.remove()
        return False

    def start(self, timeout):
        # turn off station interface to force a reconnect
        self.sta_if.active(False)
        if not self.try_connect_from_file():
            return self.captive_portal(timeout)  # Blocking Captive Portal
        return True
