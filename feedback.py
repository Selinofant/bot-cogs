import discord
from discord.ext import commands
from discord.commands import slash_command
from discord.commands import Option
import json #nicht nötig, wenn channel nicht über json gespeichert sind

with open("Channel.json") as channel:#nur, wenn channel in json gespeichert werden
    channel = json.load(channel)

feedback = channel["feedback"] #hier kommt die channel-ID des channels hin, in den Feedback/Beschwerden/Vorschläge gesendet werdn sollen
voting = channel["vorschläge"] #hier kommt die forums-ID hin, wo die Vorschläge gepostet werden sollen


class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
#slash-command mit 3 verschiedenen Optionen, aus denen der User auswählt
    @slash_command(description="Gib Feedback, reiche einen Vorschlag/Beschwerde ein")
    async def feedback(self, ctx, art:Option(str, choices=["Feedback", "Vorschlag", "Beschwerde"])):

#Unterscheidung nach Feedback, Vorschlag und Beschwerde
        if art == "Feedback":
            modal = FeedbackModal(title="Teile dein Feedback")
            await ctx.send_modal(modal)

        if art == "Vorschlag":
            modal = VorschlagModal(title="Reiche einen Vorschlag ein")
            await ctx.send_modal(modal)

        if art == "Beschwerde":
            modal = BeschwerdeModal(title="Reiche eine Beschwerde ein")
            await ctx.send_modal(modal)


#Modal für Feedback
class FeedbackModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Titel deines Feedbacks",
                placeholder="Schreibe etwas...",
                max_length=50
            ),
            discord.ui.InputText(
                label="Feedback",
                placeholder="Schreibe etwas...",
                style=discord.InputTextStyle.long,
                max_length=1000
            ),
            *args,
            **kwargs
        )

    async def callback(self, interaction):
        embed = discord.Embed(
            title="Feedback",
            description=self.children[0].value,
            color=discord.Color.from_rgb(56, 165, 125)
        )
        Autor = f"Name: {interaction.user.name},  <@{interaction.user.id}>"
        embed.add_field(name="Feedback von: ", value=Autor, inline=False)
        embed.add_field(name="Beschreibung:", value=self.children[1].value, inline=False)

        channel = interaction.guild.get_channel(feedback)
        await interaction.response.send_message("Alles klar, wir haben dein Feedback erhalten", ephemeral=True)
        await channel.send(embed=embed)


#Modal für Vorschläge
class VorschlagModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Titel deines Vorschlags",
                placeholder="Schreibe etwas...",
                max_length=50

            ),
            discord.ui.InputText(
                label="Beschreibung",
                placeholder="Schreibe etwas...",
                style=discord.InputTextStyle.long,
                max_length=1000
            ),
            *args,
            **kwargs
        )

    async def callback(self, interaction):
        embed = discord.Embed(
            title="Vorschlag",
            description=self.children[0].value,
            color=discord.Color.from_rgb(255, 255, 153)
        )

        Autor = f"Name: {interaction.user.name},  <@{interaction.user.id}>"
        embed.add_field(name="Vorschlag von: ", value=Autor, inline=False)
        embed.add_field(name="Beschreibung:", value=self.children[1].value, inline=False)

        vorschlag = interaction.guild.get_channel(voting)
        vote = await vorschlag.create_thread(
            name=self.children[0].value,
            content=self.children[1].value
        )
        await vote.starting_message.add_reaction(emoji='👍')
        await vote.starting_message.add_reaction(emoji='👎')

        channel = interaction.guild.get_channel(feedback)
        await channel.send(embed=embed)
        await interaction.response.send_message("Alles klar, wir haben deinen Vorschlag erhalten", ephemeral=True)


#Modal für Beschwerden  
class BeschwerdeModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Titel deiner Beschwerde",
                placeholder="Worum geht es?",
                max_length=50
            ),
            discord.ui.InputText(
                label="Beschreibung",
                placeholder="Schreibe etwas...",
                style=discord.InputTextStyle.long,
                max_length=800

            ),
            discord.ui.InputText(
                label="Wie geht es weiter?",
                placeholder="Was wünscht du dir? Wie können wir das Problem gemeinsam lösen?",
                style=discord.InputTextStyle.long,
                max_length=800
            ),
            *args,
            **kwargs
        )

    async def callback(self, interaction):
        embed = discord.Embed(
            title="Beschwerde",
            description=self.children[0].value,
            color=discord.Color.from_rgb(204, 0, 0)
        )

        Autor = f"Name: {interaction.user.name},  <@{interaction.user.id}>"
        embed.add_field(name="Beschwerde von: ", value=Autor, inline=False)
        embed.add_field(name="Beschreibung:", value=self.children[1].value, inline=False)
        embed.add_field(name="Wunsch, wie das Problem gelöst wird: ", value=self.children[2].value, inline=False)

        channel = interaction.guild.get_channel(feedback)
        await interaction.response.send_message("Alles klar, wir haben deine Beschwerde erhalten", ephemeral=True)
        await channel.send(embed=embed)

#Cog-Einbindung
def setup(bot):
    bot.add_cog(Feedback(bot))

