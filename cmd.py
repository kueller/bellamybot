import filehandle

def dump_commands_to_file(commands, filename):
    filelist = []
    for element in commands:
        cmd = "[command]\nname=%s\nbody=%s\n" % (element, commands[element])
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
        for entry in entries:
            if entry.startswith('#'):
                continue
            args = entry.partition('=')
            if len(args) == 3:
                if args[0].strip() == 'name' and args[2].strip() not in commands:
                    ckey = args[2].strip()
                elif args[0].strip() == 'body':
                    cbody = args[2].strip()
        if ckey is not None and cbody is not None:
            commands[ckey] = cbody
    return commands

def function(commands, irc, argument):
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
                commands[cname] = cbody
                irc.msg("\"%s\" has been added to the command list." % cname)
        elif op == 'edit':
            if cname in commands:
                commands[cname] = cbody
                irc.msg("\"%s\" has been updated." % cname)
        elif op == '+=':
            if cname in commands:
                commands[cname] += ' ' + cbody
                irc.msg("\"%s\" has been updated." % cname)
        elif op == 'rename':
            if cname in commands:
                newkey = cbody.split(' ')[0].lower()
                if newkey.startswith('!') and newkey not in commands:
                    commands[newkey] = commands[cname]
                    del commands[cname]
                    irc.msg("\"%s\" has been renamed to \"%s\"." % (cname, newkey))
    else:
        if op == 'delete':
            if cname in commands:
                del commands[cname]
                irc.msg("\"%s\" has been removed from the command list." % cname)