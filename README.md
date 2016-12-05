
# What is it?
Pure is a *specification* for a configuration file format. Its goal is to
suck less than other configuration file formats. People have already started
on parsers; see the Implementation section for details.

Most people will find Pure entirely natural to read and edit. See examples later on.

To learn about why Pure exists, see https://github.com/pureconfig/pureconfig/wiki/Rationale

# File extension
The standard file name extension is *.pure*, to make it clear to users that they are
dealing with pure config files. That said, you can call it whatever you want.

# Examples
To start off, a pure file can be as simple as flat list of configuration properties:

```
port = 8443
bind = 0.0.0.0
```

It's as simple as *property = value*

Let's collect those related properties into a group called *server*

```
server.port = 8443
server.bind = 0.0.0.0
```

If we get a lot of these, we have to repeat the *server* prefix. Bad. Pure supports
nested grouping, which should be your default choice:

```
server
    port = 8443
    bind = 0.0.0.0
```

**However**. You can combine nesting and dot notation for groups. This is more useful than
you might think. For instance, you may want to place all log levels at the end of
the file, instead of spreading them all over the place:

```
# Server configuration
server
    port = 8443
    bind = 0.0.0.0

# Db configuration
database
    url = something-cool-here
    user = sys
    password = something
    timeout = 30s

    # Another nesting level (there's no limit)
    data
        path = ../data
        indexed = true

# A separate section with log levels
server.log.level = debug
database.log.level = info
```

A side note: ```user = sys``` and ```user = "sys"``` is the same thing, quotes
are optional. Joe Plumber hate quotes.

# Graph structure
You can *reference* any property, at any level, in the config file.

This is accomplished by using => instead of =

```
# Both the server and database config will reuse most of this:
shared
    log
        filename = server.log
        rolling = true
        keep-count = 10
        max-size = 50MB

# Use the same log config as the shared one, but override the max-size.
# Let's also add a date property only relevant for the server.
server
    log => shared.log
        max-size = 10MB
        date-format = "yyyy-mm-dd"

# We're happy with the log defaults, but change the file name
database
    log => shared.log
        filename = db.log
```

Indeed, this means you can serialize object graphs *with cycles* to a highly
readable format.

You can also reference a specific value.

```
vars.filename = thefile.txt

# Later on, we need to reference vars.filename
server.data => vars.filename
```

Yup, ```config.get("server.data")``` will return "thefile.txt"

# Accessing environment variables
The parser *must* support replacing environment variables. It's easy to implement, and very useful. It must be possible to turn this feature off.

```
app.logfile = $HOME/.logs/myapp.log
```

The $NAME and ${NAME} syntax is supported on all platforms.

# List of things/arrays

As you'd expect:
```
server.allowed-hosts = [localhost, 127.0.0.1, 192.168.0.1]
```

A more elaborate example, including referencing other array elements. Note that
commas are optional between items when using indentation style, in which case the []'s appear
at the same level as the key:

```
servers = 
[
    app-1
        host = 1.2.3.4
        port = 8443
        datadir = ./data   
    app-2 => servers.app-1
       host = 1.2.3.5
    dbserver
       host = 1.2.3.6
       port = 9931
]

# DevOp drama! We need tracing on app-1
servers.app-1.log.level = trace
servers.app-2.log.level = info
```

# Encoding

A pure file is required to be UTF-8 encoded (which also means ASCII files are accepted)

# Whitespaces, quotes and escape sequences

* Key and values are trimmed for whitespaces, using the unicode definition of white spaces.
* Whitespaces can be inserted using \
* Literal quotes can be inserted using \" and \'

The following two lines are equivalent
```
  key   =    value
key = value  
```

Escaping:
```
key = \ \ \ \ this value has four spaces in front of it
quotes = \"a quoted string\"
spaces-and-quotes = "    \"quoted string with four spaces in front\""
backslash = c:\\program files\\my app
```

Whitespaces are *not* allowed in keys. Moreover, only printable ASCII characters are allowed. This
ensures that keys are easily accessible in all language runtime (not every language supports utf8 literals)

# Multiline properties
Just like Java properties:
```
value = This is a long \
        property \
        value
```
Which parses to *This is a long property value*. Note how leading whitespaces on each
line is trimmed.

# Including other pure files

Other config files can be included, such as a config for a module, a snippets or a template
of some sort.

Including template configurations is especially useful in Pure since it supports referencing
and overriding other properties.

```
%include template.pure
%include ../modules/base.pure

log => base.log
    log.level = info
    log.filename = app.log
    
...etc
```
The include directive supports relative and absolute paths, as well as URLs (file:/// and http:///)

In the future, partial includes and namespaces might be supported, but Pure 1.0 will only offer simple includes. 

# Schema support
Optionally, a Pure parser may support schema definitions. This is a separate file
defining the structure of a config file. It looks almost like a regular Pure file.

You pass this to the parser along with the config file. If the config file doesn't adhere
to the schema, parsing will fail.

Property definitions with default values are optional; all others are required.

Any attempt to add properties not defined in the schema will cause
parsing to fail (catching spelling mistakes). However, a group can contain
undefined properties if the group is marked *allow-undefined* (currently
the only annotation)

**server-config.def**
```
server
    log
        date-format: string("yyyy-mm-dd")
        keep-count: int(10)
        filename: path
        max-size: quantity(50MB)
        rolling: bool

    user-properties [allow-undefined]
```

See how the schema format mirrors the property value format? Instead of
*prop = value* we have *prop: type*

Of course, we can reference other definitions using => to avoid
duplication:

```
shared
    log
        filename: path(server.log)
        rolling: bool(true)
        max-size: quantity(50MB)
        keep-count: int(10)

server
    log => shared.log
    bind: string
    port: int(8443)
```

# Data types

The parser *should* designate a data type to every property, whether a
definition file exists or not. This makes sense only for statically typed
languages, of course.

*To allow for minimal API's, every typed value must have a string representation,
which is simply its literal string, as it appears in the file.*

The type inference rules are straightforward. Note that all values can be
null, meaning the key is not present. If the key is present, but no value is
set, then the default value for the given type is used ("", 0, 0.0, false)

Why data types like "quantity" and "path" ? Because these are so frequent in
configuration files that it makes sense to provide special support for them. By
special support, we mean that the API *may* provide typed getter/setters, although
that's not a requirement.

```
Data type           Inference rule
----------------------------------------------------------------------------
string              If the value is "quoted" or 'single quoted', it's
                    always a string.

                    Moreover, any value not inferred to be of any other
                    type is a string, such as username = admin

int                 64-bit signed integer literal, such as 9500

double              64-bit IEEE double literal, such as 3.1415

bool                Literals true and false

path                A string leading with . or containing / or \

                    The parser is required to translate path separators to
                    the proper system separator.

quantity            An integer followed by a unit, such as 250ms,
                    50MB, 60s, 200cm

                    SI units should be used, but anything is allowed. There
                    must be an API to get both the value and the unit.
```

# Include files

A Redditor proposed an %include directive. The env variable syntax can be used to communicate variables (of course, these 
are only visible to the parser)

```
$SOMEPARAM = ./data
%include other.conf
```

You can also specify glob-like patterns to include more than one file (ordered alphabetically):

```
%include conf.d/*.conf
```

# API
Pure doesn't specify an API, just a format. Use whatever is idiomatic in a given language. 

The API in an OOP language is probably just a set of get/set methods to access properties, and a way
to load and save.

Use "dot.notation" to reference groups. This must work even if indentation style grouping is used.

In Java, a Pure parser might look something like this:

```
// Get the port
int port = config.getInt("server.port");

// Or, interpret as string, no matter what the value type is
String port = config.get("server.port");

// Check if the path exists
if (config.getPath("database.dir").exists())
  ...

// Get a quantity
int logSize = config.getQuantityValue("log.size"); // 500
String unit = config.getQuantityUnit("log.size");  // "MB"

// Same as above, using a pair type provided by the API (or whatever
// the language runtime offers)
Pair logSize = config.getQuanity("log.size");

// Set the port
config.put("server.port", 8443);
```

# What's next
This spec is work in progress and I'm more than happy to take pull requests and discuss issues!

* A formal specification, although the informal description above should be
enough to write a parser.
* Yes, actual parsers must be written. Pull requests accepted for any language!
A non-validating one should doable as a weekend project for your favorite language.
* Consider supporting inline type definitions, such as *username: string = admin* 

# Implementations

People have already started working on implementations. Thanks a lot guys!

* Rust - [pureconfig-rust](https://github.com/shelbyd/pureconfig-rust)
* Python - See the pureconfig repo

# Reddit input so far
* It's awesome (thanks!)
* It's shit (sod off, you insensitive clod)
* Yes, definitely need a spec (agreed!)
* Include files would be great (agreed!)
* Specify UTF8 clearly (agreed!)
* ${ENVVAR} alternative to $ENVVAR to disambiguate

