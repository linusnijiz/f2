import discord
from discord.ext import commands

from app import app     # Flask-App importieren
from models import User
from database import db

# Discord Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot ist eingeloggt als {bot.user}")


@bot.command()
async def setplan(ctx, email, plan):
    with app.app_context():   # 👈 WICHTIG: Flask Kontext aktivieren!
        user = User.query.filter_by(email=email).first()

        if not user:
            return await ctx.send("❌ User nicht gefunden!")

        user.plan = plan
        db.session.commit()

    await ctx.send(f"✅ Plan von {email} wurde auf **{plan}** gesetzt.")


@bot.command()
async def addmoney(ctx, email, amount: float):
    with app.app_context():
        user = User.query.filter_by(email=email).first()

        if not user:
            return await ctx.send("❌ User nicht gefunden!")

        user.balance += amount
        db.session.commit()

    await ctx.send(f"💰 {amount}€ zu {email} hinzugefügt.")


@bot.command()
async def balance(ctx, email):
    with app.app_context():
        user = User.query.filter_by(email=email).first()

        if not user:
            return await ctx.send("❌ Benutzer nicht gefunden!")

        await ctx.send(
            f"💰 **Kontostand von {user.username}:**\n"
            f"{user.balance} €"
        )

@bot.command()
async def affiliatecheck(ctx, email):
    with app.app_context():
        user = User.query.filter_by(email=email).first()

        if not user:
            return await ctx.send("❌ Benutzer nicht gefunden!")

        if not user.referred_by:
            return await ctx.send(f"ℹ️ {user.username} wurde von niemandem geworben.")

        inviter = User.query.filter_by(referral_code=user.referred_by).first()

        if not inviter:
            return await ctx.send("❌ Der Werber konnte nicht gefunden werden (DB-Fehler).")

        await ctx.send(
            f"👤 **Affiliate-Info:**\n"
            f"Der Benutzer **{user.username} ({user.email})** wurde geworben von:\n"
            f"➡️ **{inviter.username} ({inviter.email})**"
        )


@bot.command()
async def resetmoney(ctx, email):
    with app.app_context():
        user = User.query.filter_by(email=email).first()

        if not user:
            return await ctx.send("❌ User nicht gefunden!")

        user.balance = 0
        db.session.commit()

    await ctx.send(f"🔄 Kontostand von {email} wurde zurückgesetzt.")

import os
bot.run(os.getenv("DISCORD_TOKEN"))
