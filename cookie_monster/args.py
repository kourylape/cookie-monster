"""Configure Arguments for the CLI"""

import argparse

class Args(object):
    """Configure the arguments"""

    def __init__(self):
        parser = argparse.ArgumentParser(prog='cookie-monster')

        # Force Boolean
        parser.add_argument('--force', action='store_true',
                            help = 'Force rescanning all URLs of the sitemap')

        # Ouput URL
        parser.add_argument('-o', '--output', metavar='FILE', default='output.csv',
                            help='The path and filename of the output CSV file. Defaults to "output.csv".')

        req = parser.add_argument_group('required arguments')

        # API Key
        req.add_argument('-k', '--key', required=True,
                         help='Web Cookies API key (https://webcookies.org/)')

        # Sitemap URL
        req.add_argument('-s', '--sitemap', required=True, metavar='URL',
                         help='URL to site\'s sitemap XML file')

        args = parser.parse_args()

        self.key = args.key
        self.sitemap = args.sitemap
        self.force = args.force
        self.output = args.output
