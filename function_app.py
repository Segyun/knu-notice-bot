import asyncio
import os
import azure.functions as func
import json
import logging
from azure_blob import AzureBlob
from knu_notice_bot import KNUNoticeBot

app = func.FunctionApp()


@app.schedule(
    schedule="0 0 0-15 * * *",
    arg_name="myTimer",
    run_on_startup=True,
    use_monitor=False,
)
def hourly_trigger(myTimer: func.TimerRequest) -> None:
    ACADEMY = "academy"
    AI = "ai"
    COMPUTER = "computer"
    NOTICE = "notice"
    SEMINAR = "seminar"
    SWEDU = "swedu"

    # Initialize azure blob storage
    azure_blob = AzureBlob(
        account_url="https://knunoticebot.blob.core.windows.net",
        container_name="knunoticebot",
    )

    # Get latest notice number from azure blob
    NOTICE_NUMBERS_JSON = "notice_numbers.json"
    notice_numbers_json = azure_blob.download_blob_to_str(NOTICE_NUMBERS_JSON)
    notice_numbers = json.loads(notice_numbers_json)

    # Get telegram bot token from file
    bot_token = ""
    bot_token_path = os.path.join(os.getcwd(), "bot_token.txt")
    with open(bot_token_path, "r") as bot_token_file:
        bot_token = bot_token_file.readline()

    # Get chat id from file
    chat_id = ""
    chat_id_path = os.path.join(os.getcwd(), "chat_id.txt")
    with open(chat_id_path, "r") as chat_id_file:
        chat_id = chat_id_file.readline()

    # Initialize KNUNoticeBot
    knunoticebot = KNUNoticeBot(bot_token=bot_token, chat_id=chat_id)

    # Send notice to telegram chat room
    async def send_all_notices() -> None:
        await knunoticebot.send_and_save_posts(ACADEMY, notice_numbers, azure_blob)
        await knunoticebot.send_and_save_posts(AI, notice_numbers, azure_blob)
        await knunoticebot.send_and_save_posts(COMPUTER, notice_numbers, azure_blob)
        await knunoticebot.send_and_save_posts(NOTICE, notice_numbers, azure_blob)
        await knunoticebot.send_and_save_posts(SEMINAR, notice_numbers, azure_blob)
        await knunoticebot.send_and_save_posts(SWEDU, notice_numbers, azure_blob)

    asyncio.run(send_all_notices())

    # Update latest notice number to azure blob
    notice_numbers_json = json.dumps(notice_numbers, indent=2)
    azure_blob.upload_blob(NOTICE_NUMBERS_JSON, notice_numbers_json)

    logging.info("Python timer trigger function executed.")
