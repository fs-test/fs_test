#! /usr/bin/env python

########################### ior_out_to_db.py ##############################
#
# This program is a modified version of ior_wrapper.py.  It handles
# parsing of an ior run output that exist in a file (e.g. experiment_
# management runs of ior). The parsed output is formatted into a MySQL 
# insert command which is written to ior.sql_query in your home directory.
#
# To run this program:
# ior_out_to_db.py --file ior_output_file --db_file_path path 
#
# Last modified:  12/2/2014
############################################################################

import getopt
import sys
import os
import array
import string
import time
import user
import re
import MySQLdb as db
from optparse import OptionParser

import subprocess

# database identifying variables
table = "ior"
host = "phpmyadmin"
db = "mpi_io_test_pro"
user = "cron"
passwd = "hpciopwd"


def main():
    
    # check for minimum number of arguments
    if (len(sys.argv) != 5):
        print "Your command needs to have two arguements"
        print "It should look something like this:"
        print "python ior_out_to_db.py --file ior_output_file --db_file_path path"
        sys.exit()

    #  look for arguments
    for a in sys.argv:
        if ( a == '--file'):
             index = sys.argv.index(a) + 1
             if (index < len(sys.argv)):
                out_file = sys.argv[index]
        if ( a == '--db_file_path'):
             index = sys.argv.index(a) + 1
             if (index < len(sys.argv)):
                db_path = sys.argv[index]

    # open the output file for reading
    file = open(out_file, "r")
    ior_output = file.read()

    # [re-]initialize dictionary, before parsing output
    db_data = dict()
    #initDictionary(db_data, description)
    initDictionary(db_data)

    parseOutput(ior_output, db_data)

    db_insert(db, db_data, db_path)

    # same data, formatted for gnuplot this time
    #if (not db_data['run_time_error']):
    #    gnuplot_insert(db_data)
    #    gnuplot_commands(db_data)


# initialize the values in the results dictionary
#def initDictionary(db_data, description):
def initDictionary(db_data):
#    global walltime

    # keys
    #
    # NOTE: These three keys make up the primary-key for DBMS rows in table
    #       'ior' in the 'mpi_io_test_pro' database, at LANL.  Therefore,
    #       they must be given values, if parsed experiment-results are to
    #       be accessioned into the DB.  <date_ts> and <system> can be
    #       parsed from IOR output, but <user> isn't going to get any
    #       easier to conjure up than it is right now.
    db_data['user'] = os.getenv('USER')
    db_data['mpihost'] = os.getenv('MY_MPI_HOST')
    db_data['system'] = None
    db_data['date_ts'] = None

#    db_data['description'] = description

    # initialize ior parameters output
    db_data['test_number'] = None
    db_data['api'] = None                        # 
    db_data['block_size'] = None                 # 
    db_data['use_o_direct'] = None
    db_data['collective'] = None
    db_data['reorder_tasks'] = None
    db_data['task_per_node_offset'] = None
    db_data['reorder_tasks_random'] = None
    db_data['random_seed'] = None
    db_data['inter_test_delay'] = None
    db_data['deadline_for_stonewalling'] = None
    db_data['fsync_after_write'] = None
    db_data['fsync_after_close'] = None
    db_data['use_existing_test_file'] = None
    db_data['script_file'] = None
    db_data['file_per_proc'] = None              # access was N:1? value is {0,1}
    db_data['intra_test_barriers'] = None
    db_data['set_timestamp_signature'] = None
    db_data['show_help'] = None
    db_data['show_hints'] = None
    db_data['repetitions'] = None
    db_data['individual_data_sets'] = None
    db_data['outlier_threshold'] = None
    db_data['set_alignment'] = None
    db_data['keep_file'] = None
    db_data['keep_file_with_error'] = None
    db_data['store_file_offset'] = None
    db_data['multi_file'] = None
    db_data['no_fill'] = None
    db_data['command_line'] = None
    db_data['num_tasks'] = None                  # 
    db_data['test_file'] = None
    db_data['ior_directives'] = None
    db_data['preallocate'] = None
    db_data['use_shared_file_pointer'] = None
    db_data['quit_on_error'] = None
    db_data['read_file'] = None
    db_data['check_read'] = None
    db_data['segment_count'] = None              # 
    db_data['use_strided_datatype'] = None
    db_data['transfer_size'] = None              # 
    db_data['max_time_duration'] = None
    db_data['unique_dir'] = None
    db_data['hints_file_name'] = None
    db_data['verbose'] = None
    db_data['use_file_view'] = None
    db_data['write_file'] = None
    db_data['check_write'] = None
    db_data['single_transfer_attempt'] = None
    db_data['random_offset'] = None
    
    # initialize ior operations output
    db_data['write_data_rate_max'] = None
    db_data['write_data_rate_min'] = None
    db_data['write_data_rate_mean'] = None
    db_data['write_data_rate_std_dev'] = None
    db_data['write_op_rate_max'] = None
    db_data['write_op_rate_min'] = None
    db_data['write_op_rate_mean'] = None
    db_data['write_op_rate_std_dev'] = None
    db_data['write_time_mean'] = None
    db_data['read_data_rate_max'] = None
    db_data['read_data_rate_min'] = None
    db_data['read_data_rate_mean'] = None
    db_data['read_data_rate_std_dev'] = None
    db_data['read_op_rate_max'] = None
    db_data['read_op_rate_min'] = None
    db_data['read_op_rate_mean'] = None
    db_data['read_op_rate_std_dev'] = None
    db_data['read_time_mean'] = None
    db_data['num_io_procs'] = None             # (Cf. "num_tasks")
    db_data['num_io_procs_per_node'] = None    # (Cf. "procs_per_node")
    db_data['files_per_proc'] = None           # (Cf. "file_per_proc")
    db_data['node_offset_for_reads'] = None
    db_data['segments_per_file'] = None
    db_data['aggregate_size'] = None

    # initialize system output
    db_data['mpihome'] = None
    #db_data['mpihost'] = None
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
    db_data['procs_per_node'] = None     # "processors"? or "processes"? (assuming latter)
#    db_data['walltime'] = walltime
    db_data['run_time_error'] = None



def getEnv(path_to_script, db_data):

    #TODO: move this to the end (after param and output parse
    # run env_to_db and parse output
    if (path_to_script is not None and os.path.exists(path_to_script)):
        #TODO: this should use target 
        command = "%s %s" % (path_to_script, os.getcwd())
        print "getENV: command = '" + command + "'"
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



# fail wrapper to print error and exit
def fail(message):
    print message
    sys.exit()


# --- parse ior output
#
# NOTE: How did this ever work?  There's no variable named 'canStart'.
#       Also the parsing of output was incomplete.  Tightened this
#       up, and extended the parser.
#
#       Here's some output from IOR:
#
#
#    -----------------------------------------------------------------
#    IOR-3.0.1: MPI Coordinated Test of Parallel I/O
#    
#    Began: Wed Oct 22 15:21:46 2014
#    Command line used: /users/jti/projects/ecs_hobo/ior/installed/bin/ior -a S3 -b 33554432 -i 1 -o experiment__2014_10_22__15_21_44.out -s 1 -t 33554432
#    Machine: Linux rrz103.localdomain
#    
#    Test 0 started: Wed Oct 22 15:21:46 2014
#    Summary:
#            api                = S3
#            test filename      = experiment__2014_10_22__15_21_44.out
#            access             = single-shared-file
#            ordering in a file = sequential offsets
#            ordering inter file= no tasks offsets
#            clients            = 16 (4 per node)
#            repetitions        = 1
#            xfersize           = 32 MiB
#            blocksize          = 32 MiB
#            aggregate filesize = 512 MiB
#    
#    access    bw(MiB/s)  block(KiB) xfer(KiB)  open(s)    wr/rd(s)   close(s)   total(s)   iter
#    ------    ---------  ---------- ---------  --------   --------   --------   --------   ----
#    write     324.02     32768      32768      0.151023   1.28       0.853845   1.58       0   
#    read      24.03      32768      32768      0.028845   21.30      15.86      21.30      0   
#    remove    -          -          -          -          -          -          0.004515   0   
#    
#    Max Write: 324.02 MiB/sec (339.76 MB/sec)
#    Max Read:  24.03 MiB/sec (25.20 MB/sec)
#    
#    Summary of all tests:
#    Operation   Max(MiB)   Min(MiB)  Mean(MiB)     StdDev    Mean(s) Test# #Tasks tPN reps fPP reord reordoff reordrand seed segcnt blksiz xsize aggsize API RefNum
#    write         324.02     324.02     324.02       0.00    1.58014 0 16 4 1 0 0 1 0 0 1 33554432 33554432 536870912 S3 0
#    read           24.03      24.03      24.03       0.00   21.30473 0 16 4 1 0 0 1 0 0 1 33554432 33554432 536870912 S3 0
#    
#    Finished: Wed Oct 22 15:22:09 2014


def parseUnits(token):
    units = [ 'bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB' ];
    mult = 1
    for u in units:
        if token == u:
            return mult
        mult *= 1024;

    errmsg = "Couldn't parse units from token '" + token + "'"
    fail(errmsg)


def parseOutput(output, db_data):
    lines = output.splitlines()
    canParsePrelim  = True
    canParseSummary = False
    canParseAccess  = False
    canParseOps     = False
    finished        = False
    parseAccessBWOnly = False

    for line in lines:

        # recognize run-time errors and punt
        if (line.startswith('ERR')
            or line.startswith('ior ERROR')  # iordef.h
            or line.startswith('PID:')
            or line.startswith('mpirun has exited')
            or (line.find('] FAILED comparison') >= 0)):

            # abandon further parsing
            db_data['run_time_error'] = 1
            break


        line = line.lstrip()

        # parsing initial part of output, before "Summary"
        if canParsePrelim:
            tokens = line.split()

            if (len(tokens) == 0):
                continue
            elif (tokens[0] == 'Command'):
                command = " ".join(tokens[3:]) 
                db_data['command_line'] = command
                # since command line established here, go ahead and parse it now
                parseParams(tokens[4:], db_data);
            elif (tokens[0] == 'Summary:'):
                canParsePrelim  = False
                canParseSummary = True

            elif (tokens[0] == 'Began:'):
                date_str  = " ".join(tokens[1:])
                date_time = time.strptime(date_str, "%a %b %d %H:%M:%S %Y")
                epoch     = int(time.mktime(date_time));
                db_data['date_ts'] = epoch
                if (date_time.tm_mon < 10 or date_time.tm_mday < 10 ):    
                    if (date_time.tm_mon < 10 and date_time.tm_mday < 10 ):    
                        db_data['yyyymmdd'] = str(date_time.tm_year) + '0' + str(date_time.tm_mon) + '0' + str(date_time.tm_mday)
                    elif (date_time.tm_mon < 10): 
                        db_data['yyyymmdd'] = str(date_time.tm_year) + '0' + str(date_time.tm_mon) + str(date_time.tm_mday)
                    elif (date_time.tm_mday < 10 ):
                        db_data['yyyymmdd'] = str(date_time.tm_year) + str(date_time.tm_mon) + '0' + str(date_time.tm_mday)
                else:  
                    db_data['yyyymmdd'] = str(date_time.tm_year) + str(date_time.tm_mon) + str(date_time.tm_mday)
            elif (tokens[0] == 'Machine:'):
                db_data['system'] = tokens[2]

            elif (tokens[0] == 'Test'):
                db_data['test_number'] = int(tokens[1])


        # parsing "Summary:" output-section
        elif canParseSummary:
            tokens = line.split()

            if (len(tokens) == 0):
                canParseSummary = False
                canParseAccess = True

            # in case "access" section is not always present ...
            elif (line.startswith('Operation')):
                canParseSummary = False
                canParseOps = True

            elif (tokens[0] == 'api'):
                db_data['api'] = tokens[2]

            elif (tokens[0] == 'test' and tokens[1] == 'filename'):
                db_data['test_file'] = tokens[3]

            # Comment out the following since they are populated later
            #elif (tokens[0] == 'xfersize'):
            #    db_data['transfer_size'] = int(tokens[2]) * parseUnits(tokens[3])

            #elif (tokens[0] == 'blocksize'):
            #    db_data['block_size'] = float(tokens[2]) * parseUnits(tokens[3])

            #elif (tokens[0] == 'aggregate'):
            #    db_data['aggregate_size'] = float(tokens[3]) * parseUnits(tokens[4])
            elif (tokens[0] == 'Using' and tokens[1] == 'stonewalling'):
                db_data['deadline_for_stonewalling'] = tokens[3]



        # parsing "access" output-section (elapsed times)
        # NOTE: This is also where errors will happen
        elif canParseAccess:
            if re.match("WARNING: Expected aggregate file size",line):
               parseAccessBWOnly = True 
            elif re.match("WARNING: Using actual aggregate bytes moved", line):
                line_tokens = line.split()
                if not (db_data['aggregate_size']):
                    db_data['aggregate_size'] = int(line_tokens[7][0:-1])
            elif (line.startswith('write') and parseAccessBWOnly):
                line_tokens = line.split()
                db_data['write_data_rate_mean'] = line_tokens[1]
            elif (line.startswith('write')):
                line_tokens = line.split()
                db_data['write_open_time'] = line_tokens[4]
                db_data['write_wrrd_time'] = line_tokens[5]
                db_data['write_close_time'] = line_tokens[6]
            elif (line.startswith('read')):
                line_tokens = line.split()
                db_data['read_open_time'] = line_tokens[4]
                db_data['read_wrrd_time'] = line_tokens[5]
                db_data['read_close_time'] = line_tokens[6]

            # TBD ...
            if (line.startswith('Operation')):
                canParseAccess = False
                canParseOps = True


        # parsing "Operation" output-section ("Summary of all tests:")
        #
        # NOTE: block_size, xfer_size, and aggregate_size may supercede values parsed
        #       from summary-section.  The values here are given more precisely.
        elif (canParseOps):
            if (line.startswith('write')):
                line_tokens = line.split()
                if ( not parseAccessBWOnly):
                    db_data['write_data_rate_max'] = line_tokens[1]
                    db_data['write_data_rate_min'] = line_tokens[2]
                    db_data['write_data_rate_mean'] = line_tokens[3]
                    db_data['write_data_rate_std_dev'] = line_tokens[4]
                    db_data['write_time_mean'] = line_tokens[5]
                    db_data['aggregate_size'] = line_tokens[18]  # see "Summary:"

                db_data['num_tasks'] = line_tokens[7]
                db_data['procs_per_node'] = line_tokens[8] # WARNING: probly sposed to be processors

                db_data['file_per_proc'] = line_tokens[10]

                db_data['segment_count'] = line_tokens[15]
                db_data['block_size'] = line_tokens[16]      # see "Summary:"
                db_data['transfer_size'] = line_tokens[17]   # see "Summary:"
                #db_data['aggregate_size'] = line_tokens[18]  # see "Summary:"
                
            elif (line.startswith('read')):
                line_tokens = line.split()
                db_data['read_data_rate_max'] = line_tokens[1]
                db_data['read_data_rate_min'] = line_tokens[2]
                db_data['read_data_rate_mean'] = line_tokens[3]
                db_data['read_data_rate_std_dev'] = line_tokens[4]
                db_data['read_time_mean'] = line_tokens[5]

                db_data['num_tasks'] = line_tokens[7]
                db_data['procs_per_node'] = line_tokens[8] # WARNING: probly sposed to be processors

                db_data['file_per_proc'] = line_tokens[10]

                db_data['segment_count'] = line_tokens[15]
                db_data['block_size'] = line_tokens[16]      # see "Summary:"
                db_data['transfer_size'] = line_tokens[17]   # see "Summary:"
                if ( not parseAccessBWOnly):
                    db_data['aggregate_size'] = line_tokens[18]  # see "Summary:"

            elif (line.startswith('Finished')):
                finished = True

    if (not finished):
        db_data['run_time_error'] = 1



# parse the parameters
def parseParams(argArray, db_data):

    # parameter parser
    parser = OptionParser()

    # add options to parser
    parser.add_option("-A", action="store", dest="test_number", type="int")
    parser.add_option("-a", action="store", dest="api", type="string")
    #TODO: convert string to int (e.g. 1k => 1024)
    # block size is a string because of k,m,g unit designation possibility
    # need to convert back to integer but currently, output overwrites these
    # values anyway.  
    parser.add_option("-b", action="store", dest="block_size", type="string")
    parser.add_option("-B", action="store_const", dest="use_o_direct",
                      const=1)
    parser.add_option("-c", action="store_const", dest="collective",
                      const=1)
    parser.add_option("-C", action="store_const", dest="reorder_tasks",
                      const=1)
    parser.add_option("-Q", action="store", dest="task_per_node_offset",
                      type="int")
    parser.add_option("-Z", action="store_const", dest="reorder_tasks_random",
                      const=1)
    parser.add_option("-X", action="store", dest="random_seed",
                      type="int")
    parser.add_option("-d", action="store", dest="inter_test_delay",
                      type="int")
    parser.add_option("-D", action="store", dest="deadline_for_stonewalling",
                      type="int")
    parser.add_option("-Y", action="store_const", dest="fsync_after_write",
                      const=1)
    parser.add_option("-e", action="store_const", dest="fsync_after_close",
                      const=1)
    parser.add_option("-E", action="store_const",
                      dest="use_existing_test_file", const=1)
    parser.add_option("-f", action="store", dest="script_file", type="string")
    parser.add_option("-F", action="store_const", dest="file_per_proc",
                      const=1)
    parser.add_option("-g", action="store_const", dest="intra_test_barriers",
                      const=1)
    parser.add_option("-G", action="store", dest="set_timestamp_signature",
                      type="int")
    '''TODO: figure out what to do with -h option
    parser.add_option("-h", action="store_const", dest="show_help",
                      const=1)'''
    parser.add_option("-H", action="store_const", dest="show_hints",
                      const=1)
    parser.add_option("-i", action="store", dest="repetitions", type="int")
    parser.add_option("-I", action="store_const", dest="individual_data_sets",
                      const=1)
    parser.add_option("-k", action="store_const", dest="keep_file",
                      const=1)
    parser.add_option("-K", action="store_const", dest="keep_file_with_error",
                      const=1)
    parser.add_option("-l", action="store_const", dest="store_file_offset",
                      const=1)
    parser.add_option("-m", action="store_const", dest="multi_file",
                      const=1)
    parser.add_option("-n", action="store_const", dest="no_fill",
                      const=1)
    parser.add_option("-N", action="store", dest="num_tasks", type="int")
    parser.add_option("-o", action="store", dest="test_file", type="string")
    parser.add_option("-O", action="store", dest="ior_directives",
                      type="string")
    parser.add_option("-p", action="store_const", dest="preallocate",
                      const=1)
    parser.add_option("-P", action="store_const",
                      dest="use_shared_file_pointer", const=1)
    parser.add_option("-q", action="store_const", dest="quit_on_error",
                      const=1)
    parser.add_option("-r", action="store_const", dest="read_file",
                      const=1)
    parser.add_option("-R", action="store_const", dest="check_read",
                      const=1)
    parser.add_option("-s", action="store", dest="segment_count", type="int")
    parser.add_option("-S", action="store_const", dest="use_strided_data_type",
                      const=1)
    # transfer size is a string because of k,m,g unit designation possibility
    # need to convert back to integer but currently, output overwrites these
    # values anyway.  
    parser.add_option("-t", action="store", dest="transfer_size", type="string")
    parser.add_option("-T", action="store", dest="max_time_duration",
                      type="int")
    parser.add_option("-u", action="store_const", dest="unique_dir",
                      const=1)
    parser.add_option("-U", action="store", dest="hints_file_name",
                      type="string")
    parser.add_option("-v", action="store_const", dest="verbose",
                      const=1)
    parser.add_option("-V", action="store_const", dest="use_file_view",
                      const=1)
    parser.add_option("-w", action="store_const", dest="write_file",
                      const=1)
    parser.add_option("-W", action="store_const",
                      dest="check_write", const=1)
    parser.add_option("-x", action="store_const",
                      dest="single_transfer_attempt", const=1)
    parser.add_option("-z", action="store_const", dest="random_offset",
                      const=1)

    (options, args) = parser.parse_args(argArray)

    for k,v in vars(options).items():
        if db_data.has_key(k):
            db_data[k] = v
            #print k + "\t" + str(db_data[k])



# creates db insert query from db_data dictionary
# then executes query
def db_insert(dbconn, db_data, db_path):

    # create insert query
    query = "INSERT INTO " + table + " ("

    count = 0

    #temporary debug info
    for key in sorted(db_data.keys()):
        flag = ''
        if ((key == "run_time_error") and db_data.get(key)):
            flag = "\t***"
        #print '%-25s ==> %-10s%s' % (key, str(db_data.get(key)), flag)

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

    try: 
        # connect to the database
        conn = db.connect(host=host,db=db,user=user,passwd=passwd)
        cursor = conn.cursor()
    
        # execute the query
        cursor.execute(query)

        # close connection
        cursor.close()
        conn.close()
        
        print "Query inserted into database"

    except:

        #sql_file = os.getenv('HOME') + "/ior.sql_query"
        sql_file = db_path + "/ior.sql_query"

        # if unable to connect to db, print query to file sql_query
        try:
            f = open(sql_file,'a')
        except:
            f = open(sql_file,'w')
        try:
            f.write(query + ';\n')
            f.close()
            print "\nAppended query to %s" % sql_file 
        except:
            print "Unable to append query to %s" % sql_file

    # print query to standard out for user's benefit
    #print query
    

# print gnuplot-compatible data to gnuplot_file
def gnuplot_insert(db_data):

    gnuplot_data = os.getenv('HOME') + "/ior.gnuplot.data"
    gnuplot_sep  = ","          # will be field-delimiter for gnuplot
    keys         = sorted(db_data.keys())

    # write field-names in a comment at the top, to make it easier to
    # construct gnuplot commands, looking at the file.
    try:
        os.stat(gnuplot_data)
        f = open(gnuplot_data,'a')
    except:
        # file doesn't exist yet.  write comments at the top.
        f = open(gnuplot_data,'a')
        i = 1                   # gnuplot columns start at "1"
        comment = ""
        for key in keys:
            comment += "# %02d_%s \n" % (i, key)
            i += 1
        f.write(comment)

    # write one data-line with all field-values
    line = ""
    for key in keys:
        val = db_data.get(key, None)
        if (val == None):
            line += "0"
        elif ((type(val) == type("")) \
              and (val.find(" ") >= 0)):
            line += ("'" + str(val).replace(gnuplot_sep, "__") + "'")
        else:
            line += str(val)
        line += gnuplot_sep

    f.write(line + "\n");
    f.close()

    print "\nAppended line to %s" % gnuplot_data
    print line


# if the gnuplot-cokmmands file doesn't already exist, then create it.
# This contains commands to produce some graphs, based on the data-file
# written (incrementally) by gnuplot_insert().  We get called
# incrementally, too, which is why we only write the file once.
#
# 
def gnuplot_commands(db_data):

    
    gnuplot_cmds = os.getenv('HOME') + "/ior.gnuplot.cmds"
    gnuplot_data = "./ior.gnuplot.data"
    gnuplot_img  = "./ior.gnuplot.out.ps"

    block_size     = int(db_data.get("block_size"))
    aggregate_size = int(db_data.get("aggregate_size"))
    n_tasks        = int(db_data.get("num_tasks"))
    procs_per_node = int(db_data.get("procs_per_node"))
    n_to_n         = int(db_data.get("file_per_proc"))
    segment_count  = int(db_data.get("segment_count"))
    api            = db_data.get("api")

    mb             = 1024 * 1024

    algorithm_style_str = "N:N"
    if (not n_to_n):
        algorithm_style_str = "N:1"
        if (segment_count == 1):
            algorithm_style_str += " (segmented)"
        else:
            algorithm_style_str += " (strided)"
        

    # write some simple gnuplot commands, using the data written in gnuplot_insert
    try:
        f = open(gnuplot_cmds,'w')
    except:
        fail("couldn't open '" + gnuplot_cmds + "'")

    f.write("set datafile separator \",\"\n") # see gnuplot_data()

    f.write("set title 'IOR ECS BW-tests, {0}, api={1}, ({2} procs * {3} nodes * blocksize={4} MB) = {5} MB total'\n"\
                .format(algorithm_style_str,
                        api,
                        procs_per_node,
                        (n_tasks / procs_per_node),
                        (block_size / mb),
                        (aggregate_size / mb)))

    f.write("set xlabel 'transfer-size (MB)'\n")
    f.write("set ylabel 'bandwidth (MB/s)'\n")
        
    f.write("xtic_fn(x) = sprintf(\"%d%s\", "\
                + "(x < (1024*1024) ? x/1024 : x/(1024*1024)), "\
                + "(x < (1024*1024) ? \"k\" : \"M\")"\
                + ")\n")
    f.write("set xtics rotate\n")

    f.write("set term postscript\n")
    f.write("set output '{0}'\n"\
                .format(gnuplot_img))

    f.write(" plot '{0}' using 80:91:xtic(xtic_fn($80))".format(gnuplot_data)\
                + " with linespoints title 'write', "\
                + "'{0}' using 80:54:xtic(xtic_fn($80))".format(gnuplot_data)\
                + " with linespoints title 'read'"\
                + "\n")





if __name__ == "__main__":
    main()


