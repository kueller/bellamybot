import musegames
import filehandle
import txtfunctions
import timercommands
import setlistgenerator
from bellamylib import BotInfo
from random import randint

# Bot information is stored here
bot = BotInfo()

# Extra step in getting a random phrase to connect with bot.state
# Raises exception if file could not be opened
def phrase():
    if bot.state:
        try:
            phrase = timercommands.random_phrase()
        except IOError as e:
            raise IOError(e)
        return phrase

# Command handling is done here
# String response is returned for valid commands
# "None" is returned if input did not match any commands (general text)
# Exceptions that are caught are re-raised and passed on
def command_run(text):
    if text.msgtype == "JOIN" and bot.joinmsg and bot.state:
        return ("Welcome to the sexy plane %s. "
                "Enter !commands to view the bot functions." % text.nick)

    if text.nick in bot.ops:
        if text.command in ("!wake\r\n", "!wake"):
            bot.state = True
            return "BellamyBot is online."

        if text.command in ("!sleep\r\n", "!sleep"):
            bot.state = False
            return "Sleep mode activated"
        
        if text.command == "!joinmsg":
            if text.argument in ("on\r\n", "!on"):
                bot.joinmsg = True
                print("Join messages ON")
            elif text.argument in ("off\r\n", "!on"):
                bot.joinmsg = False
                print("Join messages OFF")

        if text.command == "!setgig":
            try:
                filehandle.clear_file('text/gig')
                filehandle.list_append('text/gig', text.argument)
            except IOError as e:
                print(e);

        # Setlist controls
        if text.command == "!add":
            txtfunctions.add_song(text.argument)

        if text.command in ("!clearset\r\n", "!clearset"):
            try:
                filehandle.clear_file('text/setlist')
            except IOError as e:
                raise IOError(e)
            return "Current setlist has been cleared."

        if text.command in ("!undo\r\n", "!undo"):
            try:
                txtfunctions.song_undo()
            except IOError as e:
                raise IOError(e)
            except IndexError as i:
                raise IndexError(i)
            return "The last song has been erased"

        if text.command == "!insert":
            try:
                response = txtfunctions.insert_song(text.argument)
            except IOError as e:
                raise IOError(e)
            return response

        if text.command == "!replace":
            try:
                response = txtfunctions.replace_song(text.argument)
            except IOError as e:
                raise IOError(e)
            return response

        if text.command == "!delete":
            try:
                response = txtfunctions.delete_song(text.argument)
            except IOError as e:
                raise IOError(e)
            return response
        
        if text.command in ("!setprevious\r\n", "!setprevious"):
            try:
                response = txtfunctions.set_previous()
            except IOError as e:
                raise IOError(e)
            except RuntimeError as r:
                raise RuntimeError(r)
            return response

    # All user commands
    if text.command in ("!bot\r\n", "!bot"):
        statePhrase = ("BellamyBot version 3.2.0 created by Kueller917. "
                    "Status: ")
        if bot.state:
            statePhrase = statePhrase + "ONLINE"
        else:
            statePhrase = statePhrase + "OFFLINE"

        return statePhrase

    if text.command in ("!gig\r\n", "!gig"):
        try:
            gig = filehandle.get_list('text/gig')
        except IOError as e:
            raise IOError(e)
        return gig[0]

    if text.command in ("!source\r\n", "!source"):
        srcmsg = "Get your own copy of BellamyBot today! %s" % bot.sourceCode
        return srcmsg

    # State dependent commands
    if bot.state:
        
        # General commands
        if text.command in ("!setlist\r\n", "!setlist"):
            setmsg = "CURRENT SETLIST: "
            try:
                currentset = txtfunctions.print_set('text/setlist')
            except IOError as e:
                raise IOError(e)
            
            if currentset == '':
                currentset = "...is empty"
            setmsg = setmsg + currentset
            return setmsg

        if text.command in ("!previous\r\n", "!previous"):
            try:
                previous = txtfunctions.print_set('text/previous')
            except IOError as e:
                raise IOError(e)
            return previous

        if text.command in ("!commands\r\n", "!commands"):
            return ("Use !gig, !setlist, and !previous for information "
                    "on tonight's concert and prior Try !rotation, !closer, "
                    "!opener, !manson, !roulette, !setgen, !ru-roulette, "
                    "and !realfan for fun.")

        # Games
        if text.command in ("!closer\r\n", "!closer"):
            try:
                closer = musegames.random_game('text/gigcloser')
            except IOError as e:
                raise IOError(e)
            return ("%s\'s game has closed with %s!" % (text.nick, closer))

        if text.command in ("!opener\r\n", "!opener"):
            try:
                opener = musegames.random_game('text/opener')
            except IOError as e:
                raise IOError(e)
            return ("%s\'s game has opened with %s!" % (text.nick, opener))

        if text.command in ("!realfan\r\n", "!realfan"):
            fan = randint(0,1)
            if fan:
                return ("%s is a REAL FAN. Good for you." % text.nick)
            else:
                return ("%s is not a REAL FAN. Go away." % text.nick)

        if text.command in ("!roulette\r\n", "!roulette"):
            output = musegames.T2L_roulette()
            if output != -1:
                return output
            else:
                bot.green = True
                bot.greenNick = text.nick
                return "You landed on GREEN! Type !green to get your song"

        if text.command in ("!green\r\n", "!green"):
            if bot.green:
                if text.nick == bot.greenNick:
                    bot.green = False
                    bot.greenNick = None
                    return musegames.roulette_green(text.nick)
                else:
                    return "You did not land on green."

        if text.command in ("!manson\r\n", "!manson"):
            try:
                mansons = musegames.manson_game(text.nick)
            except IOError as e:
                raise IOError(e)
            except IndexError as i:
                raise IndexError(i)
            return mansons

    return None
