import util
import json


# used to locally retrieve a package
# name is the raw code identifier (ie http.client or compiler.parser)
def get(name):
    # __application__ is an alias for build_file
    # loads util.build_file
    if name == '__application__':
        with open(util.build_file) as bf:
            data = bf.read()
        return data, '/'.join(util.build_file.split('/')[:-1])
    # open the package index
    with open(util.SOURCE_DIR + '/lib/package_index.json') as file:
        index = json.load(file)
    # split name by .
    name_list = name.split('.')
    # if the beginning of the name is in the package index (suffixes ignored)
    # applies for names such as http.client (would find package http)
    if name_list[0] in index:
        # find the raw path to package directory
        # combine it with full source directory path to prevent path ambiguity
        pkg_path = util.SOURCE_DIR + '/lib/packages/' + index[name_list[0]]
        # if the only path is to the main directory, load the main package file (__index__.sy)
        if len(name_list) == 1:
            with open(pkg_path + '/__index__.sy') as pkg_file:
                data = pkg_file.read()
            # only return the raw path to the package
            return data, pkg_path
        # if sub paths or sub files are accessed
        else:
            # get the final file name
            file_name = name_list.pop()
            # if there is full sub path and not just a sub file
            if len(name_list[1:]) > 0:
                # create a string sub path to follow
                # NOTE the .. syntax is NOT acceptable here
                # it is assumed that there should be no necessity to traverse the inward AND outward as
                # user begins in the parent directory
                str_path = '/'.join(name_list[1:])
                # synthesize full path from the package path, the sub path, and finally the sub file path
                with open(pkg_path + '/%s/%s.sy' % (str_path, file_name)) as pkg_file:
                    data = pkg_file.read()
                # return path only combines package path and sub path ignoring sub file (for chdir)
                return data, pkg_path + '/' + str_path
            # if it is just a sub file
            else:
                with open(pkg_path + '/%s.sy') as pkg_file:
                    data = pkg_file.read()
                # still return raw package path as it is just a sub file
                return data, pkg_path
    # if package not in package index, interpret as literal directory
    # where . = /  and .. = ../
    else:
        # file name is end of the split name
        # for example, in tests.test1, test1(.sy) is the file name
        file_name = name_list.pop()
        # convert ..upper_path to ../upper_path
        for i in range(len(name_list)):
            if name_list[i] == '':
                name_list[i] = '..'
        # if there is a traversable directory path, follow it
        if len(name_list) > 0:
            path = '/'.join(name_list) + '/%s.sy' % file_name
            with open(path) as source_file:
                data = source_file.read()
            return data, '/'.join(name_list)
        # otherwise just load straight for source filename
        else:
            with open(file_name + '.sy') as source_file:
                data = source_file.read()
            # None means no path needs to be changed to
            return data, None
