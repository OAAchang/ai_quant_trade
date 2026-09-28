"""Prove the default pytest configuration blocks network sockets."""

import socket

import pytest
from pytest_socket import SocketBlockedError


def test_network_socket_is_blocked_by_default() -> None:
    with pytest.raises(SocketBlockedError):
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)
