from __future__ import absolute_import, print_function
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


@reg
def sizeimage(prog, sys_args):
    '''chagne png size'''
    from PIL import Image
    import argparse
    import time
    import os
    parser = argparse.ArgumentParser(prog=prog, add_help=True)
    parser.add_argument('-o', '--output', help='the output file or template, support variable: {src}/{name}/{dir}/{format}', type=str, required=True)
    parser.add_argument('-s', '--size', help='the output size', type=str, required=True)
    parser.add_argument('file', help='the input files', default=[], type=str, nargs='*')
    args = parser.parse_args(sys_args)
    w, h = [int(i) for i in args.size.split('x')]
    for src in args.file:
        if '{' in args.output:
            bn = os.path.basename(src)
            bns = bn.split('.')
            name = '.'.join(bns[0:-1])
            format = bns[-1] if len(bns) >= 2 else ''
            dirname = os.path.dirname(src)
            dst = args.output \
                .replace('{src}', src) \
                .replace('{name}', name) \
                .replace('{dir}', dirname) \
                .replace('{format}', format) \
                #
        else:
            dst = args.output
        img = Image.open(src)
        rw, rh = img.size
        print('%s(%dx%d)->%s(%dx%d)...' % (src, rw, rh, dst, w, h), end=' ', flush=True)
        st = int(time.time() * 1000)
        if img.mode == 'RGBA' and not dst.upper().endswith('png'):
            img = img.convert('RGB')
        if rw != w or rh != h:
            nimg = img.resize((w, h), )
            nimg.save(dst)
            print('ok', end=' ')
        else:
            img.save(dst)
            print('ignore', end=' ')
        print('%sms' % (int(time.time() * 1000) - st))


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
