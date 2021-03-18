def run_coroutine(corofn, *args):
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        coro = corofn(*args)
        asyncio.set_event_loop(loop)
        ret = loop.run_until_complete(coro)
        return ret
    finally:
        loop.close()
        
def limit_futures(futures, limit):
    from itertools import islice
    import time
    import asyncio
    futures_sl = [
        c for c in islice(futures, 0, limit)
    ]
    print(len(futures_sl))
    async def first_to_finish(futures):
        while True:
            await asyncio.sleep(0)
            for f in futures_sl:
                if f.done():
                    futures_sl.remove(f)
                    try:
                        newf = next(futures)
                        futures_sl.append(newf)
                    except StopIteration as e:
                        pass
                    return f.result()
    while len(futures_sl) > 0:
        yield first_to_finish(futures)