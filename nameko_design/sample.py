from . import *


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
