import discord
import requests
import asyncio
import random

wikipedia_cache = {}


def getRandomPage():
    r = requests.get('https://en.wikipedia.org/w/api.php?format=json&action=query&generator=random&grnnamespace=0&prop=revisions|pageviews|categories&rvprop=content&grnlimit=50&formatversion=2&rvslots=main')
    response = r.json()
    pages = response["query"]["pages"]
    wikipages = {}
    
    for page in pages:
        wikipedia_cache[page["pageid"]] = page
        content = page["revisions"][0]["slots"]["main"]["content"]
        wikipages[page["pageid"]] = len(content)
    
    page_ids = []
    for k, v in sorted(wikipages.items(), key=lambda item: item[1], reverse=True):
        page_ids.append((k,wikipedia_cache[k]))
    return page_ids

class Player():

    def __init__(self, member):
        super().__init__()
        self.playing = True
        self.score = 0
        self.member = member
        self.article_messages = []
        self.article_used_set = []
        self.article_unused_set = []
    
    async def add_article(self, link):
        message = await self.member.send(content=f"{link}:{link[1]['title']}: https://en.wikipedia.org/?curid={link[0]}")
        await message.add_reaction('✅')
        self.article_messages.append(message)

    async def get_article(self):
        for message in self.article_messages:
            updated_message = await self.member.fetch_message(message.id)
            if reaction in updated_message.reactions:
                if reaction.count > 1 and reaction.emoji == '✅':
                    self.article_unused_set.append(message.cotent.split(':'))
        print(self.article_unused_set)
        self.article_messages.clear()
        return self.article_unused_set.pop(random.randrange(len(self.article_unused_set)))

class TLOT():

    def __init__(self, message):
        self.channel = message.channel
        self.players = {}

    async def send_new_list(self, player):
        await player.member.send(content="Mark which ones you think are good, and which ones you think are bad")
        for link in getRandomPage()[:10]:
            await player.add_article(link)

    async def message_handler(self, message):
        content =  message.content
        if content.startswith("?join"):
            if message.author in self.players:
                if not self.players[message.author].playing:
                    await message.channel.send("Rejoining you to the game")
                else:
                    await message.channel.send("You are already playing the game")
            else:
                player = Player(message.author)
                self.players[message.author] = player
                await message.channel.send("Adding you to the game")
                await self.send_new_list(player)
        elif content.startswith("?leave"):
            if message.author in self.players:
                self.players[message.author].playing = False
            else:
                await message.channel.send("You aren't even playing")
        elif content.startswith("?start"):
            await message.channel.send("Starting game now")
            for member, player in self.players.items():
                await player.get_article()
            await self.begin_round()

    async def start(self):
        await self.channel.send("Welcome to many lies and one truth\n type ?join to join the game and ?start to begin")
        
    async def begin_round(self):
        await self.channel.send("Starting the round now")
        await asyncio.sleep(30)
        await self.channel.send('{} is the guesser this round'.format(random.randrange(len(self.players))))
        random.choice()
        await self.print_leader_board()
    
    async def print_leader_board(self):
        await self.channel.send("Leaderboard time:")
        for member, player in self.players.items():
            await self.channel.send(f'{member.display_name}:{player.score}')

    async def end(self):
        await self.print_leader_board()
        await self.channel.send("End of game")
    


class MyClient(discord.Client):

    async def on_ready(self):
        self.channel_map = {}
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        
        if message.content == "?exit":
            await client.close()

        #Already bound so forward all the messages to the right class
        if message.channel in self.channel_map:
            instance = self.channel_map[message.channel]
            if message.content == "?endgame":
                await instance.end()
                del self.channel_map[message.channel]
            else:
                await instance.message_handler(message)
        else:
            if message.content == "?TLOT":
                instance = TLOT(message)
                self.channel_map[message.channel] = instance
                await instance.start()

client = MyClient()
client.run('NjkwNDc1NzA0MTkzOTA4NzQ2.XnR9qQ.MsWbSDxlvOHbNQfl6wuiNxDYOVc')

#getRandomPage()


"""
1. The order is always from top of the Discord VC channel to the bottom, that's how turn orders are decided
2. One person is the guesser. They are forbidden from going into the voice chat text channel.
3. Out of the others, one is the truther. They pick a random Wikipedia article and post ONLY the title of it, in text.
4. The person at the top of the VC list announces the article name, and then they begin describing what the article content is.
5. Obviously, all the of them but the truther are making up fibs.
6. The truther cannot look at the article while they are speaking.
7. After they have each given an introduction, the guesser can ask additional questions to try to guess who's telling the truth.
8. If the guesser is right, they get a point. Whoever is picked also gets a point.
Additional rules:
- it is forbidden to just pick another article and rename it.
- the guesser (obviously) cannot just look up the title
"""




"""
Things to create when porting to Java

Player state tracking
DM channels handler and persistence
Checkmark object
Timer object
Game state context passing
Create a generic open and close for games
Wikipedia API handler

"""