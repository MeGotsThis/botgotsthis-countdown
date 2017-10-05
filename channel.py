import asyncio
from datetime import timedelta

from bot import data  # noqa: F401
from lib.data import ChatCommandArgs
from lib.helper.chat import feature, permission_feature


@feature('countdown')
@permission_feature(('broadcaster', None), ('moderator', 'modcountdown'))
async def commandCountdown(args: ChatCommandArgs) -> bool:
    """
    !countdown 1
    """

    if 'countdownTask' in args.chat.sessionData:
        return True

    delay: timedelta
    if 'countdown-' in args.message.command:
        try:
            delay = timedelta(
                seconds=float(args.message.command.split('countdown-')[1]))
        except (ValueError, IndexError):
            delay = timedelta()
    else:
        delay = timedelta()

    duration: timedelta
    try:
        duration = timedelta(seconds=float(args.message[1]))
    except (ValueError, IndexError):
        duration = timedelta(seconds=10)

    if not args.permissions.twitchAdmin:
        delay = min(delay, timedelta(seconds=60))
        duration = min(duration, timedelta(seconds=300))

    if not args.permissions.broadcaster:
        delay = min(delay, timedelta(seconds=30))
        duration = min(duration, timedelta(seconds=30))

    if not duration:
        return True

    coro = countdown_task(chat=args.chat, delay=delay, duration=duration)
    args.chat.sessionData['countdownTask'] = coro
    asyncio.ensure_future(coro)

    return True


async def countdown_task(
        chat: 'data.Channel',
        delay: timedelta,
        duration: timedelta) -> None:
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    asyncio.sleep(delay.total_seconds())
    lapse: int = int(round(duration.total_seconds()))
    start: float = loop.time()
    d: int
    for d in range(lapse, 0, -1):
        chat.send(str(d))
        await asyncio.sleep(start + 1 - loop.time())
        start += 1
    chat.send('Go!')
    del chat.sessionData['countdownTask']
