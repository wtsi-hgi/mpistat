import re
import grid
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

def hgi_rules(path, s) :
    # only one rule can possibly apply
    # so try the first and only try the second if it doesn't apply
    status,gid=hgi_teams_rule(path, s)
    if status :
        return(status,gid)
    return hgi_projects_rule(path, s)

# regexes for teams rule
re_hgi_teams1=re.compile(r"^\/local\/scratch11[345]\/teams\/([^/]+)\/.*$")
re_hgi_teams2=re.compile(r"^\/nfs\/humgen01\/teams\/([^/]+)\/.*$")

def hgi_teams_rule(path, s) :
    # file / directory under /lustre/scratch11[3,4,5]/teams/<team>/foo/bar
    # should be owned by group corresponding to the relevant team 
    m=None
    m1=re_hgi_teams1.compile(path)
    if m1 :
        m=m1
    else :
        m2=re_hgi_teams2.compile(path)
        if m2 :
            m=m2
        else :
            return (False, s.st_gid)
    if m :
        team=m.group(1)
        group=teams[team]
        gid=grp.getgrnam(group)[2]
        if s.dt_gid != gid :
            # inode has wrong group owner : change it
            LOG("changing %s group from %s to %s" %
                    (grp.getgrgid(s.st_gid)[0],group))
            #os.chown(path,-1,gid)
            return (True, gid)
    return (False, s.st_gid)

# regexes for projects rules
re_hgi_projects1=re.compile(r"^\/local\/scratch11[345]\/projects\/([^/]+)\/.*$")
re_hgi_projects2=re.compile(r"^\/nfs\/humgen01\/projects\/([^/]+)\/.*$")

def hgi_projects_rule(path, s) :
    # file / directory under /lustre/scratch11[3,4,5]/teams/<team>/foo/bar
    # should be owned by group corresponding to the relevant team 
    m=None
    m1=re_hgi_teams1.compile(path)
    if m1 :
        m=m1
    else :
        m2=re_hgi_teams2.compile(path)
        if m2 :
            m=m2
        else :
            return (False,s.st_gid)
    if m :
        project=m.group(1)
        gid=grp.getgrnam(project)[2]
        if sb.dt_gid != gid :
            # inode has wrong group owner : change it
            LOG("changing group owner of %s from %s to %s" % 
                    (path, grp.getgrgid(s.st_gid)[0], project))
            #os.chown(path,-1,gid)
            return (True, gid)
    return (False,s.st_gid)

