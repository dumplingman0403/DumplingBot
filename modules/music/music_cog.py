from ast import alias
import asyncio
import os
# Time tracking
import datetime
# Discord API
import discord
from discord.ext import commands 
# Download Youtude API 
import youtube_dl
from youtube_dl import YoutubeDL

from modules.help.help_command import HelpCommand
# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ffmpeg_support_formats = [".mp3", ".mp4", ".wma"]

class Music(commands.Cog):
    def __init__(self, bot):
        
        self.bot = bot

        # current playing
        self.current = None
        # format 2d array: [{'source': url, 'title': song's name, 'local': bool}]
        self.music_queue = []
        self.YTDL_OPTIONS = ytdl_format_options
        self.FFMPEG_OPTIONS = ffmpeg_options
        self.support = ffmpeg_support_formats
          

    def search_yt(self, item):
        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]   
            except Exception:
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title'], 'local': False}
    

    @commands.command(name="join", aliases=["j"], help="Joins a voice channel")
    async def join(self, ctx):
        """Joins a voice channel"""
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.reply("🚫 You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")

    @commands.command(help="Stops and disconnects the bot from voice")
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        self.music_queue = []
        self.current = None
        await ctx.voice_client.disconnect()
    
    @commands.command(help="Pause playing music", description="Pause playing music")
    async def pause(self, ctx):
        """Pause playing music"""
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.reply("⏸ Pause")
        
    @commands.command(help="Resume playing music")
    async def resume(self, ctx):
        """Resume playing music"""
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.reply("▶️ Play")
    
    @commands.command(help="Changes the player's volume")
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""
        if ctx.voice_client is None:
            return await ctx.reply("🚫 You are not connected to a voice channel.")
        
        ctx.voice_client.source.volume = volume / 100
        await ctx.reply(f"🔉 Changed volume to {volume}%")

    @commands.command(name="play_local", aliases=["pl"], help="Plays a file from the local filesystem")
    async def play_local(self, ctx, *, query):
        """Plays a file from the local filesystem"""
    
        if not os.path.isfile(query):
            return await ctx.reply("❌ Playing error: No such file or directory")
        
        file_name = os.path.basename(query)
        _, file_ext = os.path.splitext(file_name)
        
        if file_ext not in self.support:
            await ctx.reply("❌ Playing error: Player don't support this file format.")
            raise commands.CommandError(f'error file format {file_ext}')

        self.music_queue.append({'source': query, 'title': file_name, 'local': True})

        if ctx.voice_client.is_playing():
            await ctx.reply(f'➕ Add 🎵 {file_name} to queue')
        else:
            try:
                await self.play_music(ctx)
            except Exception as e:
                await ctx.reply(f'❌ Playing error: player not support file audio formats')
                raise commands.CommandError(e)
        
    @commands.command(name="play_url", aliases=["yt", "url"])
    async def play_yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)""" 

        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception as e:
                return await ctx.reply(f'❌ Playing error: {e}')

        self.music_queue.append({'source': info['formats'][0]['url'], 'title': info['title'], 'local': False})

        if ctx.voice_client.is_playing():
            await ctx.reply(f'➕ Add 🎵 {info["title"]} to queue')
        else:
            await self.play_music(ctx)
        

    @commands.command(name="play", aliases=["p"], help="Plays by searching keywords on Youtube")
    async def play(self, ctx, *, keywords):
        """Plays by searching keywords on Youtube"""
       
        song = self.search_yt(keywords)
        # check music download
        if type(song) == bool:
            await ctx.reply("❌ Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.")
        else:
            self.music_queue.append(song)

        if ctx.voice_client.is_playing():
            await ctx.reply(f'➕ Add 🎵 {song["title"]} to queue')
        else:
            await self.play_music(ctx)
    
    async def play_music(self, ctx, local=False):
        """Play music function"""
        self.current = self.music_queue[0]['title']
        source = self.music_queue[0]['source']
        local = self.music_queue[0]['local']
        self.music_queue.pop(0)
        if local:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source))
        else:
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source, **self.FFMPEG_OPTIONS))
        ctx.voice_client.play(source, after=lambda e: self.play_next(ctx, local))
        await ctx.reply(f'🎶 Now playing: {self.current}')
        
                
    def play_next(self, ctx, local=False):
        """Play next song"""
        if len(self.music_queue) > 0:
            source = self.music_queue[0]["source"]
            self.current = self.music_queue[0]["title"]
            local = self.music_queue[0]['local']
            self.music_queue.pop(0)
            if local:
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source))
            else:
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source, **self.FFMPEG_OPTIONS))
            ctx.voice_client.play(source, after=lambda e: self.play_next(ctx, local))
        

    @commands.command(name="playlist", aliases=["queue", "q", "Q"], help="Displays songs in queue")
    async def play_list(self, ctx):
        """Displays songs in queue"""
       
        if len(self.music_queue) > 0:
            # format playlist
            song_list = []
            for i, song in enumerate(self.music_queue):
                song_list.append(str(i + 1) + ". " + song["title"])
            song_list = "\n".join(song_list)

            embed = discord.Embed(
            title = "🎧 Playlist",
            colour = ctx.author.colour,
            Timestamp = datetime.datetime.utcnow()
            )
            embed.add_field(name="Next up", value=song_list)

           
        else:
            embed = discord.Embed(
            title = "🎧 Playlist",
            description = "😢 No music in queue.",
            colour = ctx.author.colour,
            Timestamp = datetime.datetime.utcnow()
            )   
        await ctx.reply(embed = embed)

        
    @commands.command(name="skip", aliases=["sk"], help="Skip current playing song to next one")
    async def skip(self, ctx):
        """Skip current playing song to next one"""
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await self.play_music(ctx)
        

    @commands.command(help="Clear songs in queue")
    async def clear(self, ctx):
        """Clear songs in queue"""
        self.music_queue = []
        # ctx.voice_client.stop()   # !!! undecided
        await ctx.reply("Queue is cleared. 🧹")
        
    @commands.command(name="now", help="Returns the song is currently playing")
    async def now_play(self, ctx):
        """Returns the song is currently playing"""
        if self.current:
            await ctx.reply(f'🎶 Now playing: {self.current}')
        else:
            await ctx.reply("No music is currently playing. 😪")

    @play_local.before_invoke
    @play.before_invoke
    @play_yt.before_invoke
    async def ensure_voice(self, ctx):

        # check if user in voice channel
        if not ctx.author.voice:
            await ctx.reply("🚫 You are not connected to a voice channel.")
            raise commands.CommandError("Author not connected to a voice channel.")

        # connect bot to voice channel
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
        # if player is paused, resume playing
        elif ctx.voice_client.is_paused():
            ctx.voice_client.resume()
    
    