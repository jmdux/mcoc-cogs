'''Scouter Lens Bot Discord Cog'''
import os
import logging
import discord
from discord.ext import commands
import requests


API_URL = os.environ['SCOUTER_LENS_BOT_API_URL']

logger = logging.getLogger('red.mcoc.scouter')
logger.setLevel(logging.INFO)


class Scouter:
    '''ScouterLensBot class'''

    class_emoji = {
        'superior':'<:all2:339511715920084993>',
        'cosmic':'<:cosmic2:339511716104896512>',
        'tech':'<:tech2:339511716197171200>',
        'mutant':'<:mutant2:339511716201365514>',
        'skill':'<:skill2:339511716549230592>',
        'science':'<:science2:339511716029267969>',
        'mystic':'<:mystic2:339511716150771712>'
    }


    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True, name='scout', aliases={'awd'})
    async def _scout(self, ctx, map_or_tier, node, champ_hp, champ_atk):
        '''Scouter Lens Bot command'''
        data = {'difficulty': map_or_tier, 'node': node, 'hp': champ_hp, 'atk': champ_atk}
        response = await self.send_request(data=data)
        if 'error' in response:
            result_em = discord.Embed(color=discord.Color.red(), title='Scout Error')
            result_em.add_field(name='Error', value=str(response['error']))
        else:
            result_em = discord.Embed(color=discord.Color.green(), title='Scout Results')
            for x in response:
                champ_name = await self.format_champ(x['champ'], x['class'])
                result_em.add_field(
                    name=champ_name,
                    value='vit:{0} gvit:{1} str:{2} gstr:{3} gc:{4} lcde:{5}'.format(
                        x["masteries"]["v"],
                        x["masteries"]["gv"],
                        x["masteries"]["s"],
                        x["masteries"]["gs"],
                        x["masteries"]["gc"],
                        x["masteries"]["lcde"]
                    )
                )
        await self.bot.say(embed=result_em)


    async def send_request(self, data):
        ''' Send request to service'''
        response = requests.post(API_URL, json=data)
        if response.status_code == 200 or response.status_code == 400:
            return response.json()
        else:
            print(response.status_code)
            print(response.json())
            return {'error': 'unknown response'}


    async def format_champ(self, champ, champ_class):
        ''' Format champ name for display '''
        return '{0} {1}★ {2} r{3}'.format(
            self.class_emoji[champ_class],
            champ[0],
            champ[2:-2],
            champ[-1]
        )


def setup(bot):
    '''Setup Cog'''
    bot.add_cog(Scouter(bot))
