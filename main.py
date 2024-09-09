import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from info import BOT_TOKEN, START_MESSAGE, HELP_MESSAGE, COMMANDS
from PIL import Image
import io

# إعداد التسجيل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# وظائف معالجة الأوامر
async def start(update: Update, context):
    await update.message.reply_text(START_MESSAGE)

async def help_command(update: Update, context):
    command_list = "\n".join([f"/{cmd} - {desc}" for cmd, desc in COMMANDS.items()])
    help_text = f"{HELP_MESSAGE}\n\nقائمة الأوامر المتاحة:\n{command_list}"
    await update.message.reply_text(help_text)

async def echo(update: Update, context):
    if context.args:
        await update.message.reply_text(' '.join(context.args))
    else:
        await update.message.reply_text("الرجاء إدخال نص بعد الأمر /echo")

async def resize_image(update: Update, context):
    if len(context.args) != 2:
        await update.message.reply_text("الرجاء إدخال العرض والارتفاع. مثال: /تصغير_صورة 300 200")
        return

    try:
        width = int(context.args[0])
        height = int(context.args[1])
    except ValueError:
        await update.message.reply_text("الرجاء إدخال أرقام صحيحة للعرض والارتفاع.")
        return

    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("الرجاء الرد على صورة بهذا الأمر.")
        return

    photo = update.message.reply_to_message.photo[-1]
    photo_file = await context.bot.get_file(photo.file_id)
    photo_bytes = await photo_file.download_as_bytearray()

    try:
        image = Image.open(io.BytesIO(photo_bytes))
        resized_image = image.resize((width, height))
        output = io.BytesIO()
        resized_image.save(output, format='JPEG')
        output.seek(0)
        await update.message.reply_photo(photo=output, caption=f"تم تصغير الصورة إلى {width}x{height}")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء معالجة الصورة: {str(e)}")

# الوظيفة الرئيسية
def main():
    # إنشاء التطبيق وإضافة المعالجات
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("echo", echo))
    application.add_handler(CommandHandler("resize_image", resize_image))  # تم تغيير الأمر هنا

    # بدء البوت
    application.run_polling()

    # إضافة معالجات للأوامر الأخرى
    for command in COMMANDS:
        if command not in ["start", "help", "echo", "resize_image"]:  # تم تحديث هذا الشرط
            application.add_handler(CommandHandler(command, echo))  # استخدم 'echo' كمعالج مؤقت

if __name__ == '__main__':
    main()
