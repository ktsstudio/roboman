# coding=utf-8
__author__ = 'grigory51'

from tornado.options import define, options
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_config(path):
    try:
        options.parse_config_file(path=path, final=False)
    except IOError:
        print('[WARNING] File no readable, run with default settings')


define('host', type=str, group='Server', default='127.0.0.1', help='Listen host')
define('port', type=int, group='Server', default=8080, help='Listen port')
define('server_name', type=str, group='Server', default='https://bot.team.ktsstudio.ru')

define('debug', default=False, help='Tornado debug mode')
define('config', type=str, help='Path to config file', callback=parse_config)

define('runtime', type=str, help='Data dir', default=CURRENT_DIR + '/runtime/')

options.parse_command_line(final=True)
