import os
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

# Number of times a song has been played. Does not count the current setlist.
def song_count(song):
    database = filehandle.get_list('text/archive.db')
    for entry in database:
        if entry.startswith('c!'):
            db_song = entry.split('!')[1].split('=')[0]
            if db_song == song.lower():
                count = int(entry.split('!')[1].split('=')[1])
                return count
            
    count = 0
        
    tours = os.listdir('GigArchive')
    for tour in tours:
        gigs = os.listdir('GigArchive/%s' % tour)
        for filename in gigs:
            setlist = filehandle.get_list('GigArchive/%s/%s' % (tour, filename))
            if song.lower() in [s.lower() for s in setlist]:
                count = count + 1

    if len(database) >= 100:
        database.pop(0)
    database.append('c!%s=%d' % (song.lower(), count))
    filehandle.put_list('text/archive.db', database)
    return count

# Finds the most recent performance of a song. Does count the current setlist.
def last_played(irc, song):
    if song.lower() in [s.lower() for s in filehandle.get_list('text/setlist')]:
        gig = filehandle.get_list('text/gig')
        irc.msg ('%s was last played at: %s' % (song, gig[0]))
        return

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
        gigs = sorted(os.listdir('GigArchive/%s' % tour))
        for filename in reversed(gigs):
            gig_file = 'GigArchive/%s/%s' % (tour, filename)
            setlist = filehandle.get_list(gig_file)
            if song.lower() in [s.lower() for s in setlist]:
                irc.msg('%s was last played at: %s' % (song, setlist[0]))
                if len(database) >= 100:
                    database.pop(0)
                database.append('lp!%s::%s' % (song.lower(), gig_file))
                filehandle.put_list('text/archive.db', database)
                return
    irc.msg('I do not seem to have information on that song.')

# Searches the file names of setlists to match a query.
# Results are greatly limited due to IRC message character limits.
# This does not access the database file.
def find_setlist(irc, query):
    query = query.lower()
    found = []
    tours = os.listdir('GigArchive')
    for tour in tours:
        gigs = os.listdir('GigArchive/%s' % tour)
        for filename in gigs:
            if filename.lower().find(query) != -1:
                found.append(filename)
    if len(found) == 0:
        irc.msg("No gigs found for given query.")
    else:
        output = "\"%s\"" % found[0]
        for gig in found[1:]:
            output = "%s, \"%s\"" % (output, gig)
        if len(output) > 400:
            irc.msg("Too vague! Please specify.")
        else:
            irc.msg("Possible setlists: %s" % output)

# Takes a date in the form YYY/MM/DD and prints the corresponding setlist.
def print_set_by_date(irc, date):
    def year_value(date):
        return int(date.split('-')[0])
    def gig_date(filename):
        return filename.split()[0].strip()
    def tour_in_range(tour, year):
        gigs = sorted(os.listdir('GigArchive/%s' % tour))
        start_year = year_value(gig_date(gigs[0]))
        end_year   = year_value(gig_date(gigs[len(gigs) - 1]))

        return year >= start_year and year <= end_year

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
