"""
Uses twitter_monitor.basic_stream to stream
filtered tweets to stdout.

This script requires some configuration,
which it can take as command line arguments
read from an ini file, or obtain
from environment variables.

The command line arguments:
    --api-key XXXX
    --api-secret XXXX
    --access-token XXXX
    --access-token-scret XXXX
    --track-file <path-to-file>
    --poll-interval <number>
    --unfiltered TRUE
    --debug TRUE
    --languages en,fr
    <filename>

A sample ini file to be read by ConfigParser:
    [twitter]
    api_key=XXXX
    api_secret=XXXX
    access_token=XXXX
    access_token_secret=XXXX
    track_file=<path-to-file>
    # optional:
    poll_interval=<number>
    unfiltered=TRUE
    debug=TRUE
    languages=en,fr

The environment variables:
    TWITTER_API_KEY=XXXX
    TWITTER_API_SECRET=XXXX
    TWITTER_ACCESS_TOKEN=XXXX
    TWITTER_ACCESS_TOKEN_SECRET=XXXX
    TWITTER_TRACK_FILE=<path-to-file>
    TWITTER_POLL_INTERVAL=<number>
    TWITTER_UNFILTERED=TRUE
    TWITTER_LANGUAGES=en,fr
    TWITTER_DEBUG=TRUE

The order below represents the order of priority as well.
That is, a command-line argument overrides an ini-file setting,
which overrides an environment variable.

One additional command-line argument is available,
to provide a path to an ini file:
    --ini-file <path-to-file>
If this is not provided, the file 'twitter_monitor.ini'
will be used in the current working directory (if it exists).
"""

import configparser
import os
import logging
import argparse

from twitter_monitor import basic_stream

logger = logging.getLogger('twitter_monitor')

CONFIG_SECTION_NAME = 'twitter'


def _configure_logger():
    if not logger.handlers:
        from logging.config import dictConfig

        dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'simple': {
                    'format': '%(asctime)s %(levelname)s %(message)s',
                    'datefmt': '%m/%d %I:%M:%S%p',
                },
            },
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple',
                    'stream': 'ext://sys.stderr',
                },
            },
            'loggers': {
                'twitter_monitor': {
                    'handlers': ['console'],
                    'propagate': False,
                    'level': 'INFO',
                },
            }
        })

class ArgParser(object):
    def __init__(self):

        self.parser = argparse.ArgumentParser(description='Stream filtered tweets to stdout.')
        self.config = configparser.SafeConfigParser()
        self.env = os.environ
        self.options = []

    def add_option(self, dest, arg_name, ini_name, env_name, default=None, help=None, required=True):
        if required and default is not None:
            required = False

        self.options.append((arg_name, env_name, ini_name, default, dest, required))
        self.parser.add_argument(arg_name, dest=dest, help=help, required=False, default=argparse.SUPPRESS)

    def read_vals(self):
        default_ini = os.path.abspath('twitter_monitor.ini')
        self.parser.add_argument('--ini-file', dest='ini_file', help='path to .ini file', default=default_ini)
        self.parser.add_argument('outfile', help='output file, else stdout', default=None, nargs='?')

        args = self.parser.parse_args()

        values = dict()
        for arg_name, env_name, ini_name, default, dest, required in self.options:
            # Try the command line
            logger.debug("Checking arguments for %s", arg_name)
            try:
                value = getattr(args, dest)
                logger.debug("Value is now %s", value)
            except AttributeError:
                # Try the ini file
                try:
                    logger.debug("Checking config file for %s", ini_name)
                    value = self.config.get(CONFIG_SECTION_NAME, ini_name)
                    logger.debug("Value is now %s", value)
                except (configparser.NoOptionError, configparser.NoSectionError):

                    # Try the environment
                    logger.debug("Checking environment for %s", env_name)
                    try:
                        value = self.env[env_name]
                        logger.debug("Value is now %s", value)
                    except KeyError:
                        if required:
                            logger.error("Option %s is required. Use %s, add %s to your .ini file, or set %s.", dest, arg_name,
                                         ini_name, env_name)
                            exit(1)
                        else:
                            logger.debug("Falling back to default value %s", default)
                            value = default

            values[dest] = value

        values['outfile'] = args.outfile

        return argparse.Namespace(**values)


def _read_args():
    parser = ArgParser()

    parser.add_option('track_file', '--track-file', 'track_file', 'TWITTER_TRACK_FILE',
                      default='track.txt',
                      help='tracking term file, one term per line')
    parser.add_option('poll_interval', '--poll-interval', 'poll_interval', 'TWITTER_POLL_INTERVAL',
                      default='15',
                      help='how often to reload the track file')

    parser.add_option('bearer_token', '--bearer-token', 'bearer_token', 'BEARER_TOKEN',
                      help='your Twitter Bearer Token',
                      required=True)
    parser.add_option('unfiltered', '--unfiltered', 'unfiltered', 'TWITTER_UNFILTERED',
                      help="allow unfiltered streaming", 
                      required=False, default=False)
    parser.add_option('languages', '--languages', 'languages', 'TWITTER_LANGUAGES',
                      help="comma-separated language codes",
                      required=False, default=None)
    parser.add_option('debug', '--debug', 'debug', 'TWITTER_DEBUG',
                      help="listen for SIGUSR1 signal to drop into debugger",
                      required=False, default=False)

    return parser.read_vals()


if __name__ == '__main__':
    _configure_logger()
    args = _read_args()
    
    if args.unfiltered not in (False, 'FALSE', '0', 0):
        args.unfiltered = True

    if args.debug not in (False, 'FALSE', '0', 0):
        args.debug = True

    if args.languages not in (False, '0', 0, None):
        args.languages = args.languages.split(',')

    basic_stream.start(track_file=args.track_file,
                       twitter_bearer_token=args.bearer_token,
                       poll_interval=args.poll_interval,
                       unfiltered=args.unfiltered,
                       debug=args.debug,
                       languages=args.languages,
                       outfile=args.outfile)
