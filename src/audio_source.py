import asyncio
import logging

import discord
import youtube_dl

import utils


_log = logging.getLogger(__name__)
_log.addHandler(utils.HANDLER)
_log.setLevel(logging.ERROR)

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ""


class YTDLSource(discord.PCMVolumeTransformer):
    """FFMPEG audio source extracted via the YTDL lib."""

    ytdl_format_options = {
        "format": "bestaudio/best",
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
        "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
    }

    ffmpeg_options = {
        "options": "-vn",
    }

    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        """Return an FFMPEG audio source from the YouTube url."""
        loop = loop or asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(
                executor=None,
                func=lambda: cls.ytdl.extract_info(url, download=not stream),
            )
        except Exception as e:
            _log.error("URL extraction failed: '%s'", e.args[0])
            return None  # Catch any download/stream error.

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else cls.ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **cls.ffmpeg_options), data=data)
