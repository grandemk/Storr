#!/usr/bin/env python3

import discord
from discord.ext import commands
import argparse
import sqlite3

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("token", help="Discord token")
    p.add_argument("database", help="Database used by Storr")
    p.add_argument("--init_db", action="store_true", help="Launch once to initialize the database")
    return p.parse_args()

def init_db(conn):
    conn.execute("create table mappings (key integer not null primary key, value text);")

class MyBot(commands.Bot):
  def __init__(self):
      super().__init__(command_prefix = "!")

def main():
    args = parse_args()

    conn = sqlite3.connect(args.database)

    if args.init_db:
        init_db(conn)
        return

    bot = MyBot()

    @bot.command(help="<nom de la conférence> Ajoute une conférence")
    async def store(ctx, value):
        with conn:
            conn.execute("insert into mappings(value) values(?);", (value, ))

        embed = discord.Embed(title="Storr reports", description="Stored {}".format(value))
        await ctx.send(embed=embed)

    @bot.command(help="<id> Affiche une conférence")
    async def get(ctx, key):
        value = "Not found"

        r = conn.execute("select value from mappings where key is ?;", (key, )).fetchone()
        if r:
            value = r[0]

        embed = discord.Embed(title="Storr reports", description="[{0}] {1}".format(key, value))
        await ctx.send(embed=embed)

    @bot.command(help="<id> Supprime une conférence")
    async def delete(ctx, key):
        with conn:
            conn.execute("delete from mappings where key = ?;", (key,))

    @bot.command(help="<msg> Say something with the bot")
    async def say(ctx, msg):
        await ctx.send(msg)

    @bot.command(help="Liste des conférences proposées")
    async def list(ctx):
        description = ""
        for r in conn.execute("select key, value from mappings;"):
            description += "[{}] {}\n".format(r[0], r[1])

        embed = discord.Embed(title="Liste des conférences proposées", description=description)

        await ctx.send(embed=embed)

    bot.run(args.token)


if __name__ == "__main__":
    main()
