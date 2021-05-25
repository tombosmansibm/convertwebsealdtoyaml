import base64
import tempfile
import os
import configparser
#defaults=None, dict_type=dict, allow_no_value=False, delimiters=('=', ':'), comment_prefixes=('#', ';'), inline_comment_prefixes=None, strict=True, empty_lines_in_values=True, default_section=configparser.DEFAULTSECT, interpolation=BasicInterpolation(), converters={})

#these are stanza entries that should not be modified
global skipStanzas
skipStanzas = ["meta-info", "authentication-mechanisms", "cfg-db-cmd:entries", "cfg-db-cmd:files", "aznapi-external-authzn-services", "translog:pd.webseal", "configuration-database", "system-environment-variables", "appliance-preset", "audit-configuration", "policy-director" ]

# The following array contains entries that will be ignored across all stanzas
ignore_entries = ['azn-server-name', 'pd-user-pwd', 'bind-pwd', 'network-interface', 'server-name', 'listen-interface']
# don't process these
ignore_system_entries = ['jctdb-base-path', 'cfgdb-base-path', 'ldap-server-config', 'cfgdb-archive', 'unix-pid-file', 'request-module-library', 'server-root', 'jmt-map', 'ltpa-base-path', 'fsso-base-path', 'local-junction-file-path', 'doc-root', 'mgt-pages-root', 'server-log-cfg', 'server-log', 'config-data-log', 'requests-file', 'referers-file', 'agents-file', 'auditlog', 'db-file', 'pd-user-name', 'trace-admin-args', 'KRB5_CONFIG', 'KRB5RCACHEDIR', 'pam-log-cfg', 'pam-statistics-db-path', 'flow-data-db-path', 'ldap-server-config' ]
# Ignore duplicate entries.  this is not exactly correct.
# TODO handle duplicate entries
ignore_entries_duplicate = ['root', 'AREA', 'BODY', 'INPUT', 'LAYER', 'TEXTAREA', 'scheme', 'type' ]
#store package directory
package_directory = os.path.dirname(os.path.abspath(__file__))
print("package " + package_directory)

def loadDefaults(_dir):
    # this takes information stored like output in config_data_..log
    # it indicates what the defaults are
    # eg.
    # client-connect-timeout = [default] 120
    print("loading defaults ...\n")
    _configDefaults = configparser.ConfigParser(strict=False)
    _configDefaults.read(os.path.join(_dir,"defaults.conf"))

    #filter only values that have "[default]"
    for _section in _configDefaults.sections():
        # skip sections in ignore list
        if not _section in skipStanzas:
            _options = _configDefaults.options(_section)
            if len(_options) > 0:
                for _ws_option in _options:
                    if _configDefaults.has_option(_section, _ws_option):
                        _optionvalues = _configDefaults.get(_section, _ws_option, raw=True)
                    else:
                        _optionvalues = []
                    if isinstance(_optionvalues, list):
                        # optionvalues = [(ws_option, v) for v in config.get(section, ws_option)]
                        # now I have an option/value list
                        #
                        # Don't use multivalues as Defaults.  This would be pretty useless anyway.
                        #
                        print("Removed multivalue: " + _ws_option)

                        _configDefaults.remove_option(_section, _ws_option)
                    else:
                        print(_ws_option + " = " + _optionvalues + "\n")
                        if not '[default]' in _optionvalues:
                            _configDefaults.remove_option(_section, _ws_option)
                            print("Removed " + _ws_option)
                        else:
                            # remove [default]
                            _n = _optionvalues.strip()
                            _n = _n.replace('%','%%')
                            _configDefaults.set(_section, _ws_option, _n.replace('[default]','') )
    return _configDefaults

def equalsDefault(_defaults, stanza, entry, _value):
    # locate the stanza/entry
    _defaultValue = ''
    if _defaults.has_section(stanza) and _defaults.has_option(stanza, entry):
        _defaultValue = _defaults.get(stanza, entry, raw=True)
    if _defaultValue.strip() == _value.strip():
        return True
    else:
        return False


def decodeBase64(input, encoding='utf-8'):
    #utf-8, ascii, ...
    base64_bytes = input.encode(encoding)
    message_bytes = base64.b64decode(base64_bytes)
    decoded = message_bytes.decode(encoding)
    return decoded

def f_processwebsealdconf(_file):
    config = configparser.ConfigParser(interpolation = None, allow_no_value=True, strict=False)
    try:
        config.read(_file)
    except (configparser.DuplicateOptionError) as e:
        print("Duplicate option " + str(e))
        return
    configDefaults = loadDefaults(package_directory)
    websealdname = config.get("server","server-name")
    #print(config.sections())
    # duplicate key problem - it not a problem, just need to first create a list
    results = [('BODY', v) for v in config.get("filter-events", "BODY", raw=True)]
    print(results)
    #for item in doc.items():
    #    print(item)
    #    print("\n")

    # open a file for writing
    outfilename = tempfile.gettempdir() + '/' + websealdname + ".conf"

    outf = open(outfilename, "w", encoding='iso-8859-1')
    #outf.writelines("---\n")
    for section in config.sections():
        # translate to a json/yaml object
        # find the item that's in the junction file, and map it to an item in config
        #print('Number of elements: ' + str(len(junction)))
        print("-- Section " + section)
        # skip sections in ignore list
        if section in skipStanzas:
            print("---> SKIP STANZA " + section)
        else:
            _options = config.options(section)
            _tmpOut = []
            #writeSection = False
            if len(_options) > 0:
               #_tmpOut.append("["+section+"]")
               for ws_option in _options:
                   if ws_option in ignore_entries:
                       print("---> SKIP ENTRY not processed by API : " + ws_option)
                       continue
                   if ws_option in ignore_system_entries:
                       print("---> SKIP System entry : " + ws_option)
                       continue
                   if ws_option in ignore_entries_duplicate:
                       print("---> SKIP DUPLICATE : " + ws_option)
                   _optionvalues = config.get(section, ws_option, raw=True)
                   #- {method: set, stanza_id: azn - decision - info, entries: [['urn:schemas', 'post-data:/"schemas"']]}
                   if not isinstance(_optionvalues, str):
                       print([(ws_option, v) for v in _optionvalues])
                       #optionvalues = [(ws_option, v) for v in config.get(section, ws_option)]
                       # now I have an option/value list
                       print("LIST " + ws_option )
                       [_tmpOut.append(ws_option+" = "+v) for v in _optionvalues]
                   else:
                       if not equalsDefault(configDefaults, section, ws_option, _optionvalues):
                           _tmpOut.append(ws_option+" = "+_optionvalues)
                       #else:
                       #    print("-> Default matches value [" + section + "] - " + ws_option)
            else:
                print("Stanza " + section + " has no options")
            if len(_tmpOut) > 0:
                outf.write("["+section+"]\n")
                [outf.write(line+"\n") for line in _tmpOut]
    outf.close()

    #print
    print("\n\nWRITTEN TO: " + outfilename)
