import re
import grp
import stat
import os
import mpistat_common

# apply hgi rules for users & groups
# see rt#447639 and #468451
# pass in s : lstat buffer data structure
# rules apply to files are under
# /lustre/scratch[113,114,115] or /nfs/humgen01

# teams / groups lookup
teams={
    "anderson" : "team152",
    "barrett" : "team143",
    "barroso" : "team35",
    "carter" : "team70",
    "deloukas" : "team147",
    "durbin" : "team118",
    "hgi" : "hgi",
    "hurles" : "team29",
    "mcginnis" : "team111",
    "palotie" : "team128",
    "sandhu" : "team149",
    "soranzo" : "team151",
    "tyler-smith" : "team19",
    "zeggini" : "team144"
}
re_hgi_rules=re.compile(r"^((\/lustre\/scratch11[34]|\/lustre/scratch115\/realdata\/mdt[0123])|\/nfs\/humgen01)\/(teams|projects)\/([^/]+)\/.*$")

def hgi_rules(path, s) :
    gid=s.st_gid
    m=re_hgi_rules.match(path)
    if m :
	rule=m.group(3)
	group=m.group(4)
	if rule == "teams" :
		group=teams[group]
        gid=grp.getgrnam(group)[2]
        if s.st_gid != gid :
            # inode has wrong group owner : change it
            mpistat_common.LOG("changing %s group from %s to %s" %
                    (path, grp.getgrgid(s.st_gid)[0], group))
            #os.chown(path,-1,gid)
        # is it a directory
        if stat.S_ISDIR(s.st_mode) :
            # if so want to check that stickyguid is set and set it with a chmod if not
            if not (s.st_mode & 02000 == 01000) :
		mpistat_common.LOG("setting GID bit on %s" % path)
                #os.chmod(path, s.st_mode | stat.S_ISGID)
    return gid

if __name__ == "__main__" :

	import os

	path="/lustre/scratch114/teams/hgi/mpistat_dev/bin/hgi_rules.py"
	s=os.lstat(path)
	print "testing %s" % (path,)
	print hgi_rules(path,s)

        path="/nfs/humgen01/teams/hgi/ej4/t144.sh"
        s=os.lstat(path)
        print "testing %s" % (path,)
        print hgi_rules(path,s)

        path="/lustre/scratch114/projects/crohns/fileloc.txt"
        s=os.lstat(path)
        print "testing %s" % (path,)
        print hgi_rules(path,s)

        path="/nfs/humgen01/projects/helic/pcp.err"
        print "testing %s" % (path,)
        s=os.lstat(path)
        print hgi_rules(path,s)

        path="/lustre/scratch115/realdata/mdt0/projects/ausgen/release-external_X10/20150917/sample_improved_bams_hgi_2/PIL6.bam.bai"
        s=os.lstat(path)
        print "testing %s" % (path,)
        print hgi_rules(path,s)

        path="/lustre/scratch115/realdata/mdt1/teams/hgi/2015july2-resource-pcp.o"
        print "testing %s" % (path,)
        s=os.lstat(path)
        print hgi_rules(path,s)

