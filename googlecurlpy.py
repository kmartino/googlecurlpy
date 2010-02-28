# Prior art to look at:
# http://blog.gpowered.net/2007/08/google-reader-api-functions.html
# http://blog.martindoms.com/2009/08/15/using-the-google-reader-api-part-1/
# http://blog.martindoms.com/2009/08/15/using-the-google-reader-api-part-1/
# http://code.google.com/p/pyrfeed/wiki/GoogleReaderAPI
# http://www.niallkennedy.com/blog/2005/12/google-reader-api.html
# http://www.25hoursaday.com/weblog/CommentView.aspx?guid=D27EBDD5-EA53-4135-BA08-5A99D5C34290


def process_login(result, opts):
    '''This function captures the AUTH, LSID, and SID from the login call'''
    auth_resp_dict = dict(x.split('=') for x in result.split('\n') if x)
    opts['auth'] = auth_resp_dict["Auth"]
    opts['lsid'] = auth_resp_dict["LSID"]
    opts['sid'] = auth_resp_dict["SID"]
    opts['Cookie'] = 'Name=SID;SID=%s;Domain=.google.com;Path=/;Expires=160000000000' % auth_resp_dict["SID"]
    return opts

def process_token(result, opts):
    '''This function captures the auth token from the response'''
    opts['token'] = result
    return opts

# add each curl command here
curl_suite = [
    {"name":"login",
     "curl_statement":"curl --silent -G https://www.google.com/accounts/ClientLogin -d Email={user} -d Passwd={password} -d accountType=GOOGLE -d source=Google-cURL-Example -d service=reader",
     "post_process":process_login},

    {"name":"get token",
     "curl_statement":'curl -G -b "{Cookie}" https://www.google.com/reader/api/0/token',
     "desciption":"retrieves a token",
     "post_process":process_token},
   
    {"name":"subscription list",
     "curl_statement":'curl -G -b "{Cookie}" http://www.google.com/reader/api/0/subscription/list -d output=json',
     "description":"get a list of the users subscribed feeds"},

    {"name":"reading list",
     "curl_statement":'curl -G -b "{Cookie}" http://www.google.com/reader/atom/user/-/state/com.google/reading-list -d output=json',
     "description":"get a feed of the users unread items"},

    {"name":"read items",
     "curl_statement":'curl -G -b "{Cookie}" http://www.google.com/reader/atom/user/-/state/com.google/read -d output=json',
     "description":"get a feed of the users read items"},

    {"name":"unread items from tagged feeds",
     "curl_statement":'curl -G -b "{Cookie}" http://www.google.com/reader/atom/user/-/label/{tag} -d output=json',
     "description":"unread items from tagged feeds"},

    {"name":"starred items",
     "curl_statement":'curl -G -b "{Cookie}" http://www.google.com/reader/atom/user/-/state/com.google/starred -d output=json',
     "description":"get a feed of a users starred items/feeds"},

    {"name":"un-subcribe to feed",
     "curl_statement":'curl --request POST -b "{Cookie}" http://www.google.com/reader/api/0/subscription/edit -d client={client} -d ac=unsubscribe -d s=feed%2F{feed} -d T={token}',
     "description":"subscribes to a feed"},

    {"name":"subcribe to feed",
     "curl_statement":'curl --request POST -b "{Cookie}" http://www.google.com/reader/api/0/subscription/edit -d client={client} -d ac=subscribe -d s=feed%2F{feed} -d T={token}',
     "description":"subscribes to a feed"},

    {"name":"add feed to folder/label",
     "curl_statement":'curl --request POST -b "{Cookie}" http://www.google.com/reader/api/0/subscription/edit -d client={client} -d ac=edit -d a=user/-/label/{label} -d s=feed%2F{feed} -d T={token}',
     "description":"subscribes to a feed"},

    {"name":"get feed",
     "curl_statement":'curl -G -b "{Cookie}" http://www.google.com/reader/atom/feed/{feed} -d output=json',
     "description":"get a specific feed.  It works for any feed, subscribed or not"},

]

def run_bash(cmd):
    '''This function takes a Bash command and returns the results.'''
    import subprocess
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out = p.stdout.read().strip()
    return out  

def parse_vars(cmd, opts):
    '''This function interpolates variables in the opts dictionary with the cmd string.'''
    for (k, v) in opts.items():
        optcmd = "{%s}" % k
        cmd = cmd.replace(optcmd, v)
    return cmd

# Our main routine
def main():
    import pickle
    import getpass
    import os

    opts = {}
    if os.path.isfile("opts.p"):
        opts = pickle.load(open("opts.p")).copy()

    if len(opts) > 0:
        print opts
        opts['use_defaults'] = raw_input('Use these defaults (y/n): ')

    if len(opts) > 0 and opts.has_key('use_defaults') and opts['use_defaults'] == 'y':
        print 'Using defaults.'
        opts['feed'] = raw_input('Feed (ex http://www.philly.com/blinq.rss): ').encode('utf-8')
    else:
        opts['feed'] = raw_input('Feed (ex http://www.philly.com/blinq.rss): ').encode('utf-8')
        opts['label'] = raw_input('Label/Folder (ex blogroll): ').encode('utf-8')
        opts['tag'] = raw_input('Tag (ex philly): ').encode('utf-8')
        opts['user'] = raw_input('User: ').encode('utf-8')
        opts['save'] = raw_input('Save defaults (y/n)?: ')
        if opts['save'] == 'y':
            pickle.dump({'label':opts['label'], 'tag':opts['tag'], 'user':opts['user']}, open("opts.p", "w"))

    opts['password'] = getpass.getpass(prompt='Password: ')           
    opts['client'] = opts['user'] + "@gmail.com".encode('utf-8')

    # run each curl command against system
    for curl_cmd in curl_suite:
        print curl_cmd["name"]
        curl_statement = parse_vars(curl_cmd["curl_statement"], opts)
        print "$ %s" % curl_statement
        result = run_bash(curl_statement)
        if ("post_process" in curl_cmd):
            opts = curl_cmd["post_process"](result, opts)
        print result
        print "---------------------------\n"	    
	    
if __name__ == '__main__':
    main()




