import discord
import requests
from bs4 import BeautifulSoup
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
VINTED_URL = "https://www.vinted.com/vetements?order=newest_first"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_posted = None

async def check_vinted():
    global last_posted
    await client.wait_until_ready()
    channel = client.get_channel(YOUR_CHANNEL_ID)  # Replace with your channel ID

    while not client.is_closed():
        response = requests.get(VINTED_URL)
        soup = BeautifulSoup(response.text, "html.parser")
        
        item = soup.find("div", class_="feed-grid__item")  # Adjust this selector if needed
        if item:
            link = item.find("a")["href"]
            title = item.find("h2").text.strip()
            price = item.find("span", class_="price").text.strip()

            if link != last_posted:
                last_posted = link
                await channel.send(f"**{title}**\n💰 {price}\n🔗 https://www.vinted.com{link}")

        await asyncio.sleep(60)  # Check every 60 seconds

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    client.loop.create_task(check_vinted())

client.run(TOKEN)
