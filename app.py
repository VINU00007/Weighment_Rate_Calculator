import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "8685263578:AAFHGgSNLunjIMFZVNvRqtA4cg7amPXlumI"


async def rate_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    text = (message.text or "").strip().lower()

    # Accept only numbers or "rate 330"
    if not text.startswith("rate"):
        if not re.fullmatch(r"\d+(\.\d+)?", text):
            return

    # Check if replying
    reply = message.reply_to_message

    if reply is None:
        await message.reply_text(
            "Reply to the weighment message to calculate the amount."
        )
        return

    # Detect rate
    try:
        if text.startswith("rate"):
            rate = float(text.split()[1])
        else:
            rate = float(text)
    except:
        await message.reply_text("Send a number like: 250")
        return

    # Extract original message text safely
    original = ""

    if reply.text:
        original = reply.text
    elif reply.caption:
        original = reply.caption

    if not original:
        await message.reply_text(
            "Could not read the weighment message."
        )
        return

    # Extract data from weighment message
    net = re.search(r"NET LOAD\s*:\s*(\d+)", original)
    rst = re.search(r"RST\s*:\s*(\d+)", original)
    vehicle = re.search(r"🚛\s*([A-Z0-9\-]+)", original)

    party = re.search(r"👤\s*(.+)", original)
    material = re.search(r"MATERIAL\s*:\s*(.+)", original)
    bags = re.search(r"BAGS\s*:\s*(\d+)", original)
    time_match = re.search(r"OUT\s*[›>]\s*(.+)", original)

    if not net:
        await message.reply_text(
            "Net weight not found in the replied message."
        )
        return

    net_kg = int(net.group(1))
    quintals = net_kg / 100
    total = int(quintals * rate)

    msg = (
        "💰 PAYMENT CALCULATION\n\n"
        f"🧾 RST No : {rst.group(1) if rst else '-'}\n"
        f"🚛 Vehicle : {vehicle.group(1) if vehicle else '-'}\n\n"
        f"👤 Party : {party.group(1) if party else '-'}\n"
        f"🌾 Material : {material.group(1) if material else '-'}\n"
        f"📦 Bags : {bags.group(1) if bags else '-'}\n\n"
        f"🕒 Weighment Time : {time_match.group(1) if time_match else '-'}\n\n"
        f"⚖ Net Weight : {net_kg:,} Kg\n"
        f"📊 Net Quintals : {quintals:.2f}\n\n"
        f"💵 Rate : ₹{rate}\n\n"
        "━━━━━━━━━━━━━━━━\n"
        f"💰 TOTAL AMOUNT : ₹{total:,}\n"
        "━━━━━━━━━━━━━━━━"
    )

    await message.reply_text(msg)


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, rate_reply)
    )

    print("Rate Calculator Bot Running...")

    app.run_polling()


if __name__ == "__main__":
    main()