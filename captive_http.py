import uerrno
import uio
import uselect as select
import usocket as socket
import ujson

from collections import namedtuple
from credentials import Creds

import common

WriteConn = namedtuple("WriteConn", ["body", "buff", "buffmv", "write_range"])
ReqInfo = namedtuple("ReqInfo", ["type", "path", "params", "host"])

from server import Server

import gc

import re

_charref = re.compile(r'%([0-9a-fA-F][0-9a-fA-F])')

class HTTPServer(Server):
    def __init__(self, poller, local_ip, mac_address):
        super().__init__(poller, 80, socket.SOCK_STREAM, "HTTP Server")
        if type(local_ip) is bytes:
            self.local_ip = local_ip
        else:
            self.local_ip = local_ip.encode()
        self.mac_address = mac_address
        self.request = dict()
        self.conns = dict()
        self.routes = {b"/": b"./index.html",
                       b"/get_info": self.get_info,
                       b"/login": self.login,
                       b"/settings": self.settings}

        self.ssid = None

        # queue up to 5 connection requests before refusing
        self.sock.listen(5)
        self.sock.setblocking(False)

    def set_ip(self, new_ip, new_ssid):
        """update settings after connected to local WiFi"""

        self.local_ip = new_ip.encode()
        self.ssid = new_ssid
        # self.routes = {b"/": self.connected}

    @micropython.native
    def handle(self, sock, event, others):
        if sock is self.sock:
            # client connecting on port 80, so spawn off a new
            # socket to handle this connection
            print("- Accepting new HTTP connection")
            self.accept(sock)
        elif event & select.POLLIN:
            # socket has data to read in
            print("- Reading incoming HTTP data")
            self.read(sock)
        elif event & select.POLLOUT:
            # existing connection has space to send more data
            print("- Sending outgoing HTTP data")
            self.write_to(sock)

    def accept(self, server_sock):
        """accept a new client request socket and register it for polling"""

        try:
            client_sock, addr = server_sock.accept()
        except OSError as e:
            if e.args[0] == uerrno.EAGAIN:
                return

        client_sock.setblocking(False)
        client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.poller.register(client_sock, select.POLLIN)

    def parse_request(self, req):
        """parse a raw HTTP request to get items of interest"""

        req_lines = req.split(b"\r\n")
        req_type, full_path, http_ver = req_lines[0].split(b" ")
        path = full_path.split(b"?")
        base_path = path[0]
        query = path[1] if len(path) > 1 else None
        try:
            query_params = (
                {
                    key: self.unescape(val)
                    for key, val in [param.split(b"=") for param in query.split(b"&")]
                }
                if query
                else {}
            )
        except ValueError:
            query_params = ()
        host = [line.split(b": ")[1] for line in req_lines if b"Host:" in line][0]

        return ReqInfo(req_type, base_path, query_params, host)

    def unescape(self, s):
        return _charref.sub(lambda x: chr(int(x.group(1), 16)), s)

    def _redirect_response(self):
        headers = (
            b"HTTP/1.1 307 Temporary Redirect\r\n"
            b"Location: http://{:s}\r\n".format(self.local_ip)
        )

        return b"", headers

    def get_info(self, params):
        headers = (
            b"HTTP/1.1 200 OK\r\n"
        )
        info = common.get_config()
        info["act_pressure"] = 12345
        info["mac_address"] = self.mac_address
        return ujson.dumps(info), headers

    def login(self, params):
        ssid = params.get(b"ssid", None)
        password = params.get(b"password", None)

        # Write out credentials
        Creds(ssid=ssid, password=password).write()

        return self._redirect_response()

    def settings(self, params):
        lat = params.get(b"lat", None)
        lon = params.get(b"lon", None)
        foreindex = params.get(b"foreindex", None)
        ap_id = params.get(b"ap_id", None)
        min_level = params.get(b"min_level", None)
        min_lum = params.get(b"min_lum", None)
        max_level = params.get(b"max_level", None)
        max_lum = params.get(b"max_lum", None)
        p00_00 = params.get(b"p00_00", None)
        p00_01 = params.get(b"p00_01", None)
        p00_02 = params.get(b"p00_02", None)
        p00_03 = params.get(b"p00_03", None)
        p00_04 = params.get(b"p00_04", None)
        p00_05 = params.get(b"p00_05", None)
        p00_06 = params.get(b"p00_06", None)
        p00_07 = params.get(b"p00_07", None)
        p00_08 = params.get(b"p00_08", None)
        p00_09 = params.get(b"p00_09", None)
        p00_10 = params.get(b"p00_10", None)
        p00_11 = params.get(b"p00_11", None)
        p00_12 = params.get(b"p00_12", None)
        p00_13 = params.get(b"p00_13", None)
        p01_00 = params.get(b"p01_00", None)
        p01_01 = params.get(b"p01_01", None)
        p01_02 = params.get(b"p01_02", None)
        p01_03 = params.get(b"p01_03", None)
        p01_04 = params.get(b"p01_04", None)
        p01_05 = params.get(b"p01_05", None)
        p01_06 = params.get(b"p01_06", None)
        p01_07 = params.get(b"p01_07", None)
        p01_08 = params.get(b"p01_08", None)
        p01_09 = params.get(b"p01_09", None)
        p01_10 = params.get(b"p01_10", None)
        p01_11 = params.get(b"p01_11", None)
        p01_12 = params.get(b"p01_12", None)
        p01_13 = params.get(b"p01_13", None)
        p02_00 = params.get(b"p02_00", None)
        p02_01 = params.get(b"p02_01", None)
        p02_02 = params.get(b"p02_02", None)
        p02_03 = params.get(b"p02_03", None)
        p02_04 = params.get(b"p02_04", None)
        p02_05 = params.get(b"p02_05", None)
        p02_06 = params.get(b"p02_06", None)
        p02_07 = params.get(b"p02_07", None)
        p02_08 = params.get(b"p02_08", None)
        p02_09 = params.get(b"p02_09", None)
        p02_10 = params.get(b"p02_10", None)
        p02_11 = params.get(b"p02_11", None)
        p02_12 = params.get(b"p02_12", None)
        p02_13 = params.get(b"p02_13", None)
        p03_00 = params.get(b"p03_00", None)
        p03_01 = params.get(b"p03_01", None)
        p03_02 = params.get(b"p03_02", None)
        p03_03 = params.get(b"p03_03", None)
        p03_04 = params.get(b"p03_04", None)
        p03_05 = params.get(b"p03_05", None)
        p03_06 = params.get(b"p03_06", None)
        p03_07 = params.get(b"p03_07", None)
        p03_08 = params.get(b"p03_08", None)
        p03_09 = params.get(b"p03_09", None)
        p03_10 = params.get(b"p03_10", None)
        p03_11 = params.get(b"p03_11", None)
        p03_12 = params.get(b"p03_12", None)
        p03_13 = params.get(b"p03_13", None)
        p04_00 = params.get(b"p04_00", None)
        p04_01 = params.get(b"p04_01", None)
        p04_02 = params.get(b"p04_02", None)
        p04_03 = params.get(b"p04_03", None)
        p04_04 = params.get(b"p04_04", None)
        p04_05 = params.get(b"p04_05", None)
        p04_06 = params.get(b"p04_06", None)
        p04_07 = params.get(b"p04_07", None)
        p04_08 = params.get(b"p04_08", None)
        p04_09 = params.get(b"p04_09", None)
        p04_10 = params.get(b"p04_10", None)
        p04_11 = params.get(b"p04_11", None)
        p04_12 = params.get(b"p04_12", None)
        p04_13 = params.get(b"p04_13", None)
        p05_00 = params.get(b"p05_00", None)
        p05_01 = params.get(b"p05_01", None)
        p05_02 = params.get(b"p05_02", None)
        p05_03 = params.get(b"p05_03", None)
        p05_04 = params.get(b"p05_04", None)
        p05_05 = params.get(b"p05_05", None)
        p05_06 = params.get(b"p05_06", None)
        p05_07 = params.get(b"p05_07", None)
        p05_08 = params.get(b"p05_08", None)
        p05_09 = params.get(b"p05_09", None)
        p05_10 = params.get(b"p05_10", None)
        p05_11 = params.get(b"p05_11", None)
        p05_12 = params.get(b"p05_12", None)
        p05_13 = params.get(b"p05_13", None)
        p06_00 = params.get(b"p06_00", None)
        p06_01 = params.get(b"p06_01", None)
        p06_02 = params.get(b"p06_02", None)
        p06_03 = params.get(b"p06_03", None)
        p06_04 = params.get(b"p06_04", None)
        p06_05 = params.get(b"p06_05", None)
        p06_06 = params.get(b"p06_06", None)
        p06_07 = params.get(b"p06_07", None)
        p06_08 = params.get(b"p06_08", None)
        p06_09 = params.get(b"p06_09", None)
        p06_10 = params.get(b"p06_10", None)
        p06_11 = params.get(b"p06_11", None)
        p06_12 = params.get(b"p06_12", None)
        p06_13 = params.get(b"p06_13", None)
        p07_00 = params.get(b"p07_00", None)
        p07_01 = params.get(b"p07_01", None)
        p07_02 = params.get(b"p07_02", None)
        p07_03 = params.get(b"p07_03", None)
        p07_04 = params.get(b"p07_04", None)
        p07_05 = params.get(b"p07_05", None)
        p07_06 = params.get(b"p07_06", None)
        p07_07 = params.get(b"p07_07", None)
        p07_08 = params.get(b"p07_08", None)
        p07_09 = params.get(b"p07_09", None)
        p07_10 = params.get(b"p07_10", None)
        p07_11 = params.get(b"p07_11", None)
        p07_12 = params.get(b"p07_12", None)
        p07_13 = params.get(b"p07_13", None)
        p08_00 = params.get(b"p08_00", None)
        p08_01 = params.get(b"p08_01", None)
        p08_02 = params.get(b"p08_02", None)
        p08_03 = params.get(b"p08_03", None)
        p08_04 = params.get(b"p08_04", None)
        p08_05 = params.get(b"p08_05", None)
        p08_06 = params.get(b"p08_06", None)
        p08_07 = params.get(b"p08_07", None)
        p08_08 = params.get(b"p08_08", None)
        p08_09 = params.get(b"p08_09", None)
        p08_10 = params.get(b"p08_10", None)
        p08_11 = params.get(b"p08_11", None)
        p08_12 = params.get(b"p08_12", None)
        p08_13 = params.get(b"p08_13", None)
        p09_00 = params.get(b"p09_00", None)
        p09_01 = params.get(b"p09_01", None)
        p09_02 = params.get(b"p09_02", None)
        p09_03 = params.get(b"p09_03", None)
        p09_04 = params.get(b"p09_04", None)
        p09_05 = params.get(b"p09_05", None)
        p09_06 = params.get(b"p09_06", None)
        p09_07 = params.get(b"p09_07", None)
        p09_08 = params.get(b"p09_08", None)
        p09_09 = params.get(b"p09_09", None)
        p09_10 = params.get(b"p09_10", None)
        p09_11 = params.get(b"p09_11", None)
        p09_12 = params.get(b"p09_12", None)
        p09_13 = params.get(b"p09_13", None)
        p10_00 = params.get(b"p10_00", None)
        p10_01 = params.get(b"p10_01", None)
        p10_02 = params.get(b"p10_02", None)
        p10_03 = params.get(b"p10_03", None)
        p10_04 = params.get(b"p10_04", None)
        p10_05 = params.get(b"p10_05", None)
        p10_06 = params.get(b"p10_06", None)
        p10_07 = params.get(b"p10_07", None)
        p10_08 = params.get(b"p10_08", None)
        p10_09 = params.get(b"p10_09", None)
        p10_10 = params.get(b"p10_10", None)
        p10_11 = params.get(b"p10_11", None)
        p10_12 = params.get(b"p10_12", None)
        p10_13 = params.get(b"p10_13", None)
        p11_00 = params.get(b"p11_00", None)
        p11_01 = params.get(b"p11_01", None)
        p11_02 = params.get(b"p11_02", None)
        p11_03 = params.get(b"p11_03", None)
        p11_04 = params.get(b"p11_04", None)
        p11_05 = params.get(b"p11_05", None)
        p11_06 = params.get(b"p11_06", None)
        p11_07 = params.get(b"p11_07", None)
        p11_08 = params.get(b"p11_08", None)
        p11_09 = params.get(b"p11_09", None)
        p11_10 = params.get(b"p11_10", None)
        p11_11 = params.get(b"p11_11", None)
        p11_12 = params.get(b"p11_12", None)
        p11_13 = params.get(b"p11_13", None)
        timeout = params.get(b"timeout", None)
        debug = params.get(b"debug", None)

        common.store_config(lat, lon, foreindex, ap_id,
                            min_level, min_lum, max_level, max_lum,
                            p11_13, 
                            timeout, debug)

        return self._redirect_response()


    def connected(self, params):
        headers = b"HTTP/1.1 200 OK\r\n"
        body = open("./connected.html", "rb").read() % (self.ssid, self.local_ip)
        return body, headers

    def get_response(self, req):
        """generate a response body and headers, given a route"""

        headers = b"HTTP/1.1 200 OK\r\n"
        route = self.routes.get(req.path, None)

        if type(route) is bytes:
            # expect a filename, so return contents of file
            return open(route, "rb"), headers

        if callable(route):
            # call a function, which may or may not return a response
            response = route(req.params)
            body = response[0] or b""
            headers = response[1] or headers
            return uio.BytesIO(body), headers

        headers = b"HTTP/1.1 404 Not Found\r\n"
        return uio.BytesIO(b""), headers

    def is_valid_req(self, req):
        if req.host != self.local_ip:
            # force a redirect to the MCU's IP address
            return False
        # redirect if we don't have a route for the requested path
        return req.path in self.routes

    def read(self, s):
        """read in client request from socket"""

        data = s.read()
        if not data:
            # no data in the TCP stream, so close the socket
            self.close(s)
            return

        # add new data to the full request
        sid = id(s)
        self.request[sid] = self.request.get(sid, b"") + data

        # check if additional data expected
        if data[-4:] != b"\r\n\r\n":
            # HTTP request is not finished if no blank line at the end
            # wait for next read event on this socket instead
            return

        # get the completed request
        req = self.parse_request(self.request.pop(sid))

        if not self.is_valid_req(req):
            headers = (
                b"HTTP/1.1 307 Temporary Redirect\r\n"
                b"Location: http://{:s}/\r\n".format(self.local_ip)
            )
            body = uio.BytesIO(b"")
            self.prepare_write(s, body, headers)
            return

        # by this point, we know the request has the correct
        # host and a valid route
        body, headers = self.get_response(req)
        self.prepare_write(s, body, headers)

    def prepare_write(self, s, body, headers):
        # add newline to headers to signify transition to body
        headers += "\r\n"
        # TCP/IP MSS is 536 bytes, so create buffer of this size and
        # initially populate with header data
        buff = bytearray(headers + "\x00" * (536 - len(headers)))
        # use memoryview to read directly into the buffer without copying
        buffmv = memoryview(buff)
        # start reading body data into the memoryview starting after
        # the headers, and writing at most the remaining space of the buffer
        # return the number of bytes written into the memoryview from the body
        bw = body.readinto(buffmv[len(headers) :], 536 - len(headers))
        # save place for next write event
        c = WriteConn(body, buff, buffmv, [0, len(headers) + bw])
        self.conns[id(s)] = c
        # let the poller know we want to know when it's OK to write
        self.poller.modify(s, select.POLLOUT)

    def write_to(self, sock):
        """write the next message to an open socket"""

        # get the data that needs to be written to this socket
        c = self.conns[id(sock)]
        if c:
            # write next 536 bytes (max) into the socket
            bytes_written = sock.write(c.buffmv[c.write_range[0] : c.write_range[1]])
            if not bytes_written or c.write_range[1] < 536:
                # either we wrote no bytes, or we wrote < TCP MSS of bytes
                # so we're done with this connection
                self.close(sock)
            else:
                # more to write, so read the next portion of the data into
                # the memoryview for the next send event
                self.buff_advance(c, bytes_written)

    def buff_advance(self, c, bytes_written):
        """advance the writer buffer for this connection to next outgoing bytes"""

        if bytes_written == c.write_range[1] - c.write_range[0]:
            # wrote all the bytes we had buffered into the memoryview
            # set next write start on the memoryview to the beginning
            c.write_range[0] = 0
            # set next write end on the memoryview to length of bytes
            # read in from remainder of the body, up to TCP MSS
            c.write_range[1] = c.body.readinto(c.buff, 536)
        else:
            # didn't read in all the bytes that were in the memoryview
            # so just set next write start to where we ended the write
            c.write_range[0] += bytes_written

    def close(self, s):
        """close the socket, unregister from poller, and delete connection"""

        s.close()
        self.poller.unregister(s)
        sid = id(s)
        if sid in self.request:
            del self.request[sid]
        if sid in self.conns:
            del self.conns[sid]
        gc.collect()
