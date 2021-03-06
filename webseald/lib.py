import tempfile
import os
from collections import OrderedDict
import websealconfigparser
import yaml

# these are stanza entries that should not be modified
#
global skipStanzas
skipStanzas = ["webseal-config", "ldap", "uraf-registry", "manager", "meta-info", "authentication-mechanisms",
               "cfg-db-cmd:entries", "cfg-db-cmd:files", "aznapi-external-authzn-services", "translog:pd.webseal",
               "configuration-database", "system-environment-variables", "appliance-preset", "audit-configuration",
               "policy-director", "http-transformations:<resource-name>", "tfimsso:<jct-id>", "sso:<service-name>", "jwt:<jct-id>", "aznapi-entitlement-services"]
#aznapi-entitlement-services -> problem with UPPER lowercase entries.
# The following array contains entries that will be ignored across all stanzas
global ignore_entries
ignore_entries = ['https', 'https-port', 'http', 'http-port', 'azn-server-name', 'azn-app-host', 'pd-user-pwd', 'bind-dn'
                  'bind-pwd', 'network-interface', 'server-name']
# these are only added if http2 is not enabled
ignore_http2_entries = ['http2-max-connections', 'http2-header-table-size', 'http2-max-concurrent-streams', 'http2-initial-window-size', 'http2-max-frame-size',
                        'http2-max-header-list-size', 'http2-max-connection-duration', 'http2-idle-timeout']
# don't process these
ignore_system_entries = ['dynurl-map', 'jctdb-base-path', 'cfgdb-base-path', 'ldap-server-config',
                         'cfgdb-archive', 'unix-pid-file', 'unix-user', 'unix-group', 'request-module-library', 'server-root', 'jmt-map',
                         'ltpa-base-path', 'fsso-base-path', 'local-junction-file-path', 'doc-root', 'mgt-pages-root',
                         'server-log-cfg', 'server-log', 'config-data-log', 'requests-file', 'referers-file',
                         'agents-file', 'auditlog', 'db-file', 'pd-user-name', 'trace-admin-args', 'KRB5_CONFIG',
                         'KRB5RCACHEDIR', 'pam-log-cfg', 'pam-statistics-db-path', 'flow-data-db-path',
                         'ldap-server-config', 'ssl-listening-port', 'cred-attribute-entitlement-services',
                         'ssl-keyfile', 'ssl-keyfile-stash', 'ssl-keyfile-label', 'ssl-local-domain', 'pam-library-directory', 'update-cmd', 'enable-local-junction-scripts']

# store package directory
package_directory = os.path.dirname(os.path.abspath(__file__))
# print("package " + package_directory)

def loadDefaults(_dir, _conffile='defaults.conf'):
    '''
    # this takes information stored like output in config_data_..log
    # it indicates what the defaults are
    # eg.
    # client-connect-timeout = [default] 120
    :param _dir: the directory where defaults.conf is.
    :param _conffile: the name of the configuration file.  defaults to "defaults.conf"
    :return: configparser object
    '''

    print("loading defaults ...\n")
    _configDefaults = websealconfigparser.ConfigParser(strict=False, delimiters=("="))
    _configDefaults.read(os.path.join(_dir, _conffile))
    # filter only values that have "[default]"
    for _section in _configDefaults.sections():
        # skip sections in ignore list
        if not _section in skipStanzas:
            _options = _configDefaults.options(_section)
            if len(_options) > 0:
                for _ws_option in _options:
                    if _configDefaults.has_option(_section, _ws_option):
                        _optionvalues = _configDefaults.get(_section, _ws_option, raw=True)
                        if '\n' in _optionvalues:
                            _optionvalues = _optionvalues.split("\n")
                    else:
                        _optionvalues = []
                    if isinstance(_optionvalues, list):
                        # optionvalues = [(ws_option, v) for v in config.get(section, ws_option)]
                        # now I have an option/value list
                        #
                        # Don't use multivalues as Defaults.  This would be pretty useless anyway.
                        #   Actually, I think I'd need to make every option "default", even if it just says [default] on the first one.
                        if not '[default]' in '\n'.join(_optionvalues):
                            _configDefaults.remove_option(_section, _ws_option)
                        else:
                            # set option , multiple options stored as \n separated string
                            #[_tmpOut.append([ws_option, v]) for v in _optionvalues]
                            _n = [i.strip() for i in _optionvalues]
                            _n = [i.replace('%','%%') for i in _optionvalues]
                            #replace single quotes with double quotes (escaping in yaml syntax)
                            # not necessary anymore for yaml !  pyyaml takes care of this
                            # _n = [i.replace("'","''") for i in _optionvalues]
                            _n = '\n'.join(_n)
                            _configDefaults.set(_section, _ws_option, _n.replace('[default]', ''))
                    else:
                        if not '[default]' in _optionvalues:
                            _configDefaults.remove_option(_section, _ws_option)
                        else:
                            # remove [default]
                            _n = _optionvalues.strip()
                            _n = _n.replace('%', '%%')
                            #_n = _n.replace("'", "''")
                            _configDefaults.set(_section, _ws_option, _n.replace('[default]', ''))
    print("done loading defaults ...\n------------------\n")
    return _configDefaults

def equalsDefault(_defaults, stanza, entry, _value, debug=False):
    '''
    Check if the values for a particular entry are defined as [default] in the defaults.conf.

    :param _defaults: the configParser object containing the defaults.conf
    :param stanza: current stanza to process (section)
    :param entry:  current entry to process
    :param _value: current values
    :return: True if the _value equals what's in the defaults.conf
    '''
    # locate the stanza/entry
    _returnValue = True
    _defaultValue = ''
    if _defaults.has_section(stanza) and _defaults.has_option(stanza, entry):
        _defaultValue = _defaults.get(stanza, entry, raw=True)
        # split if contains '\n'
        _defaultValue = _defaultValue.split('\n')
        _defaultValue = [_d.strip() for _d in _defaultValue]
    #
    # ALL values must be default values, otherwise we need to output the complete entry
    #
    if isinstance(_defaultValue, list):
        if isinstance(_value, list):
            for _v in _value:
              if debug:
                print(stanza + " : Checking " + entry + " | <" + _v.strip().replace('%', '%%') + ">")
              if _v.strip().replace('%','%%') in _defaultValue:
                  _returnValue = True
              else:
                  return False
        else:
           if not _value.strip().replace('%','%%') in _defaultValue:
               return False
    else:
        #default value is a string, but _value may still be multivalue.
        #now if _value is multivalue and default is not, it's impossible that they are equal
        if isinstance(_value, list):
            if debug:
                print([v+"\n" for v in _value])
            _returnValue = False
        else:
            if _defaultValue.strip() == _value.strip().replace('%','%%'):
                _returnValue = True
            else:
                _returnValue = False
    return _returnValue

def _writeRPConfig(_outyaml, _instanceName="Default", _config=None, debug=False):
    '''
    Write the Yaml format for the Reverse proxy creation
    :param _outyaml: the file handle to the yaml file
    :param _config: the configParser object containing everything
    :return: nothing
    '''
    # I should just use yaml.dump()
    headerObject = [{
                        "inst_name": _instanceName,
                        "configuration": {
                            "host": "{{ inventory_hostname }}",
                            "listening_port": _config.get("ssl", "ssl-listening-port"),
                            "admin_id": "sec_master",
                            "admin_pwd": "{{ vault_sec_master_pwd }}",
                            "domain": "Default",
                            "http_yn": _config.get("server", "http"),
                            "http_port": _config.get("server", "http-port"),
                            "https_yn": _config.get("server", "https"),
                            "https_port": _config.get("server", "https-port"),
                            "ip_address": _config.get("server", "network-interface")
                            },
                        "entries": [],
                    }]
    if debug:
        print(yaml.dump(headerObject))
    return headerObject

def f_processwebsealdconf(_file, outdir=None, skipInstanceHeader=None, debug=False):
    '''Generate an ini and a yaml file

    :param _file: the webseald.conf file (obtained from export)
    :param skipInstanceHeader: if True, will skip adding a "instance:" part to the yaml file.
    :param outdir: the target directory, defaults to the TEMP or TMP dir configured for the user
    :param debug: Print debug statements
    :return:
    '''
    config = websealconfigparser.ConfigParser(interpolation=None, allow_no_value=True, strict=False, delimiters=("="))
    config.read(_file)
    configDefaults = loadDefaults(package_directory)

    websealdservername = config.get("server", "server-name")
    websealdname = config.get("aznapi-configuration", "azn-server-name")
    # instance name is the first -webseald-
    if "-webseald-" in websealdname:
        websealdname = websealdname.split("-webseald-")[0]
    print("instance "+websealdname)
    # open a file for writing
    if outdir == None:
        outdir = tempfile.gettempdir()
    if outdir.endswith('/'):
        outdir = outdir[:-1]
    outfilename = outdir + '/' + websealdname + ".conf"
    outyaml = outdir + '/' + websealdname + ".yaml"
    outf = open(outfilename, "w", encoding='iso-8859-1')

    outy = open(outyaml, "w", encoding='iso-8859-1')
    outy.write("---\n")
    yamlObject = [{"entries": []}]
    if not skipInstanceHeader:
        try:
            yamlObject = _writeRPConfig(outy, websealdname, config, debug)
        except:
            print("writing instance to yaml failed")

    #if http2 is not enabled, remove all occurences
    try:
        if 'no' in config.get("server", "enable-http2"):
            _ignore_entries = ignore_entries + ignore_http2_entries
        else:
            _ignore_entries = ignore_entries
    except:
        print("no enable-http2 in configuration")
        _ignore_entries = ignore_entries

    for section in config.sections():
        # translate to a json/yaml object
        # find the item that's in the junction file, and map it to an item in config
        # print('Number of elements: ' + str(len(junction)))
        if debug:
            print("-- Section " + section)
        # skip sections in ignore list
        if section in skipStanzas:
            if debug:
                print("---> SKIP STANZA " + section)
        else:
            _options = config.options(section)
            _tmpOut = []
            tmpOutYaml = OrderedDict()

            # writeSection = False
            if len(_options) > 0:
                # _tmpOut.append("["+section+"]")
                for ws_option in _options:
                    if ws_option in _ignore_entries:
                        if debug:
                            print("---> SKIP ENTRY not processed by API : " + ws_option)
                        continue
                    if ws_option in ignore_system_entries:
                        if debug:
                            print("---> SKIP System entry : " + ws_option)
                        continue
                    _optionvalues = config.get(section, ws_option, raw=True)
                    #
                    # multivalue are stored as \n separated string (default behaviour in configparser.py)
                    #
                    if '\n' in _optionvalues:
                        _optionvalues = _optionvalues.split("\n")
                    if isinstance(_optionvalues, list) and _optionvalues:
                        # print([(ws_option, v) for v in _optionvalues])
                        # optionvalues = [(ws_option, v) for v in config.get(section, ws_option)]
                        # now I have an option/value list
                        #
                        if not equalsDefault(configDefaults, section, ws_option, _optionvalues, debug=debug):
                            #_tmpOut.append([ws_option, v] for v in _optionvalues)
                            for v in _optionvalues:
                                _tmpOut.append([ws_option, v])
                                if debug:
                                    print( "- added " + v)
                    else:
                        if '/var/pdweb' in _optionvalues:
                            # only take the last of the filename, this is specifically for "keyfiles" etc.
                            _optionvalues = _optionvalues[_optionvalues.rfind("/") + 1:]
                            if debug:
                                print("/var/pdweb " + _optionvalues)
                        if not equalsDefault(configDefaults, section, ws_option, _optionvalues, debug=debug):
                            _tmpOut.append([ws_option, _optionvalues])
            else:
                if debug:
                    print("Stanza " + section + " has no options")
            if _tmpOut:
                # ini file
                outf.write("[" + section + "]\n")
                tmpOutYaml2 = {"method": "set", "stanza_id": section, "entries": []}
                for line in _tmpOut:
                    outf.write(line[0] + " = " + line[1] + "\n")
                    if '{%' in line[1]:
                        # this makes sure request-log-format can be written
                        line[1] = '{% raw %}' + line[1] + '{% endraw %}'

                    tmpOutYaml2["entries"].append([line[0], line[1]])
                yamlObject[0]["entries"].append(tmpOutYaml2)
                tmpOutYaml2 = None

    outf.close()
    outy.write(yaml.dump(yamlObject, default_style=None, default_flow_style=None, sort_keys=False))
    outy.close()
    # print
    print("\n\nCONF FILE WRITTEN TO: " + outfilename + "\n")
    print("YAML FILE WRITTEN TO: " + outyaml)
