# How to Contribute

## Types of plugins accepted

We are interested in general-use plugins that have the potential to be used on multiple channels. If you have an idea that is unique to your specific channel, it's unlikely to be accepted. If you are unsure, ask first (file an issue or via `#lincolnloop` on Freenode).

Also be sure your plugin meets [Freenode's channel guidelines](http://freenode.net/channel_guidelines.shtml).

## Plugin code requirements

1. Written in Python (2.7.x)
2. Closely follows [PEP 8 guidelines](http://www.python.org/dev/peps/pep-0008/)
3. Tested. See `botbotme_plugins/tests` directory for examples.
4. Each plugin is implemented as a single module in the `botbotme_plugins/plugins` directory. The module should contain a single `Plugin` class that inherits from `botbotme_plugins.base.BasePlugin`.
5. The `Plugin` class' docstring should thoroughly describe its behavior to an end-user. It should start with a single line of text serving as a succinct (75 characters or less) summary. It will be formatted with Markdown and displayed as help text.
6. Preferably no additional external dependencies. Use the standard lib or [existing dependencies](https://github.com/lincolnloop/botbotme-plugins/blob/master/setup.py) whenever possible.
7. Submitted as a pull request via GitHub.