# -*- coding: UTF-8 -*
'''
Created on 2021-04-16
'''
from __future__ import print_function

try:
    from importlib import reload
except:
    pass


def walk_class(clz):
    '''wall all subclass of clz'''
    yield clz
    for sm in clz.__subclasses__():
        for nclz in walk_class(sm):
            yield nclz


class Progress(object):
    '''show progress for long time task'''
    progress_interval = 5
    time_interval = 2
    progress_template = '{title}...{progres} Finish:{finish} Spent:{spent} Speed:{speed}/s Left:{left} Status:{status}'
    finish_template = '{title} Finished Spent:{spent}'

    def __init__(self, title='Runing', total=0, **kwargs):
        self.total = total
        self.title = title
        self.__dict__.update(kwargs)

    def __enter__(self):
        self.enter()
        return self

    def enter(self):
        import time
        self.count = 0
        self.lasttime = time.time()
        self.lastprogs = 0
        self.start = time.time()
        print('%s...' % self.title)

    def _time_str(self, sec):
        if sec > 3600:
            return '%dh%02dm%02ds' % (int(sec / 3600), int((sec % 3600) / 60), int(sec % 60))
        elif sec > 60:
            return '%dm%02ds' % (int(sec / 60), int(sec % 60))
        elif sec > 3:
            return '%ds' % int(sec)
        else:
            return '%dms' % int(sec * 1000)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit()

    def exit(self):
        import time
        self.end = time.time()
        print(self.finish_template.format(title=self.title, spent=self._time_str(self.end - self.start)))

    def feed(self, step=1, count=None, status=''):
        import time
        if count != None:
            self.count = count
        else:
            self.count += step
        p = int(self.count * 100 / self.total) if self.total else self.count
        t = time.time()
        if (p - self.lastprogs) >= self.progress_interval or (t - self.lasttime) > self.time_interval:
            spent = t - self.start
            speed = int(self.count / max(spent, 0.01) + 0.5)
            left = spent * self.total / self.count - spent
            print(self.progress_template.format(
                title=self.title,
                progres='%3d%%' % p if self.total else '',
                finish='%d/%d' % (self.count, self.total) if self.total else str(self.count),
                spent=self._time_str(spent),
                speed=speed,
                left=self._time_str(left) if self.total else '?',
                status=status))
            self.lastprogs = p
            self.lasttime = t


class Feeder(object):
    '''自动分割任务，用于将频繁调用简化，在一定的容量内尽可能的减少函数调用
    fd = Feeder(func, 10)   # 创建一个容量为10的分割器
    fd.feed(d1)
    fd.feed(d2)
    ...
    fd.feed(d10)    # 满10个数据，此时会自动调用方法func([d1, d2, .., d10])
    # 使用with上下文能够让代码执行完成之后自动将剩余未被调用的数据进行func函数调用
    '''

    def __init__(self, func, capacity=100):
        self.func = func
        self.capacity = capacity
        self.datas = []
        self.total = 0

    def __enter__(self):
        self.enter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit()

    def _do_func(self):
        if not self.datas:
            return
        rd = self.datas
        self.total += len(rd)
        self.func(rd)
        self.datas = []

    def feed(self, data):
        self.datas.append(data)
        if len(self.datas) >= self.capacity:
            self._do_func()

    def enter(self):
        self.total = 0

    def exit(self):
        if self.datas:
            self._do_func()


class FilesWatcher(object):
    '''to watch files, and get changed'''

    def __init__(self, files=None):
        if files == None:
            files = []
        self.files = files
        self.file_map = {}
        for f in self.files:
            self.add_file(f)

    def add_file(self, file):
        import os
        if file not in self.file_map:
            if not os.path.exists(file):
                self.file_map[file] = 0
            else:
                self.file_map[file] = os.path.getmtime(file)

    def get_changed(self):
        '''get changed files'''
        import os
        rs = []
        for f, t in self.file_map.items():
            if not os.path.exists(f):
                continue
            nt = os.path.getmtime(f)
            if t != nt:
                self.file_map[f] = nt
                rs.append(f)
        return rs


class ModulesWatcher(object):
    '''to watch modules, and reload module when module changed.'''

    def __init__(self, modules=None):
        if modules == None:
            modules = []
        self.module_map = {}
        self.files_watcher = FilesWatcher()
        for m in modules:
            self.add_module(m)

    def add_module(self, module):
        f = module.__file__
        if f not in self.module_map:
            self.files_watcher.add_file(f)
            self.module_map[f] = set()
        self.module_map[f].add(module)

    def get_changed(self):
        '''get changed modules'''
        fs = self.files_watcher.get_changed()
        mds = set()
        for f in fs:
            for m in self.module_map[f]:
                mds.add(m)
        return mds

    def auto_reload(self):
        '''reload module if it changed'''
        mds = self.get_changed()
        if mds:
            for m in mds:
                try:
                    reload(m)
                except:
                    import traceback
                    traceback.print_exc()
        return mds

def make_tcp_proxy(port, target_ip, target_port, verbose=False):
    import socket, select
    server_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 绑定本地地址和端口
    server_addr = ('', port)
    server_fd.bind(server_addr)
    # 开始监听
    server_fd.listen(100)
    def print_verbose(msg):
        if verbose:
            print(msg)
    print("Starting %s<->%s:%s ..." % (port, target_ip, target_port))
    client_target_map = {}
    target_addr = (target_ip, target_port)
    target_title = '%s:%s' % (target_ip, target_port)
    running = True
    while running:
        # 使用select监控所有文件描述符
        fds = list(client_target_map.keys()) + [server_fd]
        readfds, _, _ = select.select(fds, [], [], 1)
        for fd in readfds:
            try:
                if fd == server_fd:
                    # 接受新的客户端连接
                    client_fd, client_addr = server_fd.accept()
                    client_title = '%s:%s' % client_addr
                    print_verbose("New client %s connected" % client_title)
                    target_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    target_addr = (target_ip, target_port)
                    try:
                        target_fd.connect(target_addr)
                    except Exception as e:
                        print_verbose("Error connecting to target: %s" % e)
                        import traceback
                        traceback.print_exc()
                        client_fd.close()
                        target_fd.close()
                        continue
                    client_target_map[client_fd] = dict(fd=target_fd, title=target_title, bytes=0, tag='client')
                    client_target_map[target_fd] = dict(fd=client_fd, title=client_title, bytes=0, tag='target')
                    print_verbose("Tunnect %s<->%s connected" % (client_title, target_title))
                elif fd in client_target_map:
                    # 读取客户端发送的数据
                    try:
                        data = fd.recv(1500)
                    except:
                        data = ''
                    fd2 = client_target_map[fd]['fd']
                    if not data:
                        fd.close()
                        fd2.close()
                        d1 = client_target_map[fd]
                        d2 = client_target_map[fd2]
                        ctd, tgd = (d1, d2) if d1['tag'] == 'client' else (d2, d1)
                        tuntitle = '%s<->%s' % (ctd['title'], tgd['title'])
                        print_verbose("Tunnel %s disconnected, send=%d recv=%d" % (tuntitle, ctd['bytes'], tgd['bytes']))
                        del client_target_map[fd]
                        del client_target_map[fd2]
                    else:
                        client_target_map[fd]['bytes'] += len(data)
                        fd2.send(data)
            except Exception as e:
                import traceback
                traceback.print_exc()
    return 0