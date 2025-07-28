import logging
import logging.config
from hydrogram import Client, __version__, idle
from hydrogram.raw.all import layer
from database.users_chats_db import db
from info import API_ID, API_HASH, BOT_TOKEN, AUTH_CHANNEL
from utils import temp
from typing import Union, Optional, AsyncGenerator
from hydrogram import types
import asyncio
import sys

logging.basicConfig(
    level=logging.INFO,  # Now INFO logs will show everywhere
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logging.getLogger('hydrogram').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Install uvloop only on Unix systems (not Windows)
if sys.platform != 'win32':
    try:
        import uvloop
        uvloop.install()
        logger.info("uvloop installed for better performance")
    except ImportError:
        logger.info("uvloop not available, using default asyncio event loop")

# Try to import tgcrypto for better performance (optional)
try:
    import tgcrypto
    logger.info("tgcrypto loaded for faster encryption")
except ImportError:
    logger.info("tgcrypto not available - bot will work without it (slower encryption)")

class Bot(Client):
    def __init__(self):
        super().__init__(
            name='bot',
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins={"root": "plugins"},
            sleep_threshold=10,
            workers=200
        )

    async def start(self):
        await super().start()
        stg = await db.get_sttg()
        
        # Use test channels instead of database stored channels
        from info import AUTH_CHANNEL, CHANNELS
        from language_config import COMMON_CHANNEL
        temp.AUTH_CHANNEL = [AUTH_CHANNEL] if AUTH_CHANNEL else []
        temp.CHANNELS = CHANNELS
        temp.COMMON_CHANNEL = COMMON_CHANNEL
        logger.info(f"Using auth channel: {temp.AUTH_CHANNEL}")
        logger.info(f"Using common channel: {COMMON_CHANNEL}")
        logger.info(f"Using movie channels: {len(CHANNELS)} channels")
        
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        logger.info(f"bot started - @{me.username}")

    async def stop(self):
        await super().stop()
        logger.info("Bot stopped. Bye.")
    
    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Iterate through a chat sequentially.
        This convenience method does the same as repeatedly calling :meth:`~pyrogram.Client.get_messages` in a loop, thus saving
        you from the hassle of setting up boilerplate code. It is useful for getting the whole chat messages with a
        single call.
        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).
                
            limit (``int``):
                Identifier of the last message to be returned.
                
            offset (``int``, *optional*):
                Identifier of the first message to be returned.
                Defaults to 0.
        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.
        Example:
            .. code-block:: python
                for message in app.iter_messages("pyrogram", 1, 15000):
                    print(message.text)
        """
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1


async def main():
    """Main function to run the bot with proper signal handling"""
    import signal
    import os
    
    app = Bot()
    
    # Handle shutdown signals
    def signal_handler(signum, frame):
        logger.info(f"Stop signal received ({signal.Signals(signum).name}). Exiting...")
        asyncio.create_task(app.stop())
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await app.start()
        logger.info("Bot is running... Press Ctrl+C to stop.")
        await idle()  # Keep the bot running
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Stopping...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
