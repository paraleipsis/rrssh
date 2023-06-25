# REST Reverse SSH
A framework for creating asynchronous REST API services based on a reverse SSH tunnel that allows:
- create both REST-like web applications and HTTP-like clients;
- transmit data via a reverse SSH tunnel, where the connection itself initiates the server in the form of a web application REST API (as an SSH client), and the HTTP client listens and accepts new connections (as an SSH server);
- implement a request-response mechanism in the form of JSON objects based on a TCP socket similar to the HTTP protocol;
- support for HTTP verbs for forming requests: GET, POST, PATCH, DELETE and STREAM;
- create a persistent connection in the form of a TCP session;
- create asynchronous client and server.

## Usage

Creating a reverse server with endpoints:

```python
import asyncio
from typing import Mapping

from rrssh.server.server import ReverseSSHServer

rssh_server = ReverseSSHServer(
    remote_host='localhost',
    remote_port=8022,
    server_host_keys='id_rsa_path',
    authorized_client_keys='authorized_keys_path',
)


async def home():
    response = {
        'home': 'router'
    }

    return response


def service_data(data):
    print(data)
    return 'OK'


async def create(data: Mapping):
    status = service_data(data=data)

    response = {
        'status': status
    }

    return response


async def stream():
    for i in range(10):
        await asyncio.sleep(1)
        yield i


rssh_server.path(request_type='GET', resource='/home', callback=home)
rssh_server.path(request_type='POST', resource='/create', callback=create)
rssh_server.path(request_type='STREAM', resource='/stream', callback=stream)


async def main():
    await rssh_server.start()

asyncio.run(main())
```

Creating a reverse client with endpoints:

```python
from client.client import ReverseSSHClient
from client.session import ReverseSSHClientSession
from pubsub.subscriber import Subscriber
from pubsub.pubsub import pb

rssh_client = ReverseSSHClient(
    local_host='localhost',
    local_port=8022,
    client_keys='id_rsa_path',
    known_hosts=None
)

rssh_client.run_rssh_forever()

# get UUID of new connection
sub = Subscriber(channel='connections', pubsub=pb)
host_ssh_data = await sub.get()

session = host_ssh_data['session']


async def get_example(session: ReverseSSHClientSession):
    some_params = {
        'key': 'value'
    }

    request = await session.get(
        router='/home',
        params=some_params,
    )

    return request


async def stream_example(session: ReverseSSHClientSession):
    async for msg in session.stream(
            router='/stream',
    ):
        yield msg

```
