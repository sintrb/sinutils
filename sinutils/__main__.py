from __future__ import absolute_import
from collections import OrderedDict

cmdmap = OrderedDict()


def reg(func):
    cmdmap[func.__name__] = func
    return func


@reg
def watch(prog, sys_args):
    '''watch file change'''
    from sinutils import FilesWatcher
    import argparse
    import time
    import os
    parser = argparse.ArgumentParser(prog=prog, add_help=True)
    parser.add_argument('-f', '--file', help='the file will be watch', type=str, nargs='+', required=True)
    parser.add_argument('-i', '--interval', help='the time(seconds) interval to check, default is 1', type=int, default=1, required=False)
    parser.add_argument('-t', '--timeout', help='the max time(seconds) to check wait, 0(default) is wait forever', type=int, default=0, required=False)
    parser.add_argument('-e', '--execute', help='the system command will be run, "{f}" will replace with file', type=str, required=False)
    args = parser.parse_args(sys_args)
    watch = FilesWatcher(files=args.file)
    untiltime = (int(time.time()) + args.timeout) if args.timeout else 0
    while True:
        for i in watch.get_changed():
            if args.execute:
                # run
                os.system(args.execute.replace('{f}', i))
            else:
                # just print
                print(i)
        time.sleep(min(args.interval, 0.1))
        if untiltime and (time.time() > untiltime):
            break


def print_cmd_error(cmd):
    if not cmd:
        sys.stderr.write('need command!\n')
    else:
        sys.stderr.write('unknow command:%s\n' % cmd)
    sys.stderr.write('useage commands: %s\n' % (
        '/'.join(cmdmap.keys())
    ))


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print_cmd_error(None)
    else:
        cmd = sys.argv[1]
        if cmd not in cmdmap:
            print_cmd_error(cmd)
        else:
            prog = 'python -m sinutils %s' % cmd
            cmdmap[cmd](cmd, sys.argv[2:])
