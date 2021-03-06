'''
Common functions for generating slurm scripts

Created on 15/12/2014

@author: Andrew Robinson
'''

import os, sys, subprocess, time

def makeExclusiveHeader(**kwargs):
    '''Makes an exclusive slurm header'''
    allargs={"partition": "compute", "nodes": "1", "mem":"250000", "time": "8:00:00", "slurmconf": ""}
    allargs.update(kwargs)
    allargs["slurmconf"] = findSlurmConf()
    
    header="""#!/bin/bash
#SBATCH --nodes={nodes}
#SBATCH --exclusive
#SBATCH --mem={mem}
#SBATCH --time={time}
#SBATCH --partition={partition}
{slurmconf}
""".format(**allargs)
    
    return header


def makeHeader(**kwargs):
    '''Makes a non-exclusive slurm header'''
    allargs={"partition": "compute", "ntasks": "1", "mem":"1024", "time": "1:00:00", "slurmconf": ""}
    allargs.update(kwargs)
    allargs["slurmconf"] = findSlurmConf()
    
    header="""#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={ntasks}
#SBATCH --time={time}
#SBATCH --mem-per-cpu={mem}
#SBATCH --partition={partition}
{slurmconf}
""".format(**allargs)
    
    return header

def findSlurmConf():
    '''Searches for the slurm.conf file for the user (if it exists)'''
    curdir = os.path.realpath(".")
    slurmconffilename = None
    while curdir not in ('/', '/home'):
        if os.path.isfile("%s/slurm.conf"%curdir):
            slurmconffilename = "%s/slurm.conf"%curdir
            break
        curdir = os.path.dirname(curdir)
    if slurmconffilename is not None:
        with open(slurmconffilename) as f:
            tmp=f.read()
        return tmp
    return ""


def quote(s):
    return "\"%s\""%s


def writecmd(argv):
    '''Writes a log entry for the given command'''
    args = map(quote, argv[1:])
    prog = argv[0]
    if prog.startswith("/usr/local/limsradseq/1/bin/"):
        prog = prog[len("/usr/local/limsradseq/1/bin/"):]
    writelog("%s %s" % (prog," ".join(args)))


def writelog(logentry):
    '''writes logentry to the process.log file with current date/time'''
    curdir = os.path.realpath(".")
    procfilename = None
    relpath = ""
    while curdir not in ('/', '/home'):
        if os.path.isfile("%s/process.log"%curdir):
            procfilename = "%s/process.log"%curdir
            break
        relpath="%s/%s" % (os.path.basename(curdir), relpath)
        curdir = os.path.dirname(curdir)
    if procfilename is not None:
        with open(procfilename, 'a') as f:
            f.write("%s: [%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), relpath, logentry));


def loadTemplate(name):
    '''Loads a template file by name.'''
    tmp=""
    filename = os.path.realpath("%s/../share/carlaseq/templates/%s"%(os.path.dirname(os.path.abspath(__file__)),name))
    with open(filename) as f:
        tmp=f.read()
    return tmp


def expandFiles(files, dirfilter="*", quiet=False):
    '''
    Takes an array of filenames and expands any wildcards within
    
    @param files: array, filenames to expand
    @param dirfilter: a wildcard filter to apply to directories
    @return: array, the expanded list of files (must exist)
    '''
    outfiles = []
    for fn in files:
        if '*' in fn or '?' in fn:
            fnexp = _expandFile(fn)
            for fne in fnexp:
                if os.path.exists(fne):
                    if os.path.isdir(fne):
                        direxp = _expandFile("%s/%s" % (fne, dirfilter))
                        if direxp is None:
                            if not quiet:
                                sys.stderr.write("Warning: directory '%s' contains no matching files and will be ignored\n"%fne)
                        else:
                            outfiles.extend(direxp)
                    else:
                        outfiles.append(fne)
                else:
                    if not quiet:
                        sys.stderr.write("Warning: file/directory '%s' does not exist and will be ignored\n"%fne)
        elif os.path.exists(fn):
            if os.path.isdir(fn):
                direxp = _expandFile("%s/%s" % (fn, dirfilter))
                if direxp is None:
                    if not quiet:
                        sys.stderr.write("Warning: directory '%s' contains no matching files and will be ignored\n"%fn)
                else:
                    outfiles.extend(direxp)
            else:
                outfiles.append(fn)
        else:
            if not quiet:
                sys.stderr.write("Warning: file/directory '%s' does not exist and will be ignored\n"%fn)
    
    # make files canonical
    outfiles = map(os.path.realpath, outfiles)
    
    return outfiles
    
    
def _expandFile(fn):
    '''Expands a single filename'''
    if str(fn).strip() != "":
        cmd = ["bash", "-c", 'ls -1d %s' % fn]
        try:
            filelist = subprocess.check_output(cmd, stderr=subprocess.STDOUT).rstrip()
            return filelist.split("\n")
        except subprocess.CalledProcessError:
            pass
    return None
