import boteval
import filehandle

# The format of a command in the command file is:
#
# [command]
# name = !command
# body = This is the text the command will run.
#
# The value $nick in the body will be replaced at runtime with the
# nick of the user who called the command.
# By convention, commands should start with a '!', or some other
# special character to keep it specific.

def dump_commands_to_file(commands, filename):
    filelist = []
    for element in commands:
        cmd = ('[command]\nname=%s\nchannel=%s\nbody=%s\n'
               % (element, ','.join(commands[element]['chan']),
                  commands[element]['body']))
        filelist.append(cmd)
    try:
        filehandle.put_list(filename, filelist)
    except IOError:
        print('Error writing commands file.')

def create_commands_from_file(filename):
    commands = {}

    try:
        with open(filename, 'r') as f:
            text = f.read()
    except IOError:
        return commands
    except FileNotFoundError:
        with open(filename, 'w') as f:
            None
        return commands

    print("Loading commands from file.")
    cmdlist = text.split('[command]')
    for cmd in cmdlist:
        entries = cmd.split('\n')
        ckey  = None
        cbody = None
        cchan = None
        for entry in entries:
            if entry.startswith('#'):
                continue
            args = entry.partition('=')
            if len(args) == 3:
                if args[0].strip() == 'name' and args[2].strip() not in commands:
                    ckey = args[2].strip()
                elif args[0].strip() == 'body':
                    cbody = args[2].strip()
                elif args[0].strip() == 'channel':
                    cchan = []
                    for chan in args[2].split(','):
                        cchan.append(chan.strip())
        if ckey is not None and cbody is not None and cchan is not None:
            commands[ckey] = {}
            commands[ckey]['chan'] = cchan
            commands[ckey]['body'] = cbody
    return commands

def function(irc, commands, argument):
    tokens = argument.split()
    if len(tokens) < 2:
        return
    
    op    = tokens[0]
    cname = tokens[1].lower()

    if not cname.startswith('!'):
        return
    
    if len(tokens) >= 3:
        cbody = ' '.join(tokens[2:]).strip()

        if op == 'add':
            if not cname in commands:
                commands[cname] = {}
                commands[cname]['chan'] = []
                commands[cname]['chan'].append(irc.channel())
                commands[cname]['body'] = cbody
                irc.msg("\"%s\" has been added to the command list." % cname)
        elif op == 'edit':
            if cname in commands:
                commands[cname]['body'] = cbody
                irc.msg("\"%s\" has been updated." % cname)
        elif op == '+=':
            if cname in commands:
                commands[cname]['body'] += ' ' + cbody
                irc.msg("\"%s\" has been updated." % cname)
        elif op == 'rename':
            if cname in commands:
                newkey = cbody.split(' ')[0].lower()
                if newkey.startswith('!') and newkey not in commands:
                    commands[newkey] = commands[cname]
                    del commands[cname]
                    irc.msg("\"%s\" has been renamed to \"%s\"." % (cname, newkey))
        elif op == 'addchan':
            if cname in commands:
                for chan in cbody.split(','):
                    if chan not in commands[cname]['chan']:
                        commands[cname]['chan'].append(chan.strip())
    else:
        if op == 'delete':
            if cname in commands:
                del commands[cname]
                irc.msg("\"%s\" has been removed from the command list." % cname)

def execute(irc, text):
    cmd = text.command.strip()
    if not cmd in commands:
        return
    if not irc.channel() in commands[cmd]['chan']:
        return
    if len(commands[cmd]['body']) == 0:
        return

    body = commands[cmd]['body']
    body = body.replace('$chan', irc.channel()).replace('$nick', text.nick)
    print(body)

    args = text.argument.strip().split()
    arg_count = []
    for token in body.replace('$', ' $').split():
        if token.startswith('$') and len(token) >= 2:
            try:
                value = int(token[1:])
                if value not in arg_count:
                    print(value)
                    arg_count.append(value)
            except ValueError:
                None

    for param in arg_count:
        try:
            body = body.replace('$%d' % param, args[param - 1])
        except IndexError:
            irc.msg("Need a parameter %d for command %s." % (param, cmd))
            return

    if body.split()[0] == '!eval':
        ev = boteval.BotEval()
        ev.eval(irc, body.partition(' ')[2])
    else:
        irc.msg(body)
