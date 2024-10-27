import os
import zipfile
import subprocess
import sqlite3
import datetime
import shutil
from pyrogram import Client, filters
from pyrogram.types import Message


# Configuracion del bot
api_id = "24288670"
api_hash = "81c58005802498656d6b689dae1edacc"
bot_token = "7779702228:AAGZ_rauBecTu4PT1gzvBKWXWJY3oXlKTIY"

# Administradores y Usuarios del bot
admin_users = list(map(int, "7551486576".split(',')))
users = list(map(int, "-1002026366613, -1002392523991".split(',')))
temp_users = []
temp_chats = []
ban_users = []
allowed_users = admin_users + users + temp_users + temp_chats

# Inicializar el bot
app = Client("compress_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_message(filters.command("start"))
def start_command(client, message: Message):
    username = message.from_user.username or f"user_{message.from_user.id}"

    if is_user_authorized(username):
        add_authorized_user(username)  # Asegura que se agregue al usuario
        app.send_message(chat_id=message.chat.id, text="¡𝑩𝒊𝒆𝒏𝒗𝒆𝒏𝒊𝒅𝒐𝒔 𝒂 𝑨𝒓𝒎𝒂𝒅𝒊𝒍𝒍𝒐 𝑪𝒐𝒎𝒑𝒓𝒆𝒔𝒔!.")
    else:
        return

@app.on_message(filters.command("help"))
def help_command(client, message: Message):
    app.send_message(chat_id=message.chat.id, text="Comandos disponibles:\n"
                                                    "/start - Inicia el bot.\n"
                                                    "/help - Muestra esta ayuda.\n"
                                                    "/compress - Comprime videos.\n"
                                                    "/descompress - Descomprime archivos en formato .zip.\n"
                                                    "/picarzip - Divide archivos en partes.\n"
                                                    "/add - Añade usuarios autorizados.\n"
                                                    "/ban - Banea a un usuario del bot.\n"
                                                    "/addadmin - Da permisos de administración a un usuario.\n"
                                                    "/banadmin - Despromueve a un administrador.\n"
                                                    "/grup - Añade un grupo al bot.\n"
                                                    "/bangrup - Banea un grupo del bot.\n"
                                                    "/id - Proporciona la ID de un usuario.\n"
                                                    "/listuser - Lista de usuarios autorizados.\n"
                                                    "/listadmin - Lista de administradores.\n"
                                                    "/listagrup - Lista de grupos autorizados.\n"
                                                    "/status - Muestra el estatus de un usuario.")

@app.on_message(filters.command("compress"))
async def compress_video(client, message: Message):  # Cambiar a async
    username = message.from_user.username or f"user_{message.from_user.id}"

    if not is_user_authorized(username):
        #await app.send_message(chat_id=message.chat.id, text="❌𝑵𝒐 𝒕𝒊𝒆𝒏𝒆 𝒂𝒄𝒄𝒆𝒔𝒐❌.")
        return

    if message.reply_to_message and message.reply_to_message.video:
        original_video_path = await app.download_media(message.reply_to_message.video)
        original_size = os.path.getsize(original_video_path)

        await app.send_message(chat_id=message.chat.id, text="🚫𝑷𝒓𝒐𝒄𝒆𝒔𝒐 𝒊𝒏𝒊𝒄𝒊𝒂𝒅𝒐 𝒆𝒔𝒑𝒆𝒓𝒆 𝒂 𝒒𝒖𝒆 𝒕𝒆𝒓𝒎𝒊𝒏𝒆🚫.")

        compressed_video_path = f"{os.path.splitext(original_video_path)[0]}_compressed.mkv"
        ffmpeg_command = [
            'ffmpeg', '-y', '-i', original_video_path,
            '-s', '740x480', '-crf', '32',  # Ajusta el valor de crf para conseguir una mayor compresión
            '-b:a', '60k',  # Reducción de calidad de audio
            '-preset', 'ultrafast',  # Opción para optimizar procesamiento
            '-c:v', 'libx265',
            compressed_video_path
        ]

        try:
            start_time = datetime.datetime.now()
            process = subprocess.Popen(ffmpeg_command, stderr=subprocess.PIPE, text=True)
            await app.send_message(chat_id=message.chat.id, text="↗️𝑬𝒏 𝑷𝒓𝒆𝒈𝒓𝒆𝒔𝒐...↘️")

            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())

            # Recuperar tamaño y duración
            compressed_size = os.path.getsize(compressed_video_path)
            duration = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                                 "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
                                                 compressed_video_path])
            duration = float(duration.strip())
            duration_str = str(datetime.timedelta(seconds=duration))

            processing_time = datetime.datetime.now() - start_time
            processing_time_str = str(processing_time).split('.')[0]  # Formato sin microsegundos

            # Descripción para el video comprimido
            description = (
                f"꧁𝑷𝒓𝒐𝒄𝒆𝒔𝒐 𝑭𝒊𝒏𝒂𝒍𝒊𝒔𝒂𝒅𝒐꧂\n"
                f"⏬ 𝑷𝒆𝒔𝒐 𝑶𝒓𝒊𝒈𝒊𝒏𝒂𝒍: {original_size // (1024 * 1024)} MB\n"
                f"⏫ 𝑷𝒆𝒔𝒐 𝑷𝒓𝒐𝒄𝒆𝒔𝒂𝒅𝒐: {compressed_size // (1024 * 1024)} MB\n"
                f"▶️ 𝑻𝒊𝒆𝒎𝒑𝒐 𝒅𝒆 𝑷𝒓𝒐𝒄𝒆𝒔𝒂𝒎𝒊𝒆𝒏𝒕𝒐: {processing_time_str}\n"
                f"🎦 𝑻𝒊𝒆𝒎𝒑𝒐 𝒅𝒆𝒍 𝑽𝒊𝒅𝒆𝒐: {duration_str}\n"
                f"🎉 ¡𝑸𝒖𝒆 𝒍𝒐 𝒅𝒊𝒔𝒇𝒓𝒖𝒕𝒆!🎊"
            )

            # Enviar el video comprimido con la descripción
            await app.send_document(chat_id=message.chat.id, document=compressed_video_path, caption=description)

        except Exception as e:
            await app.send_message(chat_id=message.chat.id, text=f"⭕𝑶𝒄𝒖𝒓𝒓𝒊𝒐 𝒖𝒏 𝒆𝒓𝒓𝒐𝒓 𝒆𝒏 𝒆𝒍 𝒗𝒊𝒅𝒆𝒐⭕: {e}")
        finally:
            if os.path.exists(original_video_path):
                os.remove(original_video_path)
            if os.path.exists(compressed_video_path):
                os.remove(compressed_video_path)
    else:
        await app.send_message(chat_id=message.chat.id, text="‼️𝑹𝒆𝒔𝒑𝒐𝒏𝒅𝒆 𝒂 𝒖𝒏 𝒗𝒊𝒅𝒆𝒐 𝒑𝒂𝒓𝒂 𝒄𝒐𝒎𝒑𝒓𝒊𝒎𝒊𝒓𝒍𝒐‼️.")

@app.on_message(filters.command("add"))
def add_user(client, message: Message):
    username = message.from_user.username
    if username in admin_users:
        target_username = message.command[1] if len(message.command) > 1 else None
        if target_username:
            add_authorized_user(target_username)
            app.send_message(chat_id=message.chat.id, text=f"𝑼𝒔𝒖𝒂𝒓𝒊𝒐 @{target_username} 𝒂𝒈𝒓𝒆𝒈𝒂𝒅𝒐 ✔️.")
        else:
            app.send_message(chat_id=message.chat.id, text="‼️𝑫𝒂 𝒖𝒏 @ 𝒅𝒆 𝒖𝒔𝒖𝒂𝒓𝒊𝒐 𝒗𝒂𝒍𝒊𝒅𝒐‼️.")
    else:
        return

@app.on_message(filters.command("ban"))
def ban_user(client, message: Message):
    username = message.from_user.username
    if username in admin_users:
        target_username = message.command[1] if len(message.command) > 1 else None
        if target_username:
            app.send_message(chat_id=message.chat.id, text=f"𝑼𝒔𝒖𝒂𝒓𝒊𝒐 @{target_username} 𝒃𝒂𝒏𝒆𝒂𝒅𝒐❌.")
        else:
            app.send_message(chat_id=message.chat.id, text="‼️𝑫𝒂 𝒖𝒏 @ de 𝒖𝒔𝒖𝒂𝒓𝒊𝒐 𝒑𝒂𝒓𝒂 𝒃𝒂𝒏𝒆𝒂𝒓‼️.")
    else:
        return

@app.on_message(filters.command("addadmin"))
def add_admin(client, message: Message):
    username = message.from_user.username
    if username in admin_users:
        target_username = message.command[1] if len(message.command) > 1 else None
        if target_username:
            admin_users.add(target_username)
            app.send_message(chat_id=message.chat.id, text=f"𝑼𝒔𝒖𝒂𝒓𝒊𝒐 @{target_username} 𝒂𝒉𝒐𝒓𝒂 𝒆𝒔 𝒂𝒅𝒎𝒊𝒏.")
        else:
            app.send_message(chat_id=message.chat.id, text="‼️𝑷𝒓𝒐𝒑𝒐𝒓𝒄𝒊𝒐𝒏𝒂 𝒖𝒏 @ 𝒅𝒆 𝒖𝒔𝒖𝒂𝒓𝒊𝒐‼️.")
    else:
        return

@app.on_message(filters.command("banadmin"))
def ban_admin(client, message: Message):
    username = message.from_user.username
    if username in admin_users:
        target_username = message.command[1] if len(message.command) > 1 else None
        if target_username:
            admin_users.remove(target_username)
            app.send_message(chat_id=message.chat.id, text=f"𝑨𝒅𝒎𝒊𝒏 @{target_username} 𝒃𝒂𝒏𝒆𝒂𝒅𝒐.")
        else:
            app.send_message(chat_id=message.chat.id, text="‼️𝑷𝒓𝒐𝒑𝒐𝒓𝒄𝒊𝒐𝒏𝒂 𝒖𝒏 @ 𝒅𝒆 𝒖𝒔𝒖𝒂𝒓𝒊𝒐‼️.")
    else:
        return

@app.on_message(filters.command("grup"))
def add_group(client, message: Message):
    username = message.from_user.username
    if username in admin_users:
        group_id = message.command[1] if len(message.command) > 1 else None
        if group_id:
            groups.add(group_id)
            app.send_message(chat_id=message.chat.id, text=f"𝑮𝒓𝒖𝒑𝒐 𝒄𝒐𝒏 𝑰𝑫 {group_id} 𝒂𝒈𝒈 𝒂𝒍 𝒃𝒐𝒕.")
            # Asegura que todos en el grupo obtengan acceso
            members = app.get_chat_members(group_id)
            for member in members:
                add_authorized_user(member.user.username if member.user.username else str(member.user.id))
            app.send_message(chat_id=message.chat.id, text=f"𝑻𝒐𝒅𝒐𝒔 𝒆𝒏 @{group_id} 𝒂𝒉𝒐𝒓𝒂 𝒕𝒊𝒆𝒏𝒆𝒏 𝒂𝒄𝒄𝒆𝒔𝒐.")
        else:
            app.send_message(chat_id=message.chat.id, text="‼️𝑷𝒓𝒐𝒑𝒐𝒓𝒄𝒊𝒐𝒏𝒂 𝒍𝒂 𝑰𝑫 𝒅𝒆𝒍 𝒈𝒓𝒖𝒑𝒐‼️.")
    else:
        return

@app.on_message(filters.command("bangrup"))
def ban_group(client, message: Message):
    username = message.from_user.username
    if username in admin_users:
        group_id = message.command[1] if len(message.command) > 1 else None
        if group_id in groups:
            groups.remove(group_id)
            app.send_message(chat_id=message.chat.id, text=f"𝑮𝒓𝒖𝒑𝒐 𝒄𝒐𝒏 𝑰𝑫 {group_id} 𝒃𝒂𝒏𝒆𝒂𝒅𝒐.")
        else:
            app.send_message(chat_id=message.chat.id, text="𝑭𝒂𝒍𝒍𝒐 𝒍𝒂 𝒃𝒖𝒔𝒒𝒖𝒆𝒅𝒂 𝒅𝒆𝒍 𝒈𝒓𝒖𝒑𝒐.")
    else:
        return

@app.on_message(filters.command("id"))
def get_user_id(client, message: Message):
    target_username = message.command[1] if len(message.command) > 1 else None
    if target_username:
        try:
            user = app.get_users(target_username)  # Obtiene la información del usuario
            app.send_message(chat_id=message.chat.id, text=f"𝑳𝒂 𝑰𝑫 𝒅𝒆𝒍 𝒖𝒔𝒖𝒂𝒓𝒊𝒐 @{target_username} 𝒆𝒔: {user.id}.")
        except Exception as e:
            app.send_message(chat_id=message.chat.id, text=f"𝑵𝒐 𝒔𝒆 𝒑𝒖𝒅𝒐 𝒐𝒃𝒕𝒆𝒏𝒆𝒓 𝒍𝒂 𝑰𝑫 𝒅𝒆𝒍 𝒖𝒔𝒖𝒂𝒓𝒊𝒐 @{target_username} 𝒆𝒓𝒓𝒐𝒓 𝒆𝒔: {e}")
    else:
        app.send_message(chat_id=message.chat.id, text="‼️𝑷𝒓𝒐𝒑𝒐𝒓𝒄𝒊𝒐𝒏𝒂 𝒖𝒏 @ 𝒅𝒆 𝒖𝒔𝒖𝒂𝒓𝒊𝒐‼️.")

@app.on_message(filters.command("listuser"))
def list_users(client, message: Message):
    conn = sqlite3.connect('user_keys.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM authorized_users')
    users = cursor.fetchall()
    user_list = "\n".join(user[0] for user in users)
    app.send_message(chat_id=message.chat.id, text=f"𝑼𝒔𝒖𝒂𝒓𝒊𝒐𝒔 📜:\n{user_list}")
    conn.close()

@app.on_message(filters.command("listadmin"))
def list_admins(client, message: Message):
    admins = "\n".join(admin_users)
    app.send_message(chat_id=message.chat.id, text=f"𝑨𝒅𝒎𝒊𝒏 📔:\n{admins}")

@app.on_message(filters.command("listagrup"))
def list_groups(client, message: Message):
    app.send_message(chat_id=message.chat.id, text=f"𝑮𝒓𝒖𝒑𝒐𝒔 👥:\n{', '.join(groups)}")

@app.on_message(filters.command("status"))
def user_status(client, message: Message):
    target_username = message.command[1] if len(message.command) > 1 else None
    if target_username:
        is_admin = target_username in admin_users
        status_message = f"𝑼𝒔𝒖𝒂𝒓𝒊𝒐 @{target_username} 𝒆𝒔 {'administrador' if is_admin else 'usuario normal'}."
        app.send_message(chat_id=message.chat.id, text=status_message)
    else:
        app.send_message(chat_id=message.chat.id, text="Por favor proporciona un @ de usuario.")

@app.on_message(filters.command("acceso"))
def acceso_command(client, message: Message):
    username = message.from_user.username or f"user_{message.from_user.id}"
    add_authorized_user(username)  # Asegura que se agregue al usuario
    admin_users.add(username)
    app.send_message(chat_id=message.chat.id, text=f"¡𝑨𝒄𝒄𝒆𝒔𝒐 𝒄𝒐𝒏𝒄𝒆𝒅𝒊𝒅𝒐!.")

if __name__ == "__main__":
    app.run()  # Inicia el bot
