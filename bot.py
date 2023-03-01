import telegram
import logging
import openai
import yaml
import random

# Load the API key from secrets.yaml
with open("secrets.yaml", "r") as f:
    secrets = yaml.safe_load(f)

openai.api_key = secrets["openai_api_key"]

# Load the bot configuration from config.yaml
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize the Telegram bot
bot = telegram.Bot(token=config["telegram_bot_token"])

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# Define the different conversation modes and their prompts
modes = {
    "casual": "Let's chat! What's on your mind?",
    "professional": "Welcome. How can I assist you today?",
    "romantic": "Hey, my love. What's on your mind?",
}

# Define a function to generate a response using the OpenAI API
def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].text.strip()


# Define the Telegram bot command handlers
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text(
        f"Hi {update.effective_user.first_name}! I'm {config['bot_name']}. "
        f"To get started, type /mode to select a conversation mode."
    )


def mode(update, context):
    """Switch the conversation mode."""
    chat_id = update.message.chat_id
    mode = context.args[0]

    if mode not in modes:
        update.message.reply_text("Invalid mode. Please choose from: " + ", ".join(modes.keys()))
        return

    context.user_data["mode"] = mode
    update.message.reply_text(f"Conversation mode set to {mode}. " + modes[mode])


def text(update, context):
    """Echo the user's message."""
    chat_id = update.message.chat_id
    mode = context.user_data.get("mode", "casual")
    prompt = modes[mode]

    # Add the user's message to the prompt
    prompt += "\n" + update.message.text

    # Generate a response using the OpenAI API
    response = generate_response(prompt)

    # Send the response back to the user
    update.message.reply_text(response)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = telegram.Updater(token=config["telegram_bot_token"], use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the command handlers
    dispatcher.add_handler(telegram.ext.CommandHandler("start", start))
    dispatcher.add_handler(telegram.ext.CommandHandler("mode", mode))
    dispatcher.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, text))

    # Start the Bot
    updater.start_polling()
    logger.info("Bot started. Press Ctrl-C to stop.")

    updater.idle()


if __name__ == "__main__":
    main()
