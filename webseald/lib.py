import base64
import tempfile
import configparser


def decodeBase64(input, encoding='utf-8'):
    #utf-8, ascii, ...
    base64_bytes = input.encode(encoding)
    message_bytes = base64.b64decode(base64_bytes)
    decoded = message_bytes.decode(encoding)
    return decoded

def f_processwebsealdconf(_file):
    config = configparser.ConfigParser()
    config.read(_file)
    print(config)
    #for item in doc.items():
    #    print(item)
    #    print("\n")

    # open a file for writing
    outfilename = tempfile.gettempdir() + junction_name + ".yaml"

    outf = open(outfilename, "w", encoding='iso-8859-1')
    outf.writelines("---\n")
    for junction in doc.items():
        # translate to a json/yaml object
        # find the item that's in the junction file, and map it to an item in config
        #print('Number of elements: ' + str(len(junction)))
        isamservers = []
        for junctionvars in junction[1]:
            jsonvars = mapping_table.get(junctionvars)
            # return an object
            if jsonvars is not None:
                jsonvarn = jsonvars.get('name')
                jsonvarsinglevalue = jsonvars.get('boolean')
            else:
                jsonvarn = None
                jsonvarsinglevalue = False
            #if jsonvarn is not None and junction[1][junctionvars] is not None:
            if jsonvarn is not None:
                if jsonvarn.startswith("servers."):
                    isamservers = f_servers(isamservers, 0, jsonvarn[jsonvarn.rfind(".") + 1:],
                                            junction[1][junctionvars])
                elif junctionvars == 'VIRTUALHOSTJCT':
                    #add virtual_hostname
                    outf.write("virtual_hostname: " + junction[1].get('VIRTHOSTNM') + "\n")
                elif junctionvars == 'SCRIPTCOOKIE':
                    outf.write(jsonvarn + ": yes\n")
                    #write out the type.  junction_cookie_javascript_block
                    for k in junction[1]:
                        if k.startswith('SCRIPTCOOKIE'):
                            cookieparam = k.replace('SCRIPTCOOKIE','')
                            if cookieparam != '':
                                outf.write("junction_cookie_javascript_block: " + cookieparam.lower() + "\n")
                elif junctionvars == 'CLIENTID':
                    #insert_all
                    #insert_pass_usgrcr
                    #do not insert
                    # also, user and groups are seperate entries
                    if junction[1][junctionvars] == 'do not insert':
                        print(">don't insert header")
                    elif junction[1][junctionvars] == 'user':
                        outf.write(jsonvarn+":\n")
                        outf.write("  - iv_user\n")
                    elif junction[1][junctionvars] == 'groups':
                        outf.write(jsonvarn+":\n")
                        outf.write("  - iv_groups\n")
                    elif junction[1][junctionvars] == 'insert_all':
                        outf.write(jsonvarn+":\n")
                        outf.write("  - all\n")
                    else:
                        #look at the end of the string, it indicates user, groups, iv-user-l and/or cred
                        cred = junction[1][junctionvars].split("_")[-1]
                        #print("> cred:" +cred)
                        cred = [cred[i:i + 2] for i in range(0, len(cred), 2)]
                        print("> cred:" + ",".join(cred))
                        outf.write(jsonvarn + ":\n")
                        for val in cred:
                            if val == 'us':
                                outf.write('  - "iv-user"\n')
                            elif val == 'ln':
                                outf.write('  - "iv-user-l"\n')
                            elif val == 'gr':
                                outf.write('  - "iv-groups"\n')
                            elif val == 'cr':
                                outf.write('  - "iv-cred"\n')
                elif junctionvars =='MUTAUTHBAUP':
                    # extract username/password
                    usernamepassword = decodeBase64(junction[1][junctionvars], "utf-8")
                    #usernamepassword = junction[1][junctionvars].decode('base64')
                    print(usernamepassword)
                    theuser = usernamepassword.split("\n")[0]
                    thepw = usernamepassword.split("\n")[1][:-1]  #this is to remove the strange ^ Q character
                    print("username:" + theuser + ", password: "+thepw)
                    outf.write("username: " + theuser + "\n")
                    outf.write("password: " + thepw.strip() + "\n")
                elif jsonvarsinglevalue is not None and jsonvarsinglevalue:
                    # variables that are just present, and hence are True
                    outf.write(jsonvarn + ": yes\n")
                else:
                    if junction[1][junctionvars] is not None:
                        print(junctionvars + ": " + junction[1][junctionvars])
                        outf.write(jsonvarn + ": " + junction[1][junctionvars] + "\n")
                    else:
                        print("002. Skipping " + junctionvars)
            else:
                print("001. Skipping " + junctionvars)

    # write out servers
    print(isamservers)
    outf.write("servers:\n")
    for r in isamservers:
        outf.write("  -\n")
        for ser in r:
            outf.write("    ")
            outf.write(ser + ": " + r[ser])
            outf.write("\n")
    outf.close()

    #print
    print("\n\nWRITTEN TO: " + outfilename)
