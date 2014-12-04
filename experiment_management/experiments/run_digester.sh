#!/bin/bash
###############################################################################
#  This script, given an experiment management output directory path and path 
#  to db insert file, will determimen which db parser to run (ior or mdtest)
#  It determines what type of output file it is by grepping for ior or mdtest
#  in the output file.
#  It will execute the correct script and place the db query file in the 
#  locations specified byt the db_path arguement.  The db file is named
#  ior.sql_query and/or mdtest.sql_query
#
# To execute this scipt:
# ./run_digester output_file_path db_path
################################################################################
# Determine if arguements provided
if [[ $# -ne 2 ]]; then
  echo Usage ./run_digester output_file_path db_path
  exit
fi 
# Now look at each file in the directory
for i in `ls $1`; do
  #Determine if output is IOR or mdtest and run appropriate parsing script
  grep -q -i ior $1/$i
  if [[ $? == 0 ]]; then
    ./ior_out_to_db.py --file $1/$i --db_file_path $2 
  fi
  grep -q -i mdtest $1/$i
  if [[ $? == 0 ]]; then
    ./mdtest_out_to_db.py --file $1/$i --db_file_path $2
  fi
done

################################################################################
