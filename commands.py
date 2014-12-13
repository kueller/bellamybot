import musegames
import setlistfm
import filehandle
import txtfunctions
import timercommands
import setlistgenerator
from random import randint

# Extra step in getting a random phrase to connect with info.state
# Prints I/O Errors, returns a single-element list.
def phrase(info):
    if info.state:
        try:
            phrase = timercommands.random_phrase()
        except IOError as e:
            raise IOError(e)
        return phrase

# Command handling is done here
# Return value is a list of responses.
# List can be empty, for no responses.
# Exceptions that are caught are printed, program continues.
def command_run(text, info):
    message = []
    
    if text.msgtype == "JOIN" and info.joinmsg and info.state:
        message.append("Welcome to the sexy plane %s. "
                "Enter !commands to view the bot functions." % text.nick)

    if text.nick in info.ops:
        if text.command in ("!wake\r\n", "!wake"):
            info.state = True
            message.append("BellamyBot is online.")

        if text.command in ("!sleep\r\n", "!sleep"):
            info.state = False
            message.append("Sleep mode activated")
        
        if text.command == "!joinmsg":
            if text.argument in ("on\r\n", "!on"):
                info.joinmsg = True
                print("Join messages ON")
            elif text.argument in ("off\r\n", "!on"):
                info.joinmsg = False
                print("Join messages OFF")

        if text.command == "!setgig":
            try:
                filehandle.clear_file('text/gig')
                filehandle.list_append('text/gig', text.argument)
            except IOError as e:
                print(e)
                return message

        # Setlist controls
        if text.command == "!add":
            txtfunctions.add_song(text.argument)

        if text.command in ("!clearset\r\n", "!clearset"):
            try:
                filehandle.clear_file('text/setlist')
            except IOError as e:
                print(e)
                return message
            message.append("Current setlist has been cleared.")

        if text.command in ("!undo\r\n", "!undo"):
            try:
                txtfunctions.song_undo()
            except IOError as e:
                print(e)
                return message
            except IndexError as i:
                print(i)
                return message
            message.append("The last song has been erased")

        if text.command == "!insert":
            try:
                response = txtfunctions.insert_song(text.argument)
            except IOError as e:
                print(e)
            message.append(response)

        if text.command == "!replace":
            try:
                response = txtfunctions.replace_song(text.argument)
            except IOError as e:
                print(e)
                return message
            message.append(response)

        if text.command == "!delete":
            try:
                response = txtfunctions.delete_song(text.argument)
            except IOError as e:
                print(e)
                return message
            message.append(response)
        
        if text.command in ("!setprevious\r\n", "!setprevious"):
            try:
                response = txtfunctions.set_previous()
            except IOError as e:
                print(e)
                return message
            except RuntimeError as r:
                print(r)
                return message
            message.append(response)

    # All user commands
    if text.command in ("!bot\r\n", "!bot"):
        statePhrase = ("BellamyBot version 3.2.0 created by Kueller917. Status: ")
        if info.state:
            statePhrase = statePhrase + "ONLINE"
        else:
            statePhrase = statePhrase + "OFFLINE"

        message.append(statePhrase)

    if text.command in ("!gig\r\n", "!gig"):
        try:
            gig = filehandle.get_list('text/gig')
        except IOError as e:
            print(e)
            return message
        message.append(gig[0])

    if text.command in ("!source\r\n", "!source"):
        sourceMsg = ("Get your own copy of BellamyBot today! %s" % info.sourceCode)
        message.append(sourceMsg)

    # State dependent commands
    if info.state:
        
        # General commands
        if text.command in ("!setlist\r\n", "!setlist"):
            setmsg = "CURRENT SETLIST: "
            try:
                currentset = txtfunctions.print_set('text/setlist')
            except IOError as e:
                print(e)
                return message
            
            if currentset == '':
                currentset = "...is empty"
            setmsg = setmsg + currentset
            message.append(setmsg)

        if text.command in ("!previous\r\n", "!previous"):
            try:
                previous = txtfunctions.print_set('text/previous')
            except IOError as e:
                print(e)
                return message
            message.append(previous)

        if text.command in ("!commands\r\n", "!commands"):
            message.append("Use !gig, !setlist, and !previous for information "
                    "on tonight's concert and prior. Try !setfm, !rotation, "
                    "!closer, !opener, !manson, !roulette, !setgen, "
                    "!ru-roulette, and !realfan for fun.")

        # Games
        if text.command in ("!closer\r\n", "!closer"):
            try:
                closer = musegames.random_game('text/gigcloser')
            except IOError as e:
                print(e)
                return message
            message.append("%s\'s game has closed with %s!" % (text.nick, closer))

        if text.command in ("!opener\r\n", "!opener"):
            try:
                opener = musegames.random_game('text/opener')
            except IOError as e:
                print(e)
                return message
            message.append("%s\'s game has opened with %s!" % (text.nick, opener))

        if text.command in ("!realfan\r\n", "!realfan"):
            fan = randint(0,1)
            if fan:
                message.append("%s is a REAL FAN. Good for you." % text.nick)
            else:
                message.append("%s is not a REAL FAN. Go away." % text.nick)

        if text.command in ("!roulette\r\n", "!roulette"):
            output = musegames.T2L_roulette()
            if output != -1:
                message.append(output)
            else:
                info.green = True
                info.greenNick = text.nick
                message.append("You landed on GREEN! Type !green to get your song")

        if text.command in ("!green\r\n", "!green"):
            if info.green:
                if text.nick == info.greenNick:
                    info.green = False
                    info.greenNick = None
                    message.append(musegames.roulette_green(text.nick))
                else:
                    message.append("You did not land on green.")

        if text.command in ("!setfm\r\n", "!setfm"):
            setlist = setlistfm.get_setlist(info.mbid)
            for messagePart in setlist:
                message.append(messagePart)

        if text.command in ("!manson\r\n", "!manson"):
            try:
                mansons = musegames.manson_game(text.nick)
            except IOError as e:
                print(e)
                return message
            except IndexError as i:
                print(i)
                return message
            message.append(mansons)

        if text.command in ("!setgen\r\n", "!setgen"):
            setlist = setlistgenerator.generate()
            if setlist != None:
                message.append(setlist['setlist'])
                message.append(setlist['encore1'])
                if setlist['encore2'] != None:
                    message.append(setlist['encore2'])

    return message
