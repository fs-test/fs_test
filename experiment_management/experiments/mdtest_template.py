import sys,os,time
sys.path += [ './lib', '../lib' ]
import expr_mgmt

# the mdtest_wrapper actually calls mpirun so use a non-default mpirun command
mpirun = "/users/user1/mdtest/wrapper.py"

# if you want to use this to run a new test, use the current time,
# if you want to use this to complete an already started test, use that time
mpi_options = {
  "np"   : [ 2, 4 ], 
}

mpi_program = ( "/users/user1/mdtest/mdtest" ) 

program_options = {
  "I" : [ 1, 10 ],
  "d" : [ "pfs/user1/mdtest.out" ], 
  "z" : [ 1, 2 ],
  "b" : [ 2 ],
}

# the wrapper looks for these args at the end of the args and splices them
# off before calling IOR, these args are used by the wrapper to get more
# data into the sql insert
program_arguments = [
  [ "--desc ./mdtest.%d" % int(time.time()) ]
]

#############################################################################
# typical use of this framework won't require modification beyond this point
#############################################################################

def get_commands( expr_mgmt_options ):
  global mpi_options,program_options,program_arguments,mpirun
  commands = expr_mgmt.get_commands( 
      mpi_options=mpi_options,
      mpi_program=mpi_program,
      program_arguments=program_arguments,
      mpirun=mpirun,
      program_options=program_options,
      expr_mgmt_options=expr_mgmt_options )
  return commands
