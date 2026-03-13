import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "8685263578:AAFHGgSNLunjIMFZVNvRqtA4cg7amPXlumI"

# store weighment data using message_id
weighments = {}


async def message_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    text = message.text or ""

    # detect weighment alert
    if "WEIGHMENT ALERT" in text.upper():

        net_match = re.search(r"NET LOAD\s*:\s*(\d+)", text)
        rst_match = re.search(r"RST\s*:\s*(\d+)", text)

        if net_match:
            weighments[message.message_id] = {
                "net": int(net_match.group(1)),
                "rst": rst_match.group(1) if rst_match else "-"
            }

        return


async def rate_calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    text = (message.text or "").strip().lower()

    # accept rate or number
    try:
        if text.startswith("rate"):
            rate = float(text.split()[1])
        else:
            rate = float(text)
    except:
        return

    reply = message.reply_to_message

    if reply is None:
        await message.reply_text(
            "Reply to the weighment message to calculate the amount."
        )
        return

    weighment = weighments.get(reply.message_id)

    if not weighment:
        await message.reply_text(
            "Weighment data not found for this message."
        )
        return

    net_kg = weighment["net"]
    rst = weighment["rst"]

    quintals = net_kg / 100
    total = int(quintals * rate)

    await message.reply_text(
        f"💰 PAYMENT CALCULATION\n\n"
        f"RST : {rst}\n\n"
        f"⚖ Net Weight : {net_kg:,} Kg\n"
        f"📊 Quintals : {quintals:.2f}\n"
        f"💵 Rate : ₹{rate}\n\n"
        f"━━━━━━━━━━━━━━\n"
        f"💰 TOTAL : ₹{total:,}"
    )


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    # listen for weighment alerts
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_listener),
        group=0
    )

    # calculate rate replies
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, rate_calculator),
        group=1
    )

    print("Rate Calculator Bot Running...")

    app.run_polling()


if __name__ == "__main__":
    main()