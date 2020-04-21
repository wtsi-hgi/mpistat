import re
import grp
import stat
import os
import mpistat_common
import errno

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

# Updated 20191009 / ch12:
# * Added exceptions
# * Copied group permissions from user permissions
exceptions = {
	"otcoregen": 15114
}

# Updated 20200124 / ch12:
# * Added scratch118, with root in /lustre/scratch118/humgen/hgi
# Updated 20180503 / ch12:
# * Corrected regex for scratch115
# * Removed scratch113 alternate
# * Added scratch119 alternate (humgen MDTs are 2 and 3)
re_hgi_rules=re.compile(r"^((\/lustre\/scratch114|\/lustre\/scratch115\/realdata\/mdt[0123]|\/lustre\/scratch118\/humgen\/hgi|\/lustre\/scratch119\/realdata\/mdt[23])|\/nfs\/humgen01)\/(teams|projects)\/([^/]+)\/.*$")

def hgi_rules(path, s) :
    gid=s.st_gid
    m=re_hgi_rules.match(path)
    if m :
	rule=m.group(3)
	newgroup=m.group(4)
	if rule == "teams" :
		newgroup=teams[newgroup]

        # 20191009 / ch12
        gid=exceptions.get(newgroup, grp.getgrnam(newgroup)[2])

        if s.st_gid != gid :
            # inode has wrong group owner : change it
            oldgroup=grp.getgrgid(s.st_gid)[0]
            mpistat_common.LOG("changing %s group from %s to %s : %d bytes" %
                    (path, oldgroup, newgroup, s.st_size))
            try :
                os.chown(path,-1,gid)
            except (IOError, OSError) as e :
                mpistat_common.ERR("Failed to change group from %s to %s for %s : %s" % (oldgroup, newgroup, path, os.strerror(e.errno)))

        # 20191009 / ch12
        # Are the user permissions different from the group permissions?
        usr_permissions = (s.st_mode & stat.S_IRWXU) or stat.S_IRWXU  # Assume full group permissions if no user permissions
        grp_permissions = s.st_mode & stat.S_IRWXG
        if (usr_permissions >> 3) != grp_permissions:
            mpistat_common.LOG("setting group permissions on %s" % path)
            try:
                os.chmod(path, s.st_mode | (usr_permissions >> 3))
            except (IOError, OSError) as e :
                mpistat_common.ERR("Failed to set group permissions on '%s' : %s" % (path, os.strerror(e.errno)))

        # is it a directory
        if stat.S_ISDIR(s.st_mode) :
            # if so want to check that stickyguid is set and set it with a chmod if not
            if not (s.st_mode & stat.S_ISGID) :
		mpistat_common.LOG("setting GID sticky bit on %s" % path)
                try :
                    os.chmod(path, s.st_mode | stat.S_ISGID)
                except (IOError, OSError) as e :
                    mpistat_common.ERR("Failed to set GID sticky bit on '%s' : %s" % (path, os.strerror(e.errno)))

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

