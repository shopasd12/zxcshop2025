import os 
import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import requests

from myserver import server_on

intents = discord.Intents.default()
intents.message_content = True  

bot = commands.Bot(command_prefix='!', intents=intents)

tickets = {}

WEBHOOK_URL = "https://discord.com/api/webhooks/1324846311526109285/i9iwmQ6SBJxSx7V5ewfVYbXnbGI_i_qAc_bBD6aZFsX8jCE_M0RyLj3JNrYHCibrLQ-f"  # เปลี่ยนเป็น URL ของ Webhook ของคุณ

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    await bot.change_presence(
        activity=discord.Streaming(name="กำลังสตรีม!", url="https://www.twitch.tv/your_channel")
    )
    
    channel_id = 1320391859754897484  

    channel = bot.get_channel(channel_id)
    if channel:
      
        button = Button(label="เปิดตั๋ว", style=discord.ButtonStyle.green)
        promote_button = Button(label="แจ้งปัญหา", style=discord.ButtonStyle.blurple) 

        view = View()
        view.add_item(button)
        view.add_item(promote_button)  

        await channel.send(
            "คลิกปุ่มเพื่อเปิดตั๋ว หรือแจ้งปัญหาง้าบ🧇\n"
            "แอดมินเด็ก🧀: ![ลิ้งgif](https://media.giphy.com/media/5Xypgz1EScTuw/giphy.gif)", 
            view=view
        )

        async def button_callback(interaction):
            user = interaction.user
            if user.id in tickets:
                await interaction.response.send_message(f'{user.mention}, คุณมีตั๋วที่เปิดอยู่แล้ว!', ephemeral=True)
            else:
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),  
                    user: discord.PermissionOverwrite(read_messages=True),
                }

                for role in interaction.guild.roles:
                    if role.permissions.administrator:
                        overwrites[role] = discord.PermissionOverwrite(read_messages=True)

                ticket_channel = await interaction.guild.create_text_channel(f'ticket-{user.name}', overwrites=overwrites)
                tickets[user.id] = ticket_channel.id  

                close_button = Button(label="ปิดตั๋ว", style=discord.ButtonStyle.red)

                close_view = View()
                close_view.add_item(close_button)

                await ticket_channel.send(
                    f'สวัสดี {user.mention}, 🍿ตั๋วของคุณถูกเปิดแล้ว! กรุณาบอกรายละเอียดปัญหาของคุณ.',
                    embed=discord.Embed(description="🥞อยากได้บอท สวยๆ  ทักแอดมินมาน้า🥞").set_image(url="https://th.bing.com/th/id/OIP.WBeXF490v_kYZFsgvrq05gHaEK?rs=1&pid=ImgDetMain"),
                    view=close_view
                )

                async def close_button_callback(interaction):
                    if interaction.user.id == user.id:
                        await ticket_channel.delete()
                        del tickets[user.id]
                        await interaction.response.send_message(f'{user.mention}, ตั๋วของคุณได้ถูกปิดแล้ว.', ephemeral=True)
                    else:
                        await interaction.response.send_message(f'{interaction.user.mention}, คุณไม่สามารถปิดตั๋วนี้ได้.', ephemeral=True)

                close_button.callback = close_button_callback

                await interaction.response.send_message(f'{user.mention}, ตั๋วของคุณได้ถูกเปิดแล้ว!', ephemeral=True)

        button.callback = button_callback

        async def promote_button_callback(interaction):
            class PromotionModal(Modal):
                def __init__(self):
                    super().__init__(title="กรุณากรอกปัญหา🍟")

                link_input = TextInput(label="ลิงก์โปรโมต", style=discord.TextStyle.paragraph, placeholder="ใส่ข้อความ", required=True)

                async def on_submit(self, interaction: discord.Interaction):
                    data = {
                        "content": f"มีลิงก์โปรโมตใหม่จาก {interaction.user.mention}: {self.link_input.value}"
                    }
                    response = requests.post(WEBHOOK_URL, json=data)

                    if response.status_code == 204:
                        await interaction.response.send_message(f"ลิงก์โปรโมตของคุณถูกส่งเรียบร้อยแล้ว!", ephemeral=True)
                    else:
                        await interaction.response.send_message(f"เกิดข้อผิดพลาดในการส่งลิงก์โปรโมต.", ephemeral=True)

            await interaction.response.send_modal(PromotionModal())

        promote_button.callback = promote_button_callback

@bot.command()
async def closeticket(ctx):
    user = ctx.author
    if user.id not in tickets:
        await ctx.send(f'{user.mention}, คุณยังไม่มีตั๋วเปิด.')
        return

    ticket_channel_id = tickets[user.id]
    ticket_channel = bot.get_channel(ticket_channel_id)

    await ticket_channel.delete()
    del tickets[user.id]

    await ctx.send(f'{user.mention}, ตั๋วของคุณได้ถูกปิดแล้ว.')

@bot.command()
async def setstream(ctx, *, status: str):
    await bot.change_presence(
        activity=discord.Streaming(name=status, url="https://www.twitch.tv/your_channel")
    )
    await ctx.send(f"ตั้งสถานะสตรีมเป็น: {status}")

server_on()

bot.run(os.getenv('TOKEN'))
