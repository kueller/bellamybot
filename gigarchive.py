import os
import shlex
import filehandle
import txtfunctions

# Statistics and searching for the gig archives.
#
# There is a max 100 line database in text/archive.db that will act as
# a cache to hopefully reduce some searching time.
# In most functions the database is checked first before running through
# the file system.
#
# Queries are case insensitive.

# Helper functions
def year_value(date):
    return int(date.split('-')[0])

def gig_date(filename):
    return filename.split()[0].strip()

def country_code(filename):
    return filename.split()[len(filename.split()) - 1].strip()

def tour_name(foldername):
    return foldername.partition(' ')[2]

def tour_in_range(tour, year):
    gigs = sorted(os.listdir('GigArchive/%s' % tour))
    start_year = year_value(gig_date(gigs[0]))
    end_year   = year_value(gig_date(gigs[len(gigs) - 1]))

    return year >= start_year and year <= end_year    

# Creates an integer of YYYYMMDD format. -1 on errors.
def convert_date_value(date):
    date = date.replace('/', '-')
    if len(date.split('-')) != 3:
        return -1

    try:
        year = year_value(date) * 10000
        month  = int(date.split('-')[1]) * 100
        day = int(date.split('-')[2])
    except ValueError:
        return -1

    return year + month + day

def date_in_range(filename, date_range):
    if date_range == None:
        return True
    if date_range == [-1,-1]:
        return True
    
    current_date = convert_date_value(gig_date(filename))
    lower_date = date_range[0] == -1 or current_date > date_range[0]
    upper_date = date_range[1] == -1 or current_date < date_range[1]

    return lower_date and upper_date

# Parsing of options --range, --country, and --tour
# -1 in range will set the lower or upper range to +/- infinity respectively.
def get_long_opts(args):
    opts = {'range': None, 'country': None, 'tour': None, 'other': []}

    for arg in shlex.split(args):
        if arg.startswith('--'):
            tokens = arg.replace('--','').split('=')
            if len(tokens) == 2:
                opt = tokens[0]
                value = tokens[1]

                if opt == 'range' and len(value.split(':')) == 2:
                    date_range = []
                    date_range.append(convert_date_value(value.split(':')[0]))
                    date_range.append(convert_date_value(value.split(':')[1]))
                    opts['range'] = date_range
                elif opt == 'country':
                    opts['country'] = value.strip()
                elif opt == 'tour':
                    opts['tour'] = value.strip()
        else:
            opts['other'].append(arg)
    return opts                    

# Number of times a song has been played. Does not count the current setlist.
def song_count(irc, args):
    total_search = True

    opts = get_long_opts(args)
    if ((opts['range'] != None and opts['range'] != [-1,-1]) or
        opts['country'] != None or
        opts['tour'] != None):
        total_search = False

    song = txtfunctions.acronym_replace(' '.join(opts['other']))

    database = filehandle.get_list('text/archive.db')
    if total_search:
        for entry in database:
            if entry.startswith('c!'):
                db_song = entry.split('!')[1].split('=')[0]
                if db_song == song.lower():
                    count = int(entry.split('!')[1].split('=')[1])
                    irc.msg("%s has been played %d times." % (song, count))
                    return
            
    count = 0
        
    tours = os.listdir('GigArchive')
    for tour in tours:
        if opts['tour'] == tour_name(tour):
            tours = [tour]
            break
        
    for tour in tours:
        gigs = os.listdir('GigArchive/%s' % tour)
        for filename in gigs:
            if not total_search:
                if (not date_in_range(filename, opts['range']) or
                    (opts['country'] is not None and
                     opts['country'] != country_code(filename))):
                    continue
            setlist = filehandle.get_list('GigArchive/%s/%s' % (tour, filename))
            if song.lower() in [s.lower() for s in setlist]:
                count = count + 1

    if total_search:
        if len(database) >= 100:
            database.pop(0)
        database.append('c!%s=%d' % (song.lower(), count))
        filehandle.put_list('text/archive.db', database)
    irc.msg("%s has been played %d times." % (song, count))

# Finds the most recent performance of a song. Does count the current setlist.
def last_played(irc, args):
    total_search = True
    opts = get_long_opts(args)
    song = txtfunctions.acronym_replace(' '.join(opts['other']))

    if ((opts['range'] != None and opts['range'] != [-1,-1]) or
        opts['country'] != None or
        opts['tour'] != None):
        total_search = False
    
    if song.lower() in [s.lower() for s in filehandle.get_list('text/setlist')]:
        gig = filehandle.get_list('text/gig')
        if date_in_range(gig, opts['range']):
            irc.msg ('%s was last played at: %s' % (song, gig[0]))
            return

    if total_search:
        database = filehandle.get_list('text/archive.db')
        for entry in database:
            if entry.startswith('lp!'):
                db_song = entry.split('!')[1].split('::')[0]
                if song.lower() == db_song:
                    db_file = entry.split('!')[1].split('::')[1]
                    setlist = filehandle.get_list(db_file)
                    irc.msg('%s was last played at: %s' % (song, setlist[0]))
                    return
            
    tours = sorted(os.listdir('GigArchive'))
    for tour in reversed(tours):
        if opts['tour'] is not None:
            if opts['tour'] != tour_name(tour):
                continue
            
        gigs = sorted(os.listdir('GigArchive/%s' % tour))
        for filename in reversed(gigs):
            if (not date_in_range(filename, opts['range']) or
                (opts['country'] is not None and
                 opts['country'] != country_code(filename))):
                continue
            gig_file = 'GigArchive/%s/%s' % (tour, filename)
            setlist = filehandle.get_list(gig_file)
            if song.lower() in [s.lower() for s in setlist]:
                irc.msg('%s was last played at: %s' % (song, setlist[0]))
                if total_search:
                    if len(database) >= 100:
                        database.pop(0)
                        database.append('lp!%s::%s' % (song.lower(), gig_file))
                        filehandle.put_list('text/archive.db', database)
                return
    irc.msg('I do not seem to have information on that song for the given options.')

# Searches the file names of setlists to match a query.
# Results are greatly limited due to IRC message character limits.
# Results are ordered to relevancy.
# This does not access the database file.
def find_setlist(irc, args):
    strict = False
    if '--strict' in shlex.split(args):
        strict = True

    opts = get_long_opts(args)
    queries = [q.lower() for q in opts['other']]
    found = {}

    tours = os.listdir('GigArchive')
    for tour in tours:
        if opts['tour'] == tour_name(tour):
            tours = [tour]
            break
        
    for tour in tours:
        gigs = os.listdir('GigArchive/%s' % tour)
        for filename in gigs:
            if (not date_in_range(filename, opts['range']) or
                (opts['country'] is not None and
                 opts['country'] != country_code(filename))):
                continue

            setlist = filehandle.get_list('GigArchive/%s/%s' % (tour, filename))
            set_lower = [s.lower() for s in setlist]
            
            ckey = filename.split()[0]
            found[ckey] = 0
            for q in queries:
                if filename.lower().find(q) != -1:
                    found[ckey] += 1
                if q in set_lower:
                    found[ckey] += 1
            if found[ckey] == 0:
                del found[ckey]
            elif found[ckey] != len(queries) and strict:
                del found[ckey]

    if len(found) == 0:
        irc.msg("No gigs found for given query.")
    else:
        sorted_found = sorted(found, key=found.get, reverse=True)
        output = "\"%s\"" % sorted_found[0]
        for gig in sorted_found[1:]:
            if len(output) + len(gig) + 2 > 400:
                break
            output = "%s, \"%s\"" % (output, gig)
        irc.msg("Possible setlists: %s" % output)

# Takes a date in the form YYY/MM/DD and prints the corresponding setlist.
def print_set_by_date(irc, date):
    date = date.replace('/', '-')

    try:
        qyear = year_value(date)
    except ValueError:
        irc.msg('Error: Invalid date format.')
        return

    database = filehandle.get_list('text/archive.db')
    for entry in database:
        if '::' not in entry:
            continue
        db_date = entry.split('::')[0]
        if date == db_date:
            db_file = entry.split('::')[1].strip()
            setlist = filehandle.get_list(db_file)
            irc.msg(setlist[0] + ':')

            setprint = txtfunctions.create_set_string(setlist[1:])
            irc.msg(setprint)
            return

    tours = sorted(os.listdir('GigArchive'))

    for tour in tours:
        if tour_in_range(tour, qyear):
            gigs = sorted(os.listdir('GigArchive/%s' % tour))
            for gig in gigs:
                if gig_date(gig) == date:
                    gig_file = 'GigArchive/%s/%s' % (tour, gig)
                    setlist = filehandle.get_list(gig_file)
                    irc.msg(setlist[0] + ':')

                    setprint = txtfunctions.create_set_string(setlist[1:])
                    irc.msg(setprint)
                    if len(database) >= 100:
                        database.pop(0)
                    database.append('%s::%s' % (date, gig_file))
                    filehandle.put_list('text/archive.db', database)
                    return
    irc.msg('Could not find the gig from that date.')

# Called by !previous
def print_recent_setlist(irc):
    tours = sorted(os.listdir('GigArchive'))
    tour  = tours.pop()
    gigs  = sorted(os.listdir('GigArchive/%s' % tour))
    gig   = gigs.pop()

    setlist = filehandle.get_list('GigArchive/%s/%s' % (tour, gig))
    irc.msg('%s:' % setlist[0])

    setprint = txtfunctions.create_set_string(setlist[1:])
    irc.msg(setprint)
