#!/usr/bin/env python
#-*- coding:utf-8 -*-

try:
    from fuse import FUSE, FuseOSError, Operations, LoggingMixIn, fuse_get_context
except ImportError as ex:
    print('Failed to import fusepy library; install from github https://github.com/terencehonles/fusepy')
    exit(1)

from stat import S_IFDIR, S_IFREG
from sys import argv
from errno import *
from time import time
import os
from urlparse import urlparse
import logging
#import some packges
import GDBFS

class GDBFSfuse(LoggingMixIn, Operations):

    def __init__(self):
        #something
        self.nodes = 0



    def readdir(self, path, fh):
        return ['.', '..'] + GDBFS.stimulate_by_fuse(path)


    def getattr(self, path, fh=None):
        if path == '/' or GDBFS.is_dir(path):
            st = dict(st_mode=(S_IFDIR | 0755), st_nlink=2)
        else:
            # file = GDBFS.get_file(path)
            if len(GDBFS.Ndb.get_node_label(GDBFS.get_node_name(path)))!=0:
                filesize=0
                try:
                    filesize=GDBFS.get_file_length(path)
                except:
                    filesize=0

                st = dict(st_mode=(S_IFREG | 0644), st_size=filesize)
            else:
                raise FuseOSError(ENOENT)
        st['st_ctime'] = st['st_mtime'] = st['st_atime'] = time()
        st['st_uid'], st['st_gid'], pid = fuse_get_context()
        print "\n\nin getattr, path =",path,"\nst =", st
        return st

    def read(self, path, size, offset, fh):
        print "\n\nin fuse read, fh =", fh
        #file = GDBFS.get_file(path)
        #os_SEEK_SET = 0       # 这里由样例可查具体是 os.SEEK_SET 应该是mongoDB支持的，这里只是代替一写
        #if file.is_exist():
        data = GDBFS.Mdb.read(path,offset,size)
            #print "\n\nfuse read:",data
        return data
        #else:
        #    raise FuseOSError(ENOENT)

    def create(self, path, mode):
        print "\n\n\nin creat, path=",path,"\nend\n\n"
        return GDBFS.create_node_fuse('file', path)

    def mkdir(self, path, mode):
        print "\n\n\nin mkdir, path=",path,"\nend\n\n"
        GDBFS.create_node_fuse('category', path)

    def write(self, path, data, offset, fh):
        GDBFS.write(path,data,offset)
        #GDBFS.create_node_fuse('file', path)
        return len(data)

    def chmod(self, path, mode):
        return 0


    # Disable unused operations:
    access = None
    flush = None
    getxattr = None
    listxattr = None
    open = None
    opendir = None
    release = None
    releasedir = None
    statfs = None


def show_usage():
    print('''
usage: %s [<mountpoint> 
    ''' % argv[0])
    exit(1)

if __name__ == '__main__':
    argc = len(argv)
    if argc != 2:
        show_usage()
        exit(1)

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(GDBFSfuse(), argv[1], foreground=True)