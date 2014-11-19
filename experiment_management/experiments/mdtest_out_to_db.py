#! /usr/bin/env python 
########################### mdtest_out_to_db.py ############################## 
#
# This program is a modified version of mdtest_wrapper.py.  It handles
# parsing of an mdtest run output that exist in a file (e.g. experiment_
# management runs of mdtest). The parsed output is formatted into a MySQL 
# insert command which is written to mdtest.sql_query in your home directory.
#
# To run this program:
# mdtest_out_to_db.py --file mdtest_output_file 
#
# Last modified:  11/19/2014
#
############################################################################

import getopt
import sys
import os
import array
import string
import time
import user
import MySQLdb as db
from optparse import OptionParser
import shutil

# database identifying variables
table = "mdtest"
host = "phpmyadmin"
db = "mpi_io_test_pro"
user = "cron"
passwd = "hpciopwd"

def main():
    
    # check for minimum number of arguments
    if (len(sys.argv) != 3):
        print "Your command needs to have one arguement:  --file"
        print "It should look something like this:"
        print "python mdtest_wrapper.py --file mdtest_output_file"
        sys.exit()

    command_line =" ".join(sys.argv)
    
    db_data = dict()
    initDictionary(db_data)
    # check for correct state and fix bad state
#    sanityCheck(db_data)

    # parse output from mdtest and put in db_data dictionary
    for a in sys.argv:
        if ( a == '--file'):
             index = sys.argv.index(a) + 1
             if (index < len(sys.argv)):
                out_file = sys.argv[index]
    file = open(out_file, "r")
    mdtest_output = file.read()

    parseOutput(mdtest_output, db_data)

    # insert results into database
    db_insert(db,db_data)



# initialize the values in the results dictionary
def initDictionary(db_data):

    # keys for output
    #db_data['user'] = None
    db_data['user'] = os.getenv('USER') 
    db_data['system'] = None
    db_data['date_ts'] = None

    # initialize mdtest parameters output
    db_data['collective_creates'] = None
    db_data['working_directory'] = None
    db_data['directories_only'] = None
    db_data['files_only'] = None
    db_data['first_task'] = None
    db_data['last_task'] = None
    db_data['iterations'] = None
    db_data['items'] = None
    db_data['items_per_dir'] = None
    db_data['nstride'] = None
    db_data['stride'] = None
    db_data['pre_delay'] = None
    db_data['remove_only'] = None
    db_data['shared_file'] = None
    db_data['time_unique_dir_overhead'] = None
    db_data['unique_dir_per_task'] = None
    db_data['write_bytes'] = None
    db_data['sync_file'] = None
    db_data['branch_factor'] = None
    db_data['depth'] = None
    db_data['random_stat'] = None
    db_data['no_barriers'] = None
    db_data['create_only'] = None
    db_data['leaf_level'] = None
    db_data['stat_only'] = None
    db_data['read_only'] = None
    db_data['read_bytes'] = None

    # initialize mdtest environment output
    db_data['mdtest_version'] = None
    db_data['num_tasks'] = None
    db_data['num_nodes'] = None
    db_data['path'] = None
    db_data['fs_size'] = None
    db_data['fs_used_pct'] = None
    db_data['inodes_size'] = None
    db_data['inodes_used_pct'] = None

    # initialize mdtest operations output
    db_data['dir_create_max'] = None
    db_data['dir_create_min'] = None
    db_data['dir_create_mean'] = None
    db_data['dir_create_stddev'] = None
    db_data['dir_stat_max'] = None
    db_data['dir_stat_min'] = None
    db_data['dir_stat_mean'] = None
    db_data['dir_stat_stddev'] = None
    db_data['dir_remove_max'] = None
    db_data['dir_remove_min'] = None
    db_data['dir_remove_mean'] = None
    db_data['dir_remove_stddev'] = None
    db_data['file_create_max'] = None
    db_data['file_create_min'] = None
    db_data['file_create_mean'] = None
    db_data['file_create_stddev'] = None
    db_data['file_stat_max'] = None
    db_data['file_stat_min'] = None
    db_data['file_stat_mean'] = None
    db_data['file_stat_stddev'] = None
    db_data['file_remove_max'] = None
    db_data['file_remove_min'] = None
    db_data['file_remove_mean'] = None
    db_data['file_remove_stddev'] = None
    db_data['tree_creation_max'] = None
    db_data['tree_creation_min'] = None
    db_data['tree_creation_mean'] = None
    db_data['tree_creation_stddev'] = None
    db_data['tree_removal_max'] = None
    db_data['tree_removal_min'] = None
    db_data['tree_removal_mean'] = None
    db_data['tree_removal_stddev'] = None

    # initialize system output
    db_data['mpihome'] = None
    db_data['mpihost'] = None
    db_data['mpi_version'] = None
    db_data['segment'] = None
    db_data['os_version'] = None
    db_data['yyyymmdd'] = None
    db_data['jobid'] = None
    db_data['host_list'] = None
    db_data['panfs'] = None
    db_data['panfs_srv'] = None
    db_data['panfs_type'] = None
    db_data['panfs_stripe'] = None
    db_data['panfs_width'] = None
    db_data['panfs_depth'] = None
    db_data['panfs_comps'] = None
    db_data['panfs_visit'] = None
    db_data['panfs_mnt'] = None
    db_data['panfs_threads'] = None
    db_data['ionodes'] = None
    db_data['num_ionodes'] = None
    db_data['procs_per_node'] = None


def getEnv(path_to_script, db_data):

    # run script and parse output
    if (path_to_script is not None and os.path.exists(path_to_script)):
        command = "%s %s" % (path_to_script, db_data['working_directory']) 
        p = os.popen(command)
        env_result = p.read()
        lines = env_result.splitlines()
        for line in lines:
            tokens = line.split()
            if (len(tokens) >= 2):
                if (tokens[0] == 'ionodes'):
                    db_data['ionodes'] = tokens[1]
                elif (tokens[0] == 'num_ionodes'):
                    db_data['num_ionodes'] = tokens[1]
                elif (tokens[0] == 'panfs_mnt'):
                    db_data['panfs_mnt'] = tokens[1]
                elif (tokens[0] == 'panfs_type'):
                    db_data['panfs_type'] = tokens[1]
                elif (tokens[0] == 'panfs_comps'):
                    db_data['panfs_comps'] = tokens[1]
                elif (tokens[0] == 'panfs_stripe'):
                    db_data['panfs_stripe'] = tokens[1]
                elif (tokens[0] == 'panfs_width'):
                    db_data['panfs_width'] = tokens[1]
                elif (tokens[0] == 'panfs_depth'):
                    db_data['panfs_depth'] = tokens[1]
                elif (tokens[0] == 'panfs_visit'):
                    db_data['panfs_visit'] = tokens[1]
                elif (tokens[0] == 'mpihome'):
                    db_data['mpihome'] = tokens[1]
                elif (tokens[0] == 'segment'):
                    db_data['segment'] = tokens[1]
                elif (tokens[0] == 'user'):
                    db_data['user'] = tokens[1]
                elif (tokens[0] == 'system'):
                    db_data['system'] = tokens[1]
                elif (tokens[0] == 'date_ts'):
                    db_data['date_ts'] = tokens[1]
                elif (tokens[0] == 'mpihost'):
                    db_data['mpihost'] = tokens[1]
                elif (tokens[0] == 'os_version'):
                    db_data['os_version'] = tokens[1]
                elif (tokens[0] == 'yyyymmdd'):
                    db_data['yyyymmdd'] = tokens[1]
                elif (tokens[0] == 'jobid'):
                    db_data['jobid'] = tokens[1]
                elif (tokens[0] == 'mpi_version'):
                    db_data['mpi_version'] = tokens[1]
                elif (tokens[0] == 'host_list'):
                    db_data['host_list'] = tokens[1]
                elif (tokens[0] == 'procs_per_node'):
                    db_data['procs_per_node'] = tokens[1]
                elif (tokens[0] == 'panfs_threads'):
                    db_data['panfs_threads'] = tokens[1]
                elif (tokens[0] == 'panfs'):
                    db_data['panfs'] = tokens[1]
                    for i in range(len(tokens)-2):
                        db_data['panfs'] += " " + tokens[i+2]


def fail(message):
    print message
    sys.exit()

# parse the parameters
def parseParams(argArray, db_data):

    # parameter parser
    parser = OptionParser()

    # add options to parser
    parser.add_option("-b", action="store", dest="branch_factor", type="int")
    parser.add_option("-B", action="store_const", dest="no_barriers", const=1)
    parser.add_option("-c", action="store_const", dest="collective_creates",
                      const=1)
    parser.add_option("-C", action="store_const", dest="create_only", const=1)
    parser.add_option("-d", action="store", dest="working_directory",
                      type="string")
    parser.add_option("-D", action="store_const", dest="directories_only", 
                      const=1)
    parser.add_option("-e", action="store", dest="read_bytes", type="int")
    parser.add_option("-E", action="store_const", dest="read_only", const=1)
    parser.add_option("-f", action="store", dest="first_task", type="int")
    parser.add_option("-F", action="store_const", dest="files_only", const=1)
    parser.add_option("-i", action="store", dest="iterations", type="int")
    parser.add_option("-I", action="store", dest="items_per_dir", type="int")
    parser.add_option("-l", action="store", dest="last_task", type="int")
    parser.add_option("-L", action="store_const", dest="leaf_only", const=1)
    parser.add_option("-n", action="store", dest="items", type="int")
    parser.add_option("-N", action="store", dest="nstride", type="int")
    parser.add_option("-p", action="store", dest="pre_delay", type="int")
    parser.add_option("-r", action="store_const", dest="remove_only", const=1)
    parser.add_option("-R", action="store_const", dest="junk", const=1)
    parser.add_option("-s", action="store", dest="stride", type="int")
    parser.add_option("-S", action="store_const", dest="shared_file", const=1)
    parser.add_option("-t", action="store_const", 
                      dest="time_unique_dir_overhead", const=1)
    parser.add_option("-T", action="store_const", dest="stat_only", const=1)
    parser.add_option("-u", action="store_const", dest="unique_dir_per_task",
                      const=1)
    parser.add_option("-v", action="count", dest="verbose")
    parser.add_option("-V", action="store", dest="verbose", type="int")
    parser.add_option("-w", action="store", dest="write_bytes", type="int")
    parser.add_option("-y", action="store_const", dest="sync_file", const=1)
    parser.add_option("-z", action="store", dest="depth", type="int")

    (options, args) = parser.parse_args(argArray)
    
    for k,v in vars(options).items():
        if db_data.has_key(k):
            db_data[k] = v



# check for correct state before running test
def sanityCheck(db_data):
    if ((db_data['create_only'] == 1) or (db_data['create_only'] is None and
        db_data['stat_only'] is None and db_data['remove_only'] is None)):
        if (db_data['working_directory'] is not None):
            path = '%s/#test-dir.0' % (db_data['working_directory'])
            if (os.path.exists(path)):
                for dir in  os.listdir(path):
                    temp = '%s/%s' % (path, dir)
                    print 'WRAPPER PERFORMING CLEAN-UP ON %s' % temp
                    shutil.rmtree(temp)



# parse mdtest output
def parseOutput(output, db_data):

    total_fs_size = 0
    free_fs_size = 0
    used_fs_pct = 0
    total_inodes = 0 
    free_inodes = 0 
    used_inodes_pct = 0 

    # parse output from mdtest and put in db_data dictionary
    lines = output.splitlines()
    for line in lines:
        if (line.startswith('-- started')):
            line_toks = line.split(' ')
            date_str = " ".join(line_toks[3:])
            date_time = time.strptime(date_str, "%m/%d/%Y %H:%M:%S --")
            epoch     = int(time.mktime(date_time));
            db_data['date_ts'] = epoch
            db_data['yyyymmdd'] = str(date_time.tm_year) + str(date_time.tm_mon) + str(date_time.tm_mday)
        if (line.startswith('mdtest')):
            line_toks = line.split(' ')
            db_data['mdtest_version'] = line_toks[0]
            first = True
            for l in line_toks:
                if (l.isdigit() and first):
                    db_data['num_tasks'] = l
                    first = False
                elif (l.isdigit()):
                    db_data['num_nodes'] = l
        # Because this code is no longer a wrapper, the command line used must be parsed here
        # The command line is parsed with a call to parseParams and
        # directory paths are parsed so that file system statistics can be gathered.
        elif (line.startswith('Command line used:')):
            line_toks = line.split(' ')
            command = " ".join(line_toks[3:])
            #args = " ".join(line_toks[4:])
            parseParams(line_toks[4:], db_data)
            db_data['command_line'] = command
            if (db_data['working_directory'] == None):
                path = os.path.abspath(line_toks[1])
                db_data['working_directory'] = os.path.dirname(path)
            # Multi volume/dir testing uses an "@" symbol to delimit paths
            # so check if multipaths are being used
            uniq_path=db_data['working_directory'].split('@')
            for dir_path in uniq_path:
                # get fs stats
                ### NOTE: this info could obtained by parsing output from mdtest
                ### but it's both easier and more accurate to do it here
                stats = os.statvfs(dir_path)

               # data blocks
                total_fs_size += stats.f_blocks * stats.f_bsize
                free_fs_size += stats.f_bfree * stats.f_bsize
                used_fs_pct += (1 - (float(free_fs_size)/float(total_fs_size))) * 100
                db_data['fs_size'] = total_fs_size
                db_data['fs_used_pct'] = used_fs_pct

               # inodes
                total_inodes += stats.f_files
                free_inodes += stats.f_ffree
                used_inodes_pct += (1 - (float(free_inodes)/float(total_inodes))) * 100
                db_data['inodes_size'] = total_inodes
                db_data['inodes_used_pct'] = used_inodes_pct

        elif (line.startswith('Path:')):
            line_toks = line.split(':')
            db_data['path'] = line_toks[1].strip()
        elif (line.startswith('random')):
            line_toks = line.split(':')
            db_data['random_stat'] = line_toks[1].strip()
        #elif (line.startswith('tree creation rate')):
        #    line_toks = line.split(':')
        #    db_data['tree_create'] = line_toks[1].strip()
        elif (line.startswith("   Directory creation:")):
            line_toks = line.split()
            length = len(line_toks)
            for i in range(length):
                if (i==(length-4)):
                    db_data['dir_create_max'] = line_toks[i]
                elif (i==(length-3)):
                    db_data['dir_create_min'] = line_toks[i]
                elif (i==(length-2)):
                    db_data['dir_create_mean'] = line_toks[i]
                elif (i==(length-1)):
                    db_data['dir_create_stddev'] = line_toks[i]
        elif (line.startswith("   Directory stat")):
            line_toks = line.split()
            length = len(line_toks)
            for i in range(length):
                if (i==(length-4)):
                    db_data['dir_stat_max'] = line_toks[i]
                elif (i==(length-3)):
                    db_data['dir_stat_min'] = line_toks[i]
                elif (i==(length-2)):
                    db_data['dir_stat_mean'] = line_toks[i]
                elif (i==(length-1)):
                    db_data['dir_stat_stddev'] = line_toks[i]
        elif (line.startswith("   Directory removal")):
            line_toks = line.split()
            length = len(line_toks)
            for i in range(length):
                if (i==(length-4)):
                    db_data['dir_remove_max'] = line_toks[i]
                elif (i==(length-3)):
                    db_data['dir_remove_min'] = line_toks[i]
                elif (i==(length-2)):
                    db_data['dir_remove_mean'] = line_toks[i]
                elif (i==(length-1)):
                    db_data['dir_remove_stddev'] = line_toks[i]
        elif (line.startswith("   File creation")):
            line_toks = line.split()
            length = len(line_toks)
            for i in range(length):
                if (i==(length-4)):
                    db_data['file_create_max'] = line_toks[i]
                elif (i==(length-3)):
                    db_data['file_create_min'] = line_toks[i]
                elif (i==(length-2)):
                    db_data['file_create_mean'] = line_toks[i]
                elif (i==(length-1)):
                    db_data['file_create_stddev'] = line_toks[i]
        elif (line.startswith("   File stat")):
            line_toks = line.split()
            length = len(line_toks)
            for i in range(length):
                if (i==(length-4)):
                    db_data['file_stat_max'] = line_toks[i]
                elif (i==(length-3)):
                    db_data['file_stat_min'] = line_toks[i]
                elif (i==(length-2)):
                    db_data['file_stat_mean'] = line_toks[i]
                elif (i==(length-1)):
                    db_data['file_stat_stddev'] = line_toks[i]
        elif (line.startswith("   File read")):
            line_toks = line.split()
            length = len(line_toks)
            for i in range(length):
                if (i==(length-4)):
                    db_data['file_read_max'] = line_toks[i]
                elif (i==(length-3)):
                    db_data['file_read_min'] = line_toks[i]
                elif (i==(length-2)):
                    db_data['file_read_mean'] = line_toks[i]
                elif (i==(length-1)):
                    db_data['file_read_stddev'] = line_toks[i]
        elif (line.startswith("   File removal")):
            line_toks = line.split()
            length = len(line_toks)
            for i in range(length):
                if (i==(length-4)):
                    db_data['file_remove_max'] = line_toks[i]
                elif (i==(length-3)):
                    db_data['file_remove_min'] = line_toks[i]
                elif (i==(length-2)):
                    db_data['file_remove_mean'] = line_toks[i]
                elif (i==(length-1)):
                    db_data['file_remove_stddev'] = line_toks[i]
        elif (line.startswith("   Tree creation")):
            line_toks = line.split()
            length = len(line_toks)
            for i in range(length):
                if (i==(length-4)):
                    db_data['tree_creation_max'] = line_toks[i]
                elif (i==(length-3)):
                    db_data['tree_creation__min'] = line_toks[i]
                elif (i==(length-2)):
                    db_data['tree_creation_mean'] = line_toks[i]
                elif (i==(length-1)):
                    db_data['tree_creation_stddev'] = line_toks[i]
        elif (line.startswith("   Tree removal")):
            line_toks = line.split()
            length = len(line_toks)
            for i in range(length):
                if (i==(length-4)):
                    db_data['tree_removal_max'] = line_toks[i]
                elif (i==(length-3)):
                    db_data['tree_removal__min'] = line_toks[i]
                elif (i==(length-2)):
                    db_data['tree_removal_mean'] = line_toks[i]
                elif (i==(length-1)):
                    db_data['tree_removal_stddev'] = line_toks[i]



# creates db insert query from db_data dictionary then executes query
def db_insert(dbconn, db_data):

    # create insert query
    query = "INSERT INTO mdtest ("

    count = 0

    # append column names to query
    for key in db_data.keys():
        if (db_data.get(key) != None):
            if (count == 1):
                query += ','
            count = 1
            query += key

    query += ") VALUES ('"
    count = 0

    # append values to query
    for value in db_data.values():
        if (value != None):
            if (count == 1):
                query += "','"
            count = 1
            query += str(value)

    query += "')"

    db_success=False
    try: 
        # connect to the database
        raise SystemError   # don't even bother, just dump to file
        conn = db.connect(host="phpmyadmin",db="mpi_io_test_pro",user="cron",
                          passwd="hpciopwd")
        cursor = conn.cursor()
    
        # execute the query
        cursor.execute(query)

        # close connection
        cursor.close()
        conn.close()
        
        print "Query inserted into database"
        db_success=True

    except:

        sql_file = os.getenv('HOME') + '/mdtest.sql_query'

        # if unable to connect to db, print query to file sql_query
        try:
            f = open(sql_file,'a')
        except:
            f = open(sql_file,'w')
        try:
            f.write(query + ';\n')
            f.close()
            print "Appended query to file: %s" % sql_file
            db_success=True
        except:
            print "Unable to append query to file: %s" % sql_file

    #finally:

    # when all else fails print query to standard out
    if db_success is False: print query
    




    
    
if __name__ == "__main__":
    main()


