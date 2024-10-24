import logging

from collections import namedtuple
from typing import Optional

import grpc

from .grpc_stubs import tunnel_iface_pb2 as stubs, tunnel_iface_pb2_grpc as grpc_stubs

log = logging.getLogger(__name__)
Tunnel = namedtuple("Tunnel", ["address", "url"])


class TunnelInterface:
    def __init__(self, tunnel_uri: str = "127.0.0.1:50056"):
        self.tunnel_uri = tunnel_uri

    def open_tunnel(
        self,
        address: str,
        protocol: str = "http",
        timeout: int = 15,
        username: str = None,
        password: str = None,
        domain: str = None,
    ) -> Optional[str]:
        """Open a tunnel with the given address and protocol.

        Returns the tunnel URL if opening the tunnel succeeded, None otherwise.
        """
        with grpc.insecure_channel(self.tunnel_uri) as channel:
            resp: stubs.OpenTunnelResponse = grpc_stubs.TunnelInterfaceStub(channel).OpenTunnel(stubs.OpenTunnelRequest(
                tunnel=stubs.TunnelRequest(
                    address=address,
                    protocol=protocol,
                    timeout=timeout,
                    username=username,
                    password=password,
                    domain=domain,
                )))

        if not resp or not resp.response_header.success or not resp.success:
            log.warning(f"Failed to open tunnel: {resp.response_header.message}")
            return

        return resp.success and resp.url

    def close_tunnel(self, address: str = None, url: str = None) -> bool:
        """Close tunnel by either address (ie. localhost:5000) or url (ie. https://random.ngrok.io)"""
        if not (address or url):
            raise ValueError("Address or URL required")

        with grpc.insecure_channel(self.tunnel_uri) as channel:
            resp: stubs.CloseTunnelResponse = grpc_stubs.TunnelInterfaceStub(channel).CloseTunnel(
                stubs.CloseTunnelRequest(address=address, url=url)
            )

        if not resp or not resp.response_header.success or not resp.success:
            log.warning(f"Failed to close tunnel: {resp.response_header.message}")
            return False

        return True

    def close_all_tunnels(self) -> bool:
        """Close all open tunnels. Returns True if this succeeded, False otherwise."""
        with grpc.insecure_channel(self.tunnel_uri) as channel:
            resp: stubs.CloseAllTunnelsResponse = grpc_stubs.TunnelInterfaceStub(channel).CloseAllTunnels(stubs.CloseTunnelRequest())

        if not resp or not resp.response_header.success or not resp.success:
            log.warning(f"Failed to close all tunnels: {resp.response_header.message}")
            return False

        return True

    def get_tunnel(self, address: str = None, url: str = None) -> Optional[Tunnel]:
        """Get tunnel by either address (ie. localhost:5000) or url (ie. https://random.ngrok.io)

        Returns a namedtuple with address and url attributes.
        """
        if not (address or url):
            raise ValueError("Address or URL required")

        with grpc.insecure_channel(self.tunnel_uri) as channel:
            resp: stubs.GetTunnelResponse = grpc_stubs.TunnelInterfaceStub(channel).GetTunnel(
                stubs.GetTunnelRequest(address=address, url=url)
            )

        if not resp or not resp.response_header.success:
            log.warning(f"Failed to get tunnel: {resp.response_header.message}")
            return None

        return Tunnel(resp.tunnel.address, resp.tunnel.url)

    def get_all_tunnels(self) -> Optional[list[Tunnel]]:
        """Get all open tunnels. Returns a list of Tunnels with address and url attributes."""
        with grpc.insecure_channel(self.tunnel_uri) as channel:
            resp: stubs.ListTunnelsResponse = grpc_stubs.TunnelInterfaceStub(channel).ListTunnels(stubs.ListTunnelsRequest())

        if not resp or not resp.response_header.success:
            log.warning(f"Failed to get all tunnels: {resp.response_header.message}")
            return None

        return [Tunnel(r.address, r.url) for r in resp.tunnels]


