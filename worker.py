import os
import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']


redis_url = os.environ.get("REDIS_URL")
#redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.Redis.from_url(redis_url)

if __name__ == '__main__':
    print('worker.py invoked from here')
    with Connection(conn):
        print('****_____________worker activated on this connection __________****')
        worker = Worker(map(Queue, listen))
        worker.work()
