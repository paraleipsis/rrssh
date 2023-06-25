from typing import Optional, Dict
from uuid import UUID

import asyncssh

from pubsub.publisher import Publisher
from pubsub.pubsub import pb
from logger.logs import logger

_publisher: Optional[Publisher] = None
_connections_channel: Optional[str] = None


def init_publisher() -> None:
    global _publisher

    _publisher = Publisher(pubsub=pb)

    return None


def init_conn_channel(channel: str) -> None:
    global _connections_channel

    _connections_channel = channel

    return None


def get_publisher() -> Publisher:
    return _publisher


def get_channel() -> str:
    return _connections_channel


async def publish_host(
        host_uuid: UUID,
        host_connection: asyncssh.SSHClientConnection,
        host_channel: asyncssh.SSHTCPChannel,
        host_session: asyncssh.SSHTCPSession
) -> None:
    msg = {
        'uuid': host_uuid,
        'connection': host_connection,
        'channel': host_channel,
        'session': host_session
    }

    publisher = get_publisher()
    channel = get_channel()

    await publisher.publish(
        channel=channel,
        message=msg
    )

    logger['debug'].debug(
        f"Message published to the channel '{channel}': {msg}"
    )

    return None


async def new_node_conn_handler(
        identify_response: Dict,
        **kwargs
) -> UUID | None:
    node_uuid = UUID(identify_response['response']['node_id'])

    await publish_host(
        host_uuid=node_uuid,
        **kwargs
    )

    return node_uuid
