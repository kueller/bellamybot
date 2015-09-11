import os
import filehandle
import txtfunctions

def song_count(song):
    count = 0
    tours = os.listdir('GigArchive')
    for tour in tours:
        gigs = os.listdir('GigArchive/%s' % tour)
        for filename in gigs:
            setlist = filehandle.get_list('GigArchive/%s/%s' % (tour, filename))
            if song.lower() in [s.lower() for s in setlist]:
                count = count + 1
    return count

def last_played(irc, song):
    if song.lower() in [s.lower() for s in filehandle.get_list('text/setlist')]:
        gig = filehandle.get_list('text/gig')
        irc.msg ('%s was last played at: %s' % (song, gig[0]))
        return
    
    tours = sorted(os.listdir('GigArchive'))
    for tour in reversed(tours):
        gigs = sorted(os.listdir('GigArchive/%s' % tour))
        for filename in reversed(gigs):
            setlist = filehandle.get_list('GigArchive/%s/%s' % (tour, filename))
            if song.lower() in [s.lower() for s in setlist]:
                irc.msg('%s was last played at: %s' % (song, setlist[0]))
                return
    irc.msg('I do not seem to have information on that song.')

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

    tours = sorted(os.listdir('GigArchive'))

    for tour in tours:
        if tour_in_range(tour, qyear):
            gigs = sorted(os.listdir('GigArchive/%s' % tour))
            for gig in gigs:
                if gig_date(gig) == date:
                    setlist = filehandle.get_list('GigArchive/%s/%s' % (tour, gig))
                    irc.msg(setlist[0] + ':')

                    setprint = txtfunctions.create_set_string(setlist[1:])
                    irc.msg(setprint)
                    return
    irc.msg('Could not find the gig from that date.')
    
def print_recent_setlist(irc):
    tours = sorted(os.listdir('GigArchive'))
    tour  = tours.pop()
    gigs  = sorted(os.listdir('GigArchive/%s' % tour))
    gig   = gigs.pop()

    setlist = filehandle.get_list('GigArchive/%s/%s' % (tour, gig))
    irc.msg('%s:' % setlist[0])

    setprint = txtfunctions.create_set_string(setlist[1:])
    irc.msg(setprint)
