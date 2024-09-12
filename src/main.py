import discord
import pytz
from datetime import datetime
from discord.ext import commands
from config import BOT_TOKEN


bot = commands.Bot(command_prefix="m!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def test_timezone_embed(ctx):
    embed = discord.Embed(
        title="Test",
        description="This is a test",
    )
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)


@bot.command()
async def get_top_chatters(
    ctx: commands.Context,
    channels_param: str,
    after: int = None,
    before: int = None,
    limit: int = 3,
):
    if not before or not after:
        await ctx.send("Please specify before and after times")
        return

    await ctx.send("Starting fetch... this will take some time")

    messages = {}  # user: count

    channels = []
    for channel_id in channels_param.split(" "):
        channel = await bot.fetch_channel(int(channel_id))
        if channel:
            channels.append(channel)
        else:
            await ctx.send(f"Channel with id {channel_id} not found")
            return

    for channel in channels:
        try:
            if not isinstance(channel, discord.TextChannel):
                continue

            async for msg in channel.history(
                limit=1_000_000,
                before=datetime.fromtimestamp(before),
                after=datetime.fromtimestamp(after),
            ):
                if not msg.author.bot:
                    messages[msg.author] = messages.get(msg.author, 0) + 1
        except discord.errors.Forbidden:
            pass

    sorted_messages = sorted(messages.items(), key=lambda x: x[1], reverse=True)

    embed = discord.Embed(
        title="Top Chatters",
        description=f"Top {limit} chatters in the channels {', '.join([channel.mention for channel in channels])}",
    )
    embed.color = discord.Color.blurple()
    for i, (user, count) in enumerate(sorted_messages[:limit]):
        embed.add_field(
            name=f"Place #{i+1}",
            value=f"{user.mention}: {count} messages",
            inline=False,
        )

    total_count = 0
    for _, count in sorted_messages[:limit]:
        total_count += count
    embed.set_footer(
        text=f"A total of {total_count} messages sent by {limit} users across {len(channels)} channels"
    )

    await ctx.reply(embed=embed)


bot.run(BOT_TOKEN)
