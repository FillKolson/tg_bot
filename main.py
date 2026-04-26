import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from supabase import create_async_client, AsyncClient

# Load environment variables
load_dotenv()

# Bot and Supabase configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY")

# Logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

supabase: AsyncClient = None

# Initialize Supabase client
async def init_supabase():
    global supabase
    supabase = await create_async_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Supabase client initialized")

# Bot startup
async def main():
    await init_supabase()
    logger.info("Bot starting...")
    me = await bot.get_me()
    logger.info(f"Bot online: @{me.username} ({me.full_name})")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())