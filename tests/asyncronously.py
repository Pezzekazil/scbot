import math
import asyncio


async def primes(up_to_number):
    for i in range(1, up_to_number + 1 ):
        for j in range(2, i):
            if i % j == 0:
                break
        else:
            yield i

async def main():
    a = el.create_task(primes(100))
    b = el.create_task(primes(1000))
    c = el.create_task(primes(10))
    await asyncio.wait([a,b,c])
    return a,b,c

if __name__ == "__main__":
    el = asyncio.get_event_loop()
    try:
        a,b,c = el.run_until_complete(main())
    finally:
        el.close()
    print([i.result() for i in [a,b,c]])
