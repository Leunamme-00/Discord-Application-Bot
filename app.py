import discord
from discord.ext import commands
import pyrebase
import asyncio
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!",intents=intents)
bot.remove_command('help')

firebaseConfig = {'removed'}

firebase = pyrebase.initialize_app(firebaseConfig) 
db2 = firebase.database()

cred = credentials.Certificate('C:/Users/emman/dev/Application-bot/sapplication-bot-80ea1-firebase-adminsdk-c1294-1c05e29bc4.json')

firebase_admin.initialize_app(cred, {"Removed"})

def get_data():
    retriveing = db2.child("applications").get()
    data = json.loads(json.dumps(retriveing.val()))
    return data

def get_roles():
    retriveing = db2.child("Roles").get()
    data = json.loads(json.dumps(retriveing.val()))
    return data


@bot.event
async def on_ready(): 
    NAME = bot.user.name
    print(f"logged in as {NAME}")
    print("-------------")

@bot.event
async def on_member_remove(member):
    data = get_data()
    for a, b in data.items():
        if "applicants" in b:
            applicants = b['applicants']
            for x, y in applicants.items():
                userid = int(y["userid"])
                if userid == member.id:
                    deleteid = db.reference(f"applications/{a}/applicants/{x}")
                    deleteid.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def create(ctx, arg):
    embed = discord.Embed(
        title='Applications creation',
        description= f"We will start to make a application fourm for the following position : {arg}\n```To cancel this action type 'cancel'And when you are done with the question tupe 'done'\nNote: maximum 10 questions```"
    )
    timeoutembed = discord.Embed(
        title="Creation of the app has been cancelled",
        description='Ooops.... you took more than 2 minutes to enter the next question'
    )
    limit = discord.Embed(
        title='Questions limit',
        description='you have hit 10 question limit the application will be save in a few seconds'
    )
    done = discord.Embed(
        title='Done',
        description='The application has been made'
    )
    await ctx.send(embed=embed)
    
    que_count = 0
    listq = []
    while que_count < 20:
        if que_count == 0 : await ctx.send("Enter the first question")
        if que_count > 0 and que_count <= 9: await ctx.send("Enter the next question question")
        try:
            question =  await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=180.0)
 
        except asyncio.TimeoutError:
            await ctx.send(embed=timeoutembed)
            break

        else:
            if question.content.lower() == "cancel":
                await ctx.send("application creation has been canceled")
                break

            elif question.content.lower() == "done":
                await ctx.send(embed=done)
                data = listq
                db2.child('applications').child(f'{arg.lower()}').child("questions").set(data)
                break
            
    
            else:
                listq = listq + [f'{question.content}']

                if que_count  >= 9:
                    data = listq
                    await ctx.send(embed=limit)
                    db2.child('applications').child(f'{arg.lower()}').child("questions").set(data)
                    break
                
        que_count = que_count + 1

@create.error
async def create_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title='Error',
            description='U have not specified the name of the application\n```command usage : !create <name>```'
        )
        await ctx.channel.send(embed=embed)

    else:
        await ctx.channel.send(f'error:\n```{error}```')


@bot.command()
async def apply(ctx,arg):
    channel = bot.get_channel(830351536331816960)
    lista = []
    data = get_data()
    UsersRoles = ctx.author.roles
    CheckRoles = get_roles()
    roled = ""
    def appCheck():
        try:
            chec = True
            applicants = data[f'{arg.lower()}']["applicants"]

        except KeyError:
            chec = True
            return chec


        else:
            for key, value in applicants.items():
                userid = value['userid']
                if userid == ctx.author.id:
                    chec = False

            return chec


    if f"{arg.lower()}" in data.keys():
        res = appCheck()
        if res == True:
            await ctx.message.add_reaction(u'\u2705')
            embed = discord.Embed(
                title='Hello!',
                description=f'You are going to fill out a forum for the application {arg} You have 3mins maximum to answer each question'
            )
            timeoutembed = discord.Embed(
                title="Creation of the app has been cancelled",
                description='Ooops.... you took more than 2 minutes to enter the next question'
            )
            embed2 = discord.Embed(
                title='Completed!',
                description="The forum has been completed. the bot will let u know if you are accepted"
            )
            embed.set_footer(text='Made by !LEUNAMME#6669')
            await ctx.author.send(embed=embed)
            
            quesiton = data[f'{arg.lower()}']['questions']
            
            for i in quesiton:
                que = discord.Embed(title=f'{i}')
                await ctx.author.send(embed=que)

                try:
                    answers =  await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.guild is None , timeout=180.0)
     
                except asyncio.TimeoutError:
                    await ctx.author.send(embed=timeoutembed)
                    break

                if answers.content.lower() == 'cancel':
                    await ctx.author.send("The forum has been canceled")
                    break
                
                else:
                    lista = lista + [f'{answers.content}']

            else:
                await ctx.author.send(embed=embed2)
                data = {"answer":lista , "userid":ctx.author.id,"status" : "pending"}
                db2.child("applications").child(f"{arg.lower()}").child('applicants').push(data)
                for i in CheckRoles:
                    rolObj = ctx.guild.get_role(i)
                    if rolObj in UsersRoles:
                        roled = roled + f"<@&{i}>,"
                emboooood = discord.Embed(title=f'Application submited by {ctx.author}')
                emboooood.set_footer(text=f'By : {ctx.author.id}',icon_url=str(ctx.author.avatar_url))
                oio = 0

                for i in lista:
                    emboooood.add_field(name=f'{quesiton[oio]}',value=f'{i}',inline=False)
                    oio = oio + 1
                
                else:
                    emboooood.add_field(name='Extra Info',value=f'**Status** : pending\n**User ID** : {ctx.author.id}\n**Roles** : {roled}')
                    await channel.send(embed=emboooood)
                    



        else:
            await ctx.message.add_reaction(u'\U0001f6ab')
            await ctx.author.send("You have already applied once for this position 🤪")            

    else:
        await ctx.message.add_reaction(u'\U0001f6ab')
        await ctx.author.send("That app is no avaliable run !applications command and try again")

@apply.error
async def apply_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title='Error',
            description='U have not specified the name of the Position you want to apply for run !applications to see the positions.\n```command usage : !apply <position>```'
        )
        await ctx.message.add_reaction(u'\U0001f6ab')
        await ctx.author.send(embed=embed)

    else:
        await ctx.channel.send(f'error:\n```{error}```')


@bot.command()
@commands.has_permissions(administrator=True)
async def review(ctx,arg):
    data = get_data()
    CheckRoles = get_roles()
    answer1 = 'APPLICATIONS NOT FOUND'
    question1 = ""
    weeee = True
    for x, y in data.items():
        if "applicants" in y:
            applicants = y['applicants']

            if arg in applicants:
                question1 = y['questions']
                status = applicants[f'{arg}']['status']
                userid = applicants[f'{arg}']['userid']
                roled = ""
                Member = ctx.guild.get_member(int(userid))
                UsersRoles = Member.roles
                answer1 = applicants[f'{arg}']['answer']
                for i in CheckRoles:
                    rolObj = ctx.guild.get_role(i)
                    if rolObj in UsersRoles:
                        roled = roled + f"<@&{i}>,"
                weeee = False
                break
    
    embed = discord.Embed(
        title = f'Application by {ctx.author}',
    )
    embed.set_footer(text=f'By : {ctx.author.id}',icon_url=str(ctx.author.avatar_url))
    
    if weeee == False :
        val = 0
        for i in question1 :
            embed.add_field(name=f'{i}' ,value=f'{answer1[val]}', inline=False)
            val = val + 1

        else:
            embed.add_field(name='Extra Info',value=f'**Status** : {status}\n**User ID** : {userid}\n**Roles** : {roled}')
            await ctx.channel.send(embed=embed)
            embed = discord.Embed(
                        title = 'Application',
                    )
            weeee = True
    
    else:
        embed_not_found = discord.Embed(
            title='Error',
            description='The Application for the ID you have enetered cant be found'
        )
        await ctx.channel.send(embed=embed_not_found)
        

@review.error
async def review_error(ctx,error):
    if isinstance(error ,commands.MissingRequiredArgument):
        CheckRoles = get_roles()
        data = get_data()
        embed = discord.Embed(
            title = 'Applications To be Reviwed',
            description = "To review applications use the folowing command ```-review <application id>```"
        )

        for x, y in data.items():
            if "applicants" in y:
                applicants = y['applicants']
                for a, b in applicants.items():
                    userid = b['userid']
                    Member = ctx.guild.get_member(int(userid))
                    roled = ""
                    UsersRoles = Member.roles
                    for i in CheckRoles:
                        rolObj = ctx.guild.get_role(i)
                        if rolObj in UsersRoles:
                            roled = roled + f"<@&{i}>,"
                    status = b['status']
                    position = x
                    if status == "pending":
                        if len(embed.fields) < 9:               
                            embed.add_field(name=f'{a}', value=f'{userid}\nstatus : {status}\nposition : {position}\nroles {roled}',inline=False)
            else:
                pass
        else:
            await ctx.channel.send(embed=embed)
    
    else:
        await ctx.channel.send(f'error : ```{error}```')

@bot.command(aliases=['roles'])
@commands.has_permissions(administrator=True)
async def role(ctx):
    data = db2.child('Roles').get()
    roled = ""
    for i in data.val():
        roled = roled + f"<@&{i}> | {i}\n"
    embed = discord.Embed(title='Roles',description=f'{roled}')
    await ctx.send(embed=embed)

@bot.command(aliases=['add_roles'])
@commands.has_permissions(administrator=True)
async def add_role(ctx):
    data = get_data()
    Var = True
    req =[]
    embed = discord.Embed(title='Config Starting',description='Enter the id of the roles you would like to be displayed when viewing a application\n```Type "cancel" when you want to cancel and "done" when you are done adding the roles```')
    message = await ctx.channel.send(embed=embed)
    while Var == True:

        try:
            roles =  await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=300.0)
     
        except asyncio.TimeoutError:
            await ctx.author.send('Cancelled.....')
            break

        else:
            if roles.content.lower() == 'done':
                if len(req) != 0 : 
                    db2.child('Roles').set(req)
                    await ctx.channel.send('Config has been completed')
                    break

                else:
                    await ctx.channel.send('No valid Ids were given | Config cancelled')
                    break

            if roles.content.lower() == 'cancel':
                await ctx.channel.send('config has been cancelled')
                break 

            else:
                try:
                    int(roles.content)

                except (TypeError, ValueError) as error:
                    await roles.add_reaction(u'\U0001f6ab')
                    await ctx.channel.send('Not a role Id')

                else:
                    roleobj = ctx.guild.get_role(int(roles.content))
                    if roleobj in ctx.guild.roles:
                        req.append(int(roles.content))
                        await roles.add_reaction(u'\u2705')

                    else:
                        await roles.add_reaction(u'\U0001f6ab')
                        await ctx.channel.send('Could not find a role with the specifed Id')
                    

@bot.group(invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def search(ctx):
    embed = discord.Embed(
        title = 'Search',
        description='This command lets you search for a applicantions with keywords like positon name / role id / status\nCommand usage :```!search <position/role/status/user> <value example moderator / 823970717045227562 / pending / 669198495533760513>```'
    )
    embed.set_footer(text='Made by : !LEUNAMME#7534 ')
    await ctx.channel.send(embed=embed)

@search.command(aliases=['pos','positions'])
@commands.has_permissions(administrator=True)
async def position(ctx,arg):
    CheckRoles = get_roles()
    data = get_data()
    embed = discord.Embed(
        title = 'Application'
    )
    embed2 = discord.Embed(
        title = 'Error',
        description = 'The position you have specified can not be found'
    )
    if arg.lower() in data:
        if "applicants" in data[f"{arg.lower()}"]:
            result = data[f"{arg.lower()}"]['applicants']
            for x, y in result.items():
                userid = y['userid']
                roled = ""
                Member = ctx.guild.get_member(int(userid))
                UsersRoles = Member.roles
                for i in CheckRoles:
                    rolObj = ctx.guild.get_role(i)
                    if rolObj in UsersRoles:
                        roled = roled + f"<@&{i}>,"
                status = y['status']
                if len(embed.fields) < 9: 
                    embed.add_field(name=f'{x}', value=f'User id : {userid}\nStatus : {status}\nRoles : {roled} ',inline=False)
            
            else:
                await ctx.channel.send(embed=embed)
        
        else:
            embed00 = discord.Embed(
                title='Ooops',
                description='No one has applied for that position'
            )
            await ctx.channel.send(embed=embed00)

    else:
        await ctx.channel.send(embed=embed2)


@position.error
async def position_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title='Error',
            description='U have not specified the name of the Position\n```command usage : !search <position/pos> <name>```'
        )
        await ctx.channel.send(embed=embed)

    else:
        await ctx.channel.send(f'error:\n```{error}```')


@search.command(aliases=['roles','roleid'])
@commands.has_permissions(administrator=True)
async def role(ctx,arg : int):
    CheckRoles = get_roles()
    data = get_data()
    chec = False
    embed = discord.Embed(
        title = 'Application'
    )
    for a, b in data.items():
        if "applicants" in b:
            applicants = b['applicants']
            for x, y in applicants.items():
                userid = int(y["userid"])
                status = y['status']
                roled = ""
                Member = ctx.guild.get_member(int(userid))
                UsersRoles = Member.roles
                for i in CheckRoles:
                    rolObj = ctx.guild.get_role(i)
                    if rolObj in UsersRoles:
                        roled = roled + f"<@&{i}>,"
                roles = ctx.guild.get_member(user_id=userid).roles 
                role_check = ctx.guild.get_role(role_id=int(arg))
                if role_check in roles:
                    if len(embed.fields) < 9: 
                        embed.add_field(name=f'{x}', value=f'User id : {userid}\nStatus : {status}\nRoles : {roled}\n position : {a}',inline=False)            
                        chec = True
            

    else:
        if chec == True:
            await ctx.channel.send(embed=embed)
        else:
            embed99 = discord.Embed(
                title ='oops',
                description='No one with that role has applied'
            )
            await ctx.channel.send(embed=embed99)

@role.error
async def role_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title='Error',
            description='U have not specified the id of the Role\n```command usage : !search role <id>```'
        )
        await ctx.channel.send(embed=embed)

    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title='Error',
            description='An id is made up of numbers try again \n```command usage : !search role <id>```'
        )
        await ctx.channel.send(embed=embed)

    else:
        await ctx.channel.send(f'error:\n```{error}```')

@search.command(aliases=['stats','statuses'])
@commands.has_permissions(administrator=True)
async def status(ctx,arg):
    CheckRoles = get_roles()
    if arg.lower() in ["pending","accepted","rejected"]:
        data = get_data()
        embed = discord.Embed(
            title = 'Application'
        )
        for a, b in data.items():
            if "applicants" in b:
                applicants = b['applicants']
                for x, y in applicants.items():
                    userid = int(y["userid"])
                    status = y['status']
                    roled = ""
                    Member = ctx.guild.get_member(int(userid))
                    UsersRoles = Member.roles
                    for i in CheckRoles:
                        rolObj = ctx.guild.get_role(i)
                        if rolObj in UsersRoles:
                            roled = roled + f"<@&{i}>,"
                    if status == arg.lower():
                        if len(embed.fields) < 9: 
                            embed.add_field(name=f'{x}', value=f'User id : {userid}\nStatus : {status}\nRoles : {roled}\n position : {a}',inline=False)            
                        
        else:
            if len(embed) == 11:
                embed003 = discord.Embed(
                    title='Ooops',
                    description=f'Could not find any application with status : {arg.lower()}'
                )
                await ctx.channel.send(embed=embed003)
            else:
                await ctx.channel.send(embed=embed)
    
    else:
        embedo = discord.Embed(
            title = 'Error',
            description='There are only 3 statuses from which u can choose <pending/accepted/rejected>'
        )
        await ctx.channel.send(embed=embedo)

@status.error
async def status_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title='Error',
            description='U have not specified the status of the Application\n```command usage : !search status <pending/acepted/rejected>```'
        )
        await ctx.channel.send(embed=embed)

    else:
        await ctx.channel.send(f'error:\n```{error}```')

@search.command(aliases=['users','userid'])
@commands.has_permissions(administrator=True)
async def user(ctx,arg : int):
    data = get_data()
    CheckRoles = get_roles()
    embed = discord.Embed(
        title = 'Application'
    )
    for a, b in data.items():
        if "applicants" in b:
            applicants = b['applicants']
            for x, y in applicants.items():
                userid = int(y["userid"])
                status = y['status']
                roled = ""
                Member = ctx.guild.get_member(int(userid))
                UsersRoles = Member.roles
                for i in CheckRoles:
                    rolObj = ctx.guild.get_role(i)
                    if rolObj in UsersRoles:
                        roled = roled + f"<@&{i}>,"
                if userid == int(arg):
                    if len(embed.fields) < 9: 
                        embed.add_field(name=f'{x}', value=f'User id : {userid}\nStatus : {status}\nRoles : {roled}\n position : {a}',inline=False)            
                
    else:
        if len(embed) == 11:
            embod = discord.Embed(
                title='oops',
                description='No one with this user ID has applied'
            )
            await ctx.channel.send(embed=embod)
        else:
            await ctx.channel.send(embed=embed)

@user.error
async def user_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title='Error',
            description='U have not specified the id of the user\n```command usage : !search user <id>```'
        )
        await ctx.channel.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title='Error',
            description='An id is made up of numbers try again \n```command usage : !search role <id>```'
        )
        await ctx.channel.send(embed=embed)
    
    else:
        await ctx.channel.send(f'error:\n```{error}```')

@bot.command(aliases=['apps'])
async def applications(ctx):
    data = get_data()
    embed = discord.Embed(
        title = "Applications",
        description = "These are the applications that are avaliable\nTo apply do : !apply <applications name>"
    )
    embed.set_footer(text='Made by !LEUNAMME#6669')
    for x, y in data.items():
        question = len(y['questions'])
        embed.add_field(name=f'{x}', value=f'Questions : {question + 1}',inline=True)
      
    else:
        await ctx.channel.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def accept(ctx,arg,arg2):
    data = get_data()
    userId = int(arg)
    position = arg2.lower()

    if position in data.keys():
        if "applicants" in data[f'{arg2.lower()}']:
            applicants = data[f'{arg2.lower()}']["applicants"]
            for key, value in applicants.items():
                userAppId = value['userid']
                if int(userId) == int(userAppId):
                    embedacept = discord.Embed(title = 'You have been accepted! 🙂' ,description = f'Hello you have been accepted for the following position in dank trades : {position}')
                    db2.child('applications').child(f'{position}').child('applicants').child(f'{key}').update({'status':'accepted'})
                    usersName = bot.get_user(userId)
                    await usersName.send(embed=embedacept)
                    await ctx.channel.send(f"{usersName.name} has been accepted for the position {position}")
                    break

            else:
                embedIdError = discord.Embed(title='Error',description='Could not find a application with the specified user-id\n```command usage : !accept <userid> <position>```')
                await ctx.channel.send(embed=embedIdError)

        else:
            embedapperror = discord.Embed(title='Error',description='Could not find a application with the specified user-id\n```command usage : !accept <userid> <position>```')
            await ctx.channel.send(embed=embedapperror)

    else:
        embedposerror = discord.Embed(title='Error',description='Could not find a postion with that name\n```command usage : !accept <userid> <position>```')
        await ctx.channel.send(embed=embedposerror)

@accept.error
async def accept_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title='Error',
            description='U have not specified the id of the user or the position\n```Command Usage : !accept <userid> <position>```'
        )
        await ctx.channel.send(embed=embed)

    else:
        await ctx.channel.send(f'error:\n```{error}```')

@bot.command()
@commands.has_permissions(administrator=True)
async def reject(ctx,arg):
    data = get_data()
    for x, y in data.items():
        if "applicants" in y:
            applicants = y['applicants']

            if arg in applicants:

                db2.child('applications').child(f'{x}').child('applicants').child(f'{arg}').update({'status':'rejected'})
                rejected = applicants[f'{arg}']['userid']
                uso = bot.get_user(id=rejected)
                await ctx.channel.send(f"{uso.name} has been rejected for the position {x}")
        
@reject.error
async def reject_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title='Error',
            description='U have not specified the id of the application\n```command usage : !reject <id>```'
        )
        await ctx.channel.send(embed=embed)

    else:
        await ctx.channel.send(f'error:\n```{error}```')

@bot.group(invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def delete(ctx):
    embed = discord.Embed(
        title = 'Error',
        description = 'Command usage : ```!delete <application / id> <value>```'
    )
    await ctx.channel.send(embed=embed)

@delete.command(aliases=['app','pos','position'])
@commands.has_permissions(administrator=True)
async def application(ctx,arg):
    data = get_data()
    embed = discord.Embed(
        title = f'Are you sure you want to delete {arg.lower()} this will delete all the applications in that'
    )
    if arg.lower() in data:
        message = await ctx.channel.send(embed=embed)
        await message.add_reaction(u"\U0001F7E2")
        await message.add_reaction(u"\U0001F534")

        try:
            reaction, user = await bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and str(reaction.emoji) in [u"\U0001F534",u"\U0001F7E2"],timeout=400.0)
            
        except asyncio.TimeoutError:
            await ctx.channel.send("You took to long to react")
        
        else:
            if reaction.emoji == u"\U0001F7E2":
                deleteid = db.reference(f"applications/{arg.lower()}")
                deleteid.delete()
                embedred = discord.Embed(
                    title='Done',
                    description=f'The Following application has been delete : {arg.lower()}'
                )
                await ctx.channel.send(embed=embedred)
            
            if reaction.emoji == u"\U0001F534":
                embedgreen = discord.Embed(
                    title='Cancled',
                    description='The action has been cancelled'
                )
                await ctx.channel.send(embed=embedgreen)
    else:
        elseembed = discord.Embed(
            title='Error',
            description='The application you specified could not be found'
        )

        await ctx.channel.send(embed=elseembed)

@application.error
async def application_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title='Error',
            description='U have not specified the name of the application you want to delete\n```command usage : !delete application <name>```'
        )
        await ctx.channel.send(embed=embed)

    else:
        await ctx.channel.send(f'error:\n```{error}```')

@delete.command(aliases=['ids','appid'])
@commands.has_permissions(administrator=True)
async def id(ctx,arg):
    data = get_data()
    green = False
    embed = discord.Embed(
        title = f'Are you sure you want to delete {arg.lower()} this will delete the application forever'
    )
    for x, y in data.items():
        if "applicants" in y: 
            reqdata = y['applicants']
            if arg in reqdata:
                message = await ctx.channel.send(embed=embed)
                await message.add_reaction(u"\U0001F7E2")
                await message.add_reaction(u"\U0001F534")

                try:
                    reaction, user = await bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and str(reaction.emoji) in [u"\U0001F534",u"\U0001F7E2"],timeout=400.0)

                except asyncio.TimeoutError:
                    await ctx.channel.send("You took to long to react")
                
                else:
                    if str(reaction.emoji) == u"\U0001F7E2":
                        green = True
                        embedred = discord.Embed(
                            title='Done',
                            description=f'The Following application has been deleted : {arg}'
                        )
                        await message.edit(embed=embedred)
                    
                    elif str(reaction.emoji) == u"\U0001F534":
                        embedgreen = discord.Embed(
                            title='Cancled',
                            description='The action has been cancelled'
                        )
                        await message.edit(embed=embedgreen)
                    break
    else:
        elseembed = discord.Embed(
            title='Error',
            description='The id you specified could not be found'
        )

        await ctx.channel.send(embed=elseembed)
    
    if green == True :
        deleteid = db.reference(f"applications/{x}/applicants/{arg}")
        deleteid.delete()


@id.error
async def id_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title='Error',
            description='U have not specified the id of the application you want to delete\n```command usage : !delete id <id>```'
        )
        await ctx.channel.send(embed=embed)

    else:
        await ctx.channel.send(f'error:\n```{error}```')

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Help has arived",
        description='These are all the commands the bot offers'
    )
    embed.add_field(name='create', value=f'This command lets you make a new application\nExample: !create <name of he application>',inline=False)
    embed.add_field(name='apply', value=f'This command lets you apply for a position in the server\nExample: !apply <name of positon>',inline=False)
    embed.add_field(name='review', value=f'This command lets you review applications if you dont specify a id it will show all pending applications\nExample : !review <id of app>',inline=False)
    embed.add_field(name='search', value=f'This command lets you search for a application\nExample: !search <position/pos> <name>\nExample: !search user <id>\nExample:!search status <pending/accepted/rejected>\n Example: !search role <id>',inline=False)
    embed.add_field(name='accept', value=f'This command lets you accept a application and will notify the accepted user\nExample: !accept <userid> <position>',inline=False)
    embed.add_field(name='reject', value=f'This command lets you reject a application and will not notify the rejected user\nExample: !reject <app id>',inline=False)
    embed.add_field(name='delete', value=f'This command lets you delete a position or a application id\nExample: !delete <position/id> <name/id>',inline=False)
    embed.add_field(name='add_role', value=f'This command lets you add roles that will be shown when viewing an Application\nExample: !delete',inline=False)
    embed.add_field(name='role', value=f'This command shows you all the roles which will be shown when viewing an Application\nExample: !role',inline=False)
    await ctx.channel.send(embed=embed)

bot.run("Token removed")
