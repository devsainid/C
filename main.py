
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
import requests

API_ID = 18388001
API_HASH = "d54b20d24aae786f0fadceac5a981506"
BOT_TOKEN = "7600489635:AAEXc3iBM7g_O_L6_yL3h5vNN4o_BSWsLDE"
OWNER_ID = 6559745280

app = Client("checkup_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.basicConfig(level=logging.INFO)

def ai_reply(text):
    url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
    headers = {"Authorization": "Bearer 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"}
    response = requests.post(url, headers=headers, json={"inputs": text})
    try:
        return response.json()[0]["generated_text"]
    except Exception as e:
        return "..."

@app.on_message(filters.group & ~filters.bot)
async def forward_to_owner(client, message: Message):
    try:
        fwd_msg = f"📨 Message from group: @{message.chat.username or message.chat.title}

{message.text}"
        await client.send_message(chat_id=OWNER_ID, text=fwd_msg)
    except Exception as e:
        print(e)

@app.on_message(filters.command(["ban", "kick", "mute", "unmute", "purge", "approve", "vc"]) & filters.user(OWNER_ID) & filters.group)
async def handle_commands(client, message: Message):
    try:
        if not message.reply_to_message:
            await message.reply("Reply to a user to perform this action.")
            return
        user_id = message.reply_to_message.from_user.id
        cmd = message.command[0]

        if cmd == "ban":
            await client.ban_chat_member(message.chat.id, user_id)
            await message.reply("User banned.")
        elif cmd == "kick":
            await client.kick_chat_member(message.chat.id, user_id)
            await message.reply("User kicked.")
        elif cmd == "mute":
            await client.restrict_chat_member(message.chat.id, user_id, permissions={})
            await message.reply("User muted.")
        elif cmd == "unmute":
            await client.restrict_chat_member(message.chat.id, user_id, permissions={"can_send_messages": True})
            await message.reply("User unmuted.")
        elif cmd == "approve":
            await client.approve_chat_join_request(message.chat.id, user_id)
            await message.reply("User approved.")
        elif cmd == "purge":
            async for msg in client.get_chat_history(message.chat.id, limit=100):
                await client.delete_messages(message.chat.id, msg.message_id)
            await message.reply("Chat purged.")
        elif cmd == "vc":
            await client.start_video_chat(message.chat.id)
            await message.reply("Voice chat started.")
    except Exception as e:
        await message.reply(f"Error: {e}")

@app.on_message(filters.text & filters.group & ~filters.bot)
async def chat_with_ai(client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user.is_self:
        reply = ai_reply(message.text)
        await message.reply(reply)

app.run()
