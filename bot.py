import discord
import requests
from bs4 import BeautifulSoup
import os
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

TOKEN = os.getenv("DISCORD_TOKEN")
VINTED_URL = "https://www.vinted.com/catalog?order=newest_first"

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent for commands
client = discord.Client(intents=intents)

last_posted = None

def fetch_latest_item():
    """Fetches the latest item from Vinted using requests, then Selenium if needed"""
    try:
        response = requests.get(VINTED_URL, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        item = soup.find("div", class_="feed-grid__item")  

        if item:
            link = item.find("a")["href"]
            title = item.find("h2").text.strip()
            price = item.find("span", class_="price").text.strip()
            return title, price, f"https://www.vinted.com{link}"

        print("Requests method failed, trying Selenium...")

    except Exception as e:
        print(f"Requests scraping failed: {e}")

    # Fallback to Selenium
    try:
        options = Options()
        options.add_argument("--headless")  
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        driver.get(VINTED_URL)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        item = soup.find("div", class_="feed-grid__item")  
        if item:
            link = item.find("a")["href"]
            title = item.find("h2").text.strip()
            price = item.find("span", class_="price").text.strip()
            return title, price, f"https://www.vinted.com{link}"

    except Exception as e:
        return f"Error fetching data: {e}"

    return "No items found"

async def check_vinted():
    """Automatically checks for new listings"""
    global last_posted
    await client.wait_until_ready()
    channel = client.get_channel(1342574387492294708)  # Replace with your channel ID

    while not client.is_closed():
        latest_item = fetch_latest_item()
        if latest_item and isinstance(latest_item, tuple):
            title, price, link = latest_item
            if link != last_posted:
                last_posted = link
                await channel.send(f"**{title}**\n💰 {price}\n🔗 {link}")
        elif isinstance(latest_item, str):  
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
        latest_item = fetch_latest_item()
        if latest_item and isinstance(latest_item, tuple):
            title, price, link = latest_item
            await message.channel.send(f"**{title}**\n💰 {price}\n🔗 {link}")
        else:
            await message.channel.send(f"⚠️ Failed to fetch latest item: {latest_item}")

client.run(TOKEN)
