import discord
import requests
from bs4 import BeautifulSoup
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
VINTED_URL = "https://www.vinted.com/catalog?order=newest_first&time=1740164528"

intents = discord.Intents.default()
intents.message_content = True  # Needed for message commands
client = discord.Client(intents=intents)

last_posted = None

async def fetch_latest_item():
    """Fetches the latest item from Vinted"""
    try:
        response = requests.get(VINTED_URL)
        soup = BeautifulSoup(response.text, "html.parser")

        item = soup.find("div", class_="feed-grid__item")  # Adjust selector if needed
        if item:
            link = item.find("a")["href"]
            title = item.find("h2").text.strip()
            price = item.find("span", class_="price").text.strip()
            return title, price, f"https://www.vinted.com{link}"
        return None
    except Exception as e:
        return f"Error: {str(e)}"

async def check_vinted():
    """Automatically checks for new listings"""
    global last_posted
    await client.wait_until_ready()
    channel = client.get_channel(1342574387492294708)  # Replace with your channel ID

    while not client.is_closed():
        latest_item = await fetch_latest_item()
        if latest_item and isinstance(latest_item, tuple):
            title, price, link = latest_item
            if link != last_posted:
                last_posted = link
                await channel.send(f"**{title}**\n💰 {price}\n🔗 {link}")
        elif isinstance(latest_item, str):  # If an error occurred
            await channel.send(f"⚠️ Error fetching data: {latest_item}")

        await asyncio.sleep(60)  # Check every 60 seconds

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    client.loop.create_task(check_vinted())

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == "!latest":
        latest_item = await fetch_latest_item()
        if latest_item and isinstance(latest_item, tuple):
            title, price, link = latest_item
            await message.channel.send(f"**{title}**\n💰 {price}\n🔗 {link}")
        else:
            await message.channel.send(f"⚠️ Failed to fetch latest item: {latest_item}")

client.run(TOKEN)
