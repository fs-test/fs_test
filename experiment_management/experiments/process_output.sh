#!/bin/bash
###############################################################################
# This script is intended to run as a post script in experiment management via 
# run_expr.py.  # After each run of mdtest or IOR, it determines if the 
# experiment management output files contains IOR output or mdtest output. 
# Based on this, it will
# run the appropriate python script that parses the output and generate an  
# sql_query file in your HOME directory.
#
# Note that this script relies on the user setting the expr_mgmnt_top variable
# to the experiment management directory.
#
# Running mdtest with this post script example:
# 
# ./run_expr.py -w 1800 -d msub -M '-j oe -V' 
#     --post=/turquoise/users/atorrez/working-wrappers/fs_test \
#             /experiment_management/experiments/process_output.sh \
#     -c experiments/mdtest_rrz.py
#
#   Note:  Full path to post script and db_path must be specified
#
################################################################################

#########
# Attention!  SET these variable accordingly
expr_mgmnt_top=/turquoise/users/atorrez/working-wrappers/fs_test/experiment_management
ior_db_path=/users/atorrez/sql_files/ior
mdtest_db_path=/users/atorrez/sql_files/mdtest
# Attention!
#########

# Find the most current directory that contains output files
dir=`ls -alrt $expr_mgmnt_top/output | grep drw | grep -v '\.' | tail -1 | awk '{print $NF}'`
# Find the most recent file - the one just created by the experiment management run
file=`ls -al $expr_mgmnt_top/output/$dir/ | grep -v drw | grep -v total | tail -1|  awk '{print $NF}'`

filepath=$expr_mgmnt_top/output/$dir/$file

#Determine if output is IOR or mdtest and run appropriate parsing script
grep -q -i ior $filepath
if [[ $? == 0 ]]; then
   $expr_mgmnt_top/experiments/ior_out_to_db.py --file $filepath --db_file_path $ior_db_path 
fi
grep -q -i mdtest $filepath
if [[ $? == 0 ]]; then
   $expr_mgmnt_top/experiments/mdtest_out_to_db.py --file $filepath --db_file_path $mdtest_db_path
fi
################################################################################
