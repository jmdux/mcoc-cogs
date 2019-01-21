'''Scouter Lens Bot Discord Cog'''
import os
import logging
import discord
from discord.ext import commands
import requests


AWD_API_URL = os.environ['SCOUTER_LENS_BOT_AWD_API_URL']
MAS_API_URL = os.environ['SCOUTER_LENS_BOT_MAS_API_URL']

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
    async def _scout(self, ctx, map_or_tier, node, champ_hp, champ_atk, champ_filter=None):
        '''Scouter Lens Bot command'''
        data = {'difficulty': map_or_tier, 'node': node, 'hp': champ_hp, 'atk': champ_atk}
        if champ_filter:
            star_filter, class_filter = await self.parse_champ_filter(champ_filter)
            if star_filter:
                data['star_filter'] = star_filter
            if class_filter:
                data['class_filter'] = class_filter

        response = await self.send_request(AWD_API_URL, data=data)
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


    async def send_request(self, url, data):
        ''' Send request to service'''
        response = requests.post(url, json=data)
        if response.status_code == 200 or response.status_code == 400:
            return response.json()
        else:
            return {'error': 'unknown response'}


    async def format_champ(self, champ, champ_class):
        ''' Format champ name for display '''
        return '{0} {1}★ {2} r{3}'.format(
            self.class_emoji[champ_class],
            champ[0],
            champ[2:-2],
            champ[-1]
        )

    async def parse_champ_filter(self, champ_filter):
        star_filter = ''.join(ch for ch in champ_filter if ch.isdigit())
        champ_filter = ''.join(ch for ch in champ_filter if ch.isalpha())
        return star_filter, champ_filter


    @commands.command(pass_context=True, name='mas')
    async def _mas(self, ctx, base_hp, profile_hp, base_atk, profile_atk):
        ''' Find player masteries'''
        data = {'base_hp': base_hp, 'profile_hp': profile_hp, 'base_atk': base_atk, 'profile_atk': profile_atk}
        response = await self.send_request(MAS_API_URL, data=data)
        if 'error' in response:
            result_em = discord.Embed(color=discord.Color.red())
            result_em.add_field(name='Error', value=str(response['error']))
        else:
            result_em = discord.Embed(color=discord.Color.green())
            if len(response) > 0:
                masteries = ''
                for x in response:
                    masteries += 'vit:{0} gvit:{1} str:{2} gstr:{3} gc:{4} lcde:{5}'.format(
                        x["v"],
                        x["gv"],
                        x["s"],
                        x["gs"],
                        x["gc"],
                        x["lcde"]
                    )
            else:
                masteries = 'No matches'
            result_em.add_field(
                name='Mastery Results',
                value=masteries
            )
        
        await self.bot.say(embed=result_em)


def setup(bot):
    '''Setup Cog'''
    bot.add_cog(Scouter(bot))
