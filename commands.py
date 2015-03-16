import musegames
import setlistfm
import filehandle
import txtfunctions
import timercommands
import setlistgenerator
from random import randint

# Extra step in getting a random phrase to connect with info.state
# Prints I/O Errors, returns a single-element list.
def phrase(irc):
    if irc.info.state:
        try:
            phrase = timercommands.random_phrase()
        except IOError as e:
            print(e)
        irc.msg(phrase)

# Command handling is done here
# Takes the IRCBot as input to send message results.
# Exceptions that are caught are printed, program continues.
def command_run(text, irc):
    
    if text.msgtype == "JOIN" and irc.info.joinmsg and irc.info.state:
        irc.msg("Welcome to the sexy plane %s. "
                "Enter !commands to view the bot functions." % text.nick)

    if text.nick in irc.modlist:
        if text.command in ("!wake\r\n", "!wake"):
            irc.info.state = True
            irc.msg("BellamyBot is online.")

        if text.command in ("!sleep\r\n", "!sleep"):
            irc.info.state = False
            irc.msg("Sleep mode activated")
        
        if text.command == "!joinmsg":
            if text.argument in ("on\r\n", "on"):
                irc.info.joinmsg = True
                print("Join messages ON")
            elif text.argument in ("off\r\n", "off"):
                irc.info.joinmsg = False
                print("Join messages OFF")

        if text.command == "!gamemode":
            if text.argument in ("on\r\n", "!on"):
                irc.info.games = True
                print("Game mode ON")
            elif text.argument in ("off\r\n", "off"):
                irc.info.games = False
                print("Game mode OFF")
                
        if text.command == "!setgig":
            try:
                filehandle.clear_file('text/gig')
                filehandle.list_append('text/gig', text.argument)
            except IOError as e:
                print(e)

        # Setlist controls
        if text.command == "!add":
            txtfunctions.add_song(text.argument)

        if text.command in ("!clearset\r\n", "!clearset"):
            try:
                filehandle.clear_file('text/setlist')
            except IOError as e:
                print(e)
            irc.msg("Current setlist has been cleared.")

        if text.command in ("!undo\r\n", "!undo"):
            try:
                txtfunctions.song_undo()
            except IOError as e:
                print(e)
            except IndexError as i:
                print(i)
            irc.msg("The last song has been erased")

        if text.command == "!insert":
            try:
                response = txtfunctions.insert_song(text.argument)
            except IOError as e:
                print(e)
            irc.msg(response)

        if text.command == "!replace":
            try:
                response = txtfunctions.replace_song(text.argument)
            except IOError as e:
                print(e)
            irc.msg(response)

        if text.command == "!delete":
            try:
                response = txtfunctions.delete_song(text.argument)
            except IOError as e:
                print(e)
            irc.msg(response)
        
        if text.command in ("!setprevious\r\n", "!setprevious"):
            try:
                response = txtfunctions.set_previous()
            except IOError as e:
                print(e)
            except RuntimeError as r:
                print(r)
            irc.msg(response)
            
    # All user commands
    if text.command in ("!bot\r\n", "!bot"):
        statePhrase = ("BellamyBot version %s created by Kueller917. Status: "
                       % irc.info.version)
        if irc.info.state:
            statePhrase = statePhrase + "ONLINE"
        else:
            statePhrase = statePhrase + "OFFLINE"

        irc.msg(statePhrase)

    if text.command in ("!gig\r\n", "!gig"):
        try:
            gig = filehandle.get_list('text/gig')
        except IOError as e:
            print(e)
        irc.msg(gig[0])

    if text.command == "!message":
        try:
            filehandle.list_append('text/ircmsg', "%s: %s" % (text.nick,
                                        filehandle.remove_nr(text.argument)))
        except IOError as e:
            print(e)
        if len(irc.owners) > 0:
            irc.memo(irc.owners[0], "You have a message from %s" % text.nick)

    if text.command in ("!source\r\n", "!source"):
        sourceMsg = ("Get your own copy of BellamyBot today! %s" % irc.info.sourceCode)
        irc.msg(sourceMsg)

    # State dependent commands
    if irc.info.state:
        
        # General commands
        if text.command in ("!setlist\r\n", "!setlist"):
            setmsg = "CURRENT SETLIST: "
            try:
                currentset = txtfunctions.print_set('text/setlist')
            except IOError as e:
                print(e)
            
            if currentset == '':
                currentset = "...is empty"
            setmsg = setmsg + currentset
            irc.msg(setmsg)

        if text.command in ("!previous\r\n", "!previous"):
            try:
                previous = txtfunctions.print_set('text/previous')
            except IOError as e:
                print(e)
            irc.msg(previous)

        if text.command in ("!commands\r\n", "!commands"):
            irc.msg("Use !gig, !setlist, and !previous for information "
                    "on tonight's concert and prior. Try !setfm, "
                    "!closer, !opener, !manson, !roulette, !setgen, "
                    "!ru-roulette, and !realfan for fun.")

        if irc.info.games:
            # Games
            if text.command in ("!closer\r\n", "!closer"):
                try:
                    closer = musegames.random_game('text/gigcloser')
                except IOError as e:
                    print(e)
                irc.msg("%s\'s game has closed with %s!" % (text.nick, closer))

            if text.command in ("!opener\r\n", "!opener"):
                try:
                    opener = musegames.random_game('text/opener')
                except IOError as e:
                    print(e)
                irc.msg("%s\'s game has opened with %s!" % (text.nick, opener))

            if text.command in ("!realfan\r\n", "!realfan"):
                fan = randint(0,1)
                if fan:
                    irc.msg("%s is a REAL FAN. Good for you." % text.nick)
                else:
                    irc.msg("%s is not a REAL FAN. Go away." % text.nick)

            if text.command in ("!roulette\r\n", "!roulette"):
                output = musegames.T2L_roulette()
                if output != -1:
                    irc.msg(output)
                else:
                    irc.info.green = True
                    irc.info.greenNick = text.nick
                    irc.msg("You landed on GREEN! Type !green to get your song")

            if text.command in ("!green\r\n", "!green"):
                if irc.info.green:
                    if text.nick == irc.info.greenNick:
                        irc.info.green = False
                        irc.info.greenNick = None
                        irc.msg(musegames.roulette_green(text.nick))
                    else:
                        irc.msg("You did not land on green.")

            if text.command in ("!setfm\r\n", "!setfm"):
                setlist = setlistfm.get_setlist(irc.info.mbid)
                for messagePart in setlist:
                    irc.msg(messagePart)

            if text.command in ("!manson\r\n", "!manson"):
                try:
                    mansons = musegames.manson_game(text.nick)
                except IOError as e:
                    print(e)
                except IndexError as i:
                    print(i)
                irc.msg(mansons)

            if text.command in ("!ru-roulette\r\n", "!ru-roulette"):
                timercommands.russian_roulette(irc, text.nick)

            if text.command in ("!setgen\r\n", "!setgen"):
                setlistgenerator.generate(irc)
