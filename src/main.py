"""Contains the entry point script to initialise the different components of the service and
start the asyncio event loop. Handles environment variables and cli args."""

import argparse
import asyncio
import logging
import os
import sys

import discord
import dotenv

import api
import utils
from bot import AudioClient

_log = logging.getLogger(__name__)
_log.addHandler(utils.HANDLER)
_log.setLevel(logging.INFO)


def run(token: str, port: int):
    """|Blocking| Starts the AudioClient Bot and its AudioService API."""
    discord.utils.setup_logging(
        handler=utils.HANDLER,
        formatter=utils.FORMATTER,
        level=logging.WARNING,
        root=False,
    )

    intents = discord.Intents.default()
    intents.message_content = True
    client = AudioClient(intents=intents)
    client_api = api.AudioServiceAPI(client, "__name__")

    async def runner():
        """|coro| Logs the Bot into Discord then starts coroutine services."""

        try:
            await client.login(token)
        except discord.LoginFailure:
            _log.fatal("Failed to login. Is your token valid?")
            return
        except discord.HTTPException as e:
            _log.fatal("Failed while making a login request to Discord.", e.args[0])
            return

        await asyncio.gather(
            client.connect(reconnect=True),
            client_api.start("0.0.0.0", port),
        )

    asyncio.run(runner())


if __name__ == "__main__":
    default_api_port = 5050

    dotenv.load_dotenv()
    bot_token = os.environ.get("DISCORD_BOT_TOKEN", None)
    api_port = os.environ.get("API_PORT", default_api_port)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--TOKEN",
        help="Set the Bot TOKEN to use for connecting to Discord."
        + "\n\tWARNING: It is advisable to pass the token as an "
        + "environment variable in the `.env` file instead.",
    )
    parser.add_argument(
        "-a",
        "--API_PORT",
        type=int,
        help=f"Set the API PORT to host the API Handler on. Defaults to '{default_api_port}'",
    )
    args = parser.parse_args()

    if args.TOKEN:
        _log.warning(
            "Received Bot Token via CLI args. For safety, pass this as an environment"
            + " variable, or in the '.env' file instead."
        )
        bot_token = args.TOKEN
    if args.API_PORT:
        api_port = args.API_PORT

    if bot_token is None:
        _log.fatal("Required environment variable `DISCORD_BOT_TOKEN` is missing.")
        sys.exit(5)  # Auth Error.

    run(token=bot_token, port=api_port)
