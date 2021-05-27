import tempfile
import os
from collections import OrderedDict
import tomsconfigparser

# these are stanza entries that should not be modified
#
global skipStanzas
skipStanzas = ["webseal-config", "uraf-registry", "manager", "meta-info", "authentication-mechanisms",
               "cfg-db-cmd:entries", "cfg-db-cmd:files", "aznapi-external-authzn-services", "translog:pd.webseal",
               "configuration-database", "system-environment-variables", "appliance-preset", "audit-configuration",
               "policy-director"]

# The following array contains entries that will be ignored across all stanzas
ignore_entries = ['https', 'https-port', 'http', 'http-port', 'azn-server-name', 'azn-app-host', 'pd-user-pwd',
                  'bind-pwd', 'network-interface', 'server-name', 'listen-interface']
# don't process these
ignore_system_entries = ['dynurl-map', 'logcfg', 'jctdb-base-path', 'cfgdb-base-path', 'ldap-server-config',
                         'cfgdb-archive', 'unix-pid-file', 'request-module-library', 'server-root', 'jmt-map',
                         'ltpa-base-path', 'fsso-base-path', 'local-junction-file-path', 'doc-root', 'mgt-pages-root',
                         'server-log-cfg', 'server-log', 'config-data-log', 'requests-file', 'referers-file',
                         'agents-file', 'auditlog', 'db-file', 'pd-user-name', 'trace-admin-args', 'KRB5_CONFIG',
                         'KRB5RCACHEDIR', 'pam-log-cfg', 'pam-statistics-db-path', 'flow-data-db-path',
                         'ldap-server-config']
# Ignore duplicate entries.  this is not exactly correct.
# TODO handle duplicate entries.  These will not be handled at the moment
ignore_stanzas_duplicate = ['ssl-qop-mgmt-default', 'user-agent-groups', 'eai-trigger-urls', 'filter-events',
                            'filter-schemes', 'filter-content-types']
ignore_entries_duplicate = ['local-response-redirect-uri']
# store package directory
package_directory = os.path.dirname(os.path.abspath(__file__))
print("package " + package_directory)


def loadDefaults(_dir):
    # this takes information stored like output in config_data_..log
    # it indicates what the defaults are
    # eg.
    # client-connect-timeout = [default] 120
    print("loading defaults ...\n")
    _configDefaults = tomsconfigparser.ConfigParser(strict=False)
    _configDefaults.read(os.path.join(_dir, "defaults.conf"))
    _skipStanzas = skipStanzas + ignore_stanzas_duplicate
    # filter only values that have "[default]"
    for _section in _configDefaults.sections():
        # skip sections in ignore list
        if not _section in _skipStanzas:
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
                            _n = _n.replace('%', '%%')
                            _configDefaults.set(_section, _ws_option, _n.replace('[default]', ''))
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


def f_processwebsealdconf(_file):
    config = tomsconfigparser.ConfigParser(interpolation=None, allow_no_value=True, strict=False)
    config.read(_file)
    configDefaults = loadDefaults(package_directory)
    websealdname = config.get("server", "server-name")
    # open a file for writing
    outfilename = tempfile.gettempdir() + '/' + websealdname + ".conf"
    outyaml = tempfile.gettempdir() + '/' + websealdname + ".yaml"
    outf = open(outfilename, "w", encoding='iso-8859-1')
    # outf.writelines("---\n")
    outy = open(outyaml, "w", encoding='iso-8859-1')
    outy.write("---")
    for section in config.sections():
        # translate to a json/yaml object
        # find the item that's in the junction file, and map it to an item in config
        # print('Number of elements: ' + str(len(junction)))
        print("-- Section " + section)
        _skipStanzas = skipStanzas + ignore_stanzas_duplicate
        # skip sections in ignore list
        if section in _skipStanzas:
            print("---> SKIP STANZA " + section)
        else:
            _options = config.options(section)
            _tmpOut = []
            tmpOutYaml = OrderedDict()
            # writeSection = False
            if len(_options) > 0:
                # _tmpOut.append("["+section+"]")
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
                    #
                    # multivalue are stored as \n separated string (default behaviour in configparser.py)
                    #
                    if '\n' in _optionvalues:
                        _optionvalues = _optionvalues.split("\n")
                    if isinstance(_optionvalues, list) and len(_optionvalues) > 1:
                        # print([(ws_option, v) for v in _optionvalues])
                        # optionvalues = [(ws_option, v) for v in config.get(section, ws_option)]
                        # now I have an option/value list
                        print("LIST " + ws_option)
                        [_tmpOut.append([ws_option, v]) for v in _optionvalues]
                    else:
                        if '/var/pdweb' in _optionvalues:
                            # only take the last of the filename, this is specifically for "keyfiles" etc.
                            _optionvalues = _optionvalues[_optionvalues.rfind("/") + 1:]
                            print("/var/pdweb " + _optionvalues)
                        if not equalsDefault(configDefaults, section, ws_option, _optionvalues):
                            _tmpOut.append([ws_option, _optionvalues])
                        # else:
                        #    print("-> Default matches value [" + section + "] - " + ws_option)
            else:
                print("Stanza " + section + " has no options")
            if len(_tmpOut) > 0:
                # ini file
                outf.write("[" + section + "]\n")
                [outf.write(line[0] + " = " + line[1] + "\n") for line in _tmpOut]
                # [outy.write('- {method: set, stanza_id: \''+ section +'\', entries: [[\''+line[0]+'\', \''+line[1]+'\']]}\n') for line in _tmpOut]
                writtenOption = []
                for line in _tmpOut:
                    if line[0] in writtenOption:
                        # if line[0] == previous one, do something differently
                        _curVal = tmpOutYaml[line[0]]
                        _curVal = _curVal.rstrip("}\n")
                        if _curVal.endswith("]]"):
                            _curVal = _curVal[:-1]
                        tmpOutYaml[line[0]] = _curVal + ',\n    [\'' + line[0] + '\', \'' + line[1] + '\']]}'
                        print(tmpOutYaml[line[0]])
                    else:
                        tmpOutYaml[line[0]] = '\n- {method: set, stanza_id: \'' + section + '\', entries: [[\'' + line[0] + '\', \'' + line[1] + '\']]}'
                    writtenOption.append(line[0])
                outy.write(''.join(tmpOutYaml.values()))
                tmpOutYaml = None
    outf.close()
    outy.close()
    # print
    print("\n\nCONF FILE WRITTEN TO: " + outfilename + "\n")
    print("YAML FILE WRITTEN TO: " + outyaml)
