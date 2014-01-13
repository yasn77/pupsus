Pupsus
======

Pupsus allows you to use stored Puppet Modules in Nexus (Or possibly any other Maven Repo). Puppet modules need to be in PuppetForge structure and like 'puppet module' command will handle module dependencies.

## Usage

The default configuration for Pupsus can be found in <code>/etc/pupsus/pupsus.ini</code>, this location can be overwritten with environment variable <code>PUPSUS_CONFIG</code>. The configuration file is a standard INI file with 2 sections <code>[pupsus_main]</code> and <code>[puppet]</code>:

### [pupsus_main]

* <code>nexus_url</code> : Full URL to nexus repository
* <code>aritifact_group</code> : Maven style group ID of the puppet modules in Nexus (i.e some.artfiact.group)
* <code>cache_dir</code> : Pupsus cache directory, requests to Nexus are cached.
* <code>nexus_repository</code> : The Nexus repository where modules are stored.

### [puppet]

* <code>config</code> : Location of Puppet configuration file
* <code>command</code> : Path to Puppet command

All configuration file settings can be overridden from the command line

### Command Line Options
<pre>
usage: pupsus [-h] [-u NEXUS_URL] [-g ARTIFACT_GROUP] [-d CACHE_DIR]
                 [-e, ENVIRONMENT] [-m PUPPET_MODULEPATH] [-f PUPPET_CONFIG]
                 [-p PUPPET_COMMAND]
                 {installenv,search,remove,install} ...

optional arguments:
  -h, --help            show this help message and exit
  
  -u NEXUS_URL, --nexus-url NEXUS_URL
                        URL to Nexus
                        
  -g ARTIFACT_GROUP, --artifact-group ARTIFACT_GROUP
                        Artifact group for modules
                        
  -d CACHE_DIR, --cache-dir CACHE_DIR
                        Directory used to store cache information
                        
  -e, ENVIRONMENT, --environment ENVIRONMENT
                        Puppet environment queried for Modulepath
  
  -m PUPPET_MODULEPATH, --modulepath PUPPET_MODULEPATH
                        Puppet Module path, please note if environment is
                        specified, then the modulepath from Puppet environment
                        will used
                        
  -f PUPPET_CONFIG, --puppet-config PUPPET_CONFIG
                        Puppet configuration file
                        
  -p PUPPET_COMMAND, --puppet-command PUPPET_COMMAND
                        Path to Puppet command

Commands:
  {installenv,search,remove,install}
    install             Install a Puppet module
    search              Search for a Puppet module
    installenv          Install all modules for a Puppet environment
    remove              Remove a module

</pre>

To install all modules for a given environment, a YAML file with a list of modules (and version to install) is required in the modulepath. This file needs to be called <code>{environment}.env</pre></code> (i.e production.env). Below is an example of this file:

<pre>
---
'puppetlabs/stdlib' : 'latest'
'puppetlabs/ntp' : '1.0.1'
'someuser/somemodule' : '>2.1.0'
</pre>

As can be seen from the example, Pupsus supports Semantic Versioning (http://semver.org/spec/v2.0.0.html) for the version number.

