import asyncio
import logging
import os
import sys

# Ensure the project root is always on the path,
# so local packages (db, handlers, keyboards, states) are found
# regardless of where Python is invoked from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from supabase import create_async_client, AsyncClient

from db import queries
from handlers import auth, common, teacher, student

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

# Validate critical environment variables
if not all([BOT_TOKEN, SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWT_SECRET]):
    missing = []
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not SUPABASE_URL:
        missing.append("NEXT_PUBLIC_SUPABASE_URL")
    if not SUPABASE_ANON_KEY:
        missing.append("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY")
    if not SUPABASE_SERVICE_ROLE_KEY:
        missing.append("SUPABASE_SERVICE_ROLE_KEY")
    if not SUPABASE_JWT_SECRET:
        missing.append("SUPABASE_JWT_SECRET")
    raise ValueError(f"❌ Missing critical environment variables: {', '.join(missing)}")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Register routers (order matters — common first for /start, /cancel)
dp.include_router(common.router)
dp.include_router(auth.router)
dp.include_router(teacher.router)
dp.include_router(student.router)


async def init_supabase() -> AsyncClient:
    """Initialize Supabase admin client with JWT support for RLS."""
    # Admin client uses SERVICE_ROLE_KEY to bypass RLS
    admin_client = await create_async_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    # Initialize queries with JWT secret for RLS enforcement
    queries.init(admin_client, SUPABASE_JWT_SECRET, SUPABASE_URL)
    
    logger.info("✅ Supabase initialized with JWT/RLS support")
    return admin_client


async def main() -> None:
    await init_supabase()

    logger.info("Bot starting…")
    me = await bot.get_me()
    logger.info(f"Bot online: @{me.username} ({me.full_name})")

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())