# nameko-design

![logo](./logo.png)

WIP: Generate [Nameko](https://www.nameko.io/) http files from design schema inspired by [goa](https://goa.design/)

## Dependencies

- Python3.6
- [Poetry](https://github.com/sdispater/poetry)

## Installation

```bash
cd nameko-design
poetry install
```

## Usage

```bash
cd nameko-design
poetry run python cli/main.py
```

## Design

This API design schema

```python
with Service('http_service'):
    Title('This is a http service')

    with Method('liveness'):
        Description('liveness probe')
        Result(str)
        HTTP(GET, '/liveness')

    with Method('readiness'):
        Description('readiness probe')
        Result(str)
        HTTP(GET, '/readiness')
```

will generate the below nameko file

```python
from nameko.web.handlers import http


class HttpService:
    name = 'http service'

    @http('GET', '/liveness')
    def liveness(self, request) -> str:
        pass

    @http('GET', '/readiness')
    def readiness(self, request) -> str:
        pass
```

## TODO

- [ ] Configure http url and port
- [ ] Add URL parameter and type
- [ ] Add payload (name, type, description, position etc)
- [ ] Add validation
- [ ] Add gRPC server
- [ ] Generate proto files
- [ ] Generate swagger json

What I want:

```python
with Service('http_service'):
    Title('This is a http service')

    with Method('liveness'):
        Description('liveness probe')
        Result(str)
        HTTP(GET, '/liveness')
        GRPC() # Not yet imnplemented

    with Method('add'):
        Description('a + b')
        with Payload(): # Not yet implemented
            Field(1, "a", int, "left operand")
            Field(2, "b", int, "right operand")
            Required("a", "b")
        Result(Int)
        HTTP(GET, '/add/{a}/{b}') # Not yet implemented
        GRPC() # Not yet imnplemented
```
