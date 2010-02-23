# http://blog.gpowered.net/2007/08/google-reader-api-functions.html
# http://blog.martindoms.com/2009/08/15/using-the-google-reader-api-part-1/
# http://blog.martindoms.com/2009/08/15/using-the-google-reader-api-part-1/
# http://code.google.com/p/pyrfeed/wiki/GoogleReaderAPI
# http://www.niallkennedy.com/blog/2005/12/google-reader-api.html

# post-process functions that take webscript results and retrieve 
# variables for later calls in the testSuite
def process_login(result, opts):
    auth_resp_dict = dict(x.split('=') for x in result.split('\n') if x)
    opts['auth'] = auth_resp_dict["Auth"]
    opts['lsid'] = auth_resp_dict["LSID"]
    opts['sid'] = auth_resp_dict["SID"]
    opts['Cookie'] = 'Name=SID;SID=%s;Domain=.google.com;Path=/;Expires=160000000000' % auth_resp_dict["SID"]
    return opts

def process_token(result, opts):
    opts['token'] = result
    return opts

# add each curl command here
curl_suite = [
    {"name":"login",
     "curl_statement":"curl --silent -G https://www.google.com/accounts/ClientLogin -d Email={user} -d Passwd={password} -d accountType=GOOGLE -d source=Google-cURL-Example -d service=reader",
     "post_process":process_login},

    {"name":"get token",
     "curl_statement":'curl -G -b "{Cookie}" http://www.google.com/reader/api/0/token',
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

# This function interpolates variables against the curl command string
def parse_vars(cmd, opts):
    '''This function takes a string and variable substutes values in the the opts hash argument.'''
    for (k, v) in opts.items():
        optcmd = "{%s}" % k
        cmd = cmd.replace(optcmd, v)
    return cmd

# Our main routine
def main():
    import getpass

    opts = {}
    opts['user'] = raw_input('User: ')
    opts['password'] = getpass.getpass(prompt='Passwpord: ')

    opts['tag'] = 'blogroll'.encode('utf-8')
    opts['feed'] = 'http://www.philly.com/blinq.rss'.encode('utf-8')
    opts['client'] = opts['user'] + "@gmail.com".encode('utf-8')
    opts['label'] = 'philly'

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




