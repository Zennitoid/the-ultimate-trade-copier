from telethon import TelegramClient, events
import asyncio
import logging
import signal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_id = 21560448
api_hash = '61273fe48b512e5baf019fd5831b3c14'
stop_event = asyncio.Event()

def signal_handler(signum, frame):
    stop_event.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

async def resolve_channel(client, channel_id):
    try:
        # Ensure channel_id is an integer
        entity = await client.get_entity(int(channel_id))
        return entity
    except Exception as e:
        logger.error(f"Could not resolve channel ID {channel_id}: {e}")
        return None

async def monitor_channel(client, channel):
    @client.on(events.NewMessage(chats=channel))
    async def handler(event):
        new_message_text = event.message.message
        logger.info(f'New message received in: {channel.title}: {new_message_text}')
        with open('messageLog.txt', 'a') as f:
            f.write(new_message_text)
            f.write('\n')


async def main():
    client = TelegramClient('copier', api_id, api_hash)
    await client.start()
    logger.info('Connected to Telegram.')
    dialogs = await client.get_dialogs()
    channel_ids = ['1002174900355', '1001447871772']

    channels = []
    for channel_id in channel_ids:
        channel = await resolve_channel(client, channel_id)
        if channel:
            channels.append(channel)
        else:
            logger.error(f'Failed to resolve channel ID: {channel_id}')
    
    tasks = [monitor_channel(client, channel) for channel in channels]

    await asyncio.gather(*tasks)
    await stop_event.wait()

    await client.disconnect()
    logger.info('Client disconnected.')

async def run_indefinitely():
    while not stop_event.is_set():
        try:
            await main()
        except Exception as e:
            logger.error(f'An error occurred: {e}')
            logger.info('Reconnecting in 5 seconds...')
            await asyncio.sleep(5)


asyncio.run(run_indefinitely())
