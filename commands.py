import cmd
import musegames
import setlistfm
import filehandle
import gigarchive
import txtfunctions
import timercommands
import setlistgenerator
from random import randint

# Extra step in getting a random phrase to connect with info.state
# Prints I/O Errors, returns a single-element list.
def phrase(irc):
    if irc.isAwake():
        try:
            phrase = timercommands.random_phrase()
        except IOError as e:
            print(e)
        irc.msg(phrase)

# Command handling is done here
# Takes the IRCBot as input to send message results.
# Exceptions that are caught are printed, program continues.
def command_run(text, irc, commands):
    
    if text.IRCcmd == "JOIN" and irc.joinmsg() and irc.isAwake():
        if text.nick != irc.nick():
            irc.msg("Welcome to the sexy plane %s. "
                    "Enter !commands to view the bot functions." % text.nick)

    if text.nick in irc.modlist:
        if text.command in ("!wake\r\n", "!wake"):
            irc.wake()
            irc.msg("BellamyBot is online.")

        elif text.command in ("!sleep\r\n", "!sleep"):
            irc.sleep()
            irc.msg("Sleep mode activated")
        
        elif text.command == "!joinmsg":
            if text.argument in ("on\r\n", "on"):
                irc.activateJoinMsg()
                print("Join messages ON")
            elif text.argument in ("off\r\n", "off"):
                irc.deactivateJoinMsg()
                print("Join messages OFF")

        elif text.command == "!gamemode":
            if text.argument in ("on\r\n", "on"):
                irc.activateGames()
                print("Game mode ON")
            elif text.argument in ("off\r\n", "off"):
                irc.deactivateGames()
                print("Game mode OFF")
                
        elif text.command == "!setgig":
            try:
                filehandle.clear_file('text/gig')
                filehandle.list_append('text/gig', text.argument)
            except IOError as e:
                print(e)

        elif text.command == "!settour":
            try:
                filehandle.clear_file('text/tour')
                filehandle.list_append('text/tour', text.argument)
            except IOError as e:
                print(e)

        # Setlist controls
        elif text.command == "!add":
            txtfunctions.add_song(text.argument)

        elif text.command == "!exp":
            original = filehandle.remove_nr(text.argument)
            check    = txtfunctions.acronym_replace(text.argument)
            if check == original:
                irc.msg("There is no expansion for " + original)
            else:
                irc.msg(original + " expands to " + check)
            
        elif text.command in ("!clearset\r\n", "!clearset"):
            try:
                filehandle.clear_file('text/setlist')
            except IOError as e:
                print(e)
            irc.msg("Current setlist has been cleared.")

        elif text.command in ("!undo\r\n", "!undo"):
            try:
                txtfunctions.song_undo()
            except IOError as e:
                print(e)
            except IndexError as i:
                print(i)
            irc.msg("The last song has been erased")

        elif text.command == "!insert":
            try:
                response = txtfunctions.insert_song(text.argument)
            except IOError as e:
                print(e)
            irc.msg(response)

        elif text.command == "!replace":
            try:
                response = txtfunctions.replace_song(text.argument)
            except IOError as e:
                print(e)
            irc.msg(response)

        elif text.command == "!delete":
            try:
                response = txtfunctions.delete_song(text.argument)
            except IOError as e:
                print(e)
            irc.msg(response)
        
        elif text.command in ("!setprevious\r\n", "!setprevious"):
            try:
                response = txtfunctions.set_previous()
            except IOError as e:
                print(e)
            except RuntimeError as r:
                print(r)
            irc.msg(response)

        elif text.command == "!cmd":
            cmd.function(commands, irc, text.argument)
            
    # All user commands
    if text.command in ("!bot\r\n", "!bot"):
        statePhrase = ("BellamyBot version %s created by Kueller917. Status: "
                       % irc.version())
        if irc.isAwake():
            statePhrase = statePhrase + "ONLINE"
        else:
            statePhrase = statePhrase + "OFFLINE"

        irc.msg(statePhrase)

    elif text.command in ("!gig\r\n", "!gig"):
        try:
            gig = filehandle.get_list('text/gig')
        except IOError as e:
            print(e)
        irc.msg(gig[0])

    elif text.command in ("!previous\r\n", "!previous"):
        gigarchive.print_recent_setlist(irc)

    elif text.command == "!message":
        try:
            filehandle.list_append('text/ircmsg', "%s: %s" % (text.nick,
                                        filehandle.remove_nr(text.argument)))
        except IOError as e:
            print(e)
        if len(irc.owners) > 0:
            irc.memo(irc.owners[0], "You have a message from %s" % text.nick)

    elif text.command in ("!source\r\n", "!source"):
        sourceMsg = ("Get your own copy of BellamyBot today! %s" % irc.source())
        irc.msg(sourceMsg)

    # State dependent commands
    if irc.isAwake():
        
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

        elif text.command == "!count":
            song = txtfunctions.acronym_replace(text.argument)
            count = gigarchive.song_count(song)
            irc.msg("%s has been played %d times." % (song, count))

        elif text.command == "!lastplayed":
            song = txtfunctions.acronym_replace(text.argument)
            gigarchive.last_played(irc, song)

        elif text.command == "!findset":
            gigarchive.find_setlist(irc, text.argument.strip())

        elif text.command == "!loadset":
            date = text.argument.strip()
            setlist = gigarchive.print_set_by_date(irc, date)

        elif text.command == "!info":
            try:
                infolist = filehandle.get_list('text/info')
            except IOError:
                print('Error opening file info')
                return

            command = text.argument.strip()
            for line in infolist:
                if line.split(':')[0] == command:
                    irc.msg(line.split(':')[1])

        elif text.command in ("!commands\r\n", "!commands"):
            irc.msg("Set commands: !gig, !setlist, !previous, !findset, "
                    "!loadset, !count, !lastplayed.")
            irc.msg("Other: !bot, !source, !closer, !opener, !realfan, "
                    "!roulette, !setfm, !ru-roulette, !setgen. Use !info "
                    "for a description of any command.")

        elif text.command.strip() in commands:
            irc.msg(commands[text.command.strip()].replace('$nick', text.nick))
            
        if irc.gamesActive():
            # Games
            if text.command in ("!closer\r\n", "!closer"):
                try:
                    closer = musegames.random_game('text/gigcloser')
                except IOError as e:
                    print(e)
                irc.msg("%s\'s game has closed with %s!" % (text.nick, closer))

            elif text.command in ("!opener\r\n", "!opener"):
                try:
                    opener = musegames.random_game('text/opener')
                except IOError as e:
                    print(e)
                irc.msg("%s\'s game has opened with %s!" % (text.nick, opener))

            elif text.command in ("!realfan\r\n", "!realfan"):
                if randint(0,1):
                    irc.msg("%s is a REAL FAN. Good for you." % text.nick)
                else:
                    irc.msg("%s is not a REAL FAN. Go away." % text.nick)

            elif text.command in ("!roulette\r\n", "!roulette"):
                output = musegames.T2L_roulette()
                if output != -1:
                    irc.msg(output)
                else:
                    irc.greenOn()
                    irc.greenNick(text.nick)
                    irc.msg("You landed on GREEN! Type !green to get your song")

            elif text.command in ("!green\r\n", "!green"):
                if irc.greenActive():
                    if irc.checkGreen(text.nick):
                        irc.greenOff()
                        irc.greenNick(None)
                        irc.msg(musegames.roulette_green(text.nick))
                    else:
                        irc.msg("You did not land on green.")

            elif text.command in ("!setfm\r\n", "!setfm"):
                setlist = setlistfm.get_setlist(irc.mbid())
                for messagePart in setlist:
                    irc.msg(messagePart)

            elif text.command in ("!manson\r\n", "!manson"):
                try:
                    mansons = musegames.manson_game(text.nick)
                except IOError as e:
                    print(e)
                except IndexError as i:
                    print(i)
                irc.msg(mansons)

            elif text.command in ("!ru-roulette\r\n", "!ru-roulette"):
                timercommands.russian_roulette(irc, text.nick)

            elif text.command in ("!setgen\r\n", "!setgen"):
                setlistgenerator.generate(irc)
