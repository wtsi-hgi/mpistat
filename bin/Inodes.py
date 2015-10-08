import riak
import riak.datatypes
import json

# class to abstract an inode entry for storage in riak
class Inode:
    def __init__(self, client, path, size, uid, gid, type, atime, mtime, ctime, children = None):
        self.client=client
        self.bucket = client.bucket_type('maps').bucket('inodes')
        self.key = path
        self.inode_map = riak.datatypes.Map(self.bucket, self.key)
        self.inode_map.registers['size'].assign(size)
        self.inode_map.registers['uid'].assign(uid)
        self.inode_map.registers['gid'].assign(gid)
        self.inode_map.registers['type'].assign(type)
        self.inode_map.registers['atime'].assign(atime)
        self.inode_map.registers['mtime'].assign(mtime)
        self.inode_map.registers['ctime'].assign(ctime)
        self.inode_map.registers['parent'].assign(path[0:path.rfind('/')])
        if type == 'd' : # set children to empty set initially
            if children :
                self.inode_map.sets['children'].assign(children) 
        # Thus far, all changes to the user_map object have only been
        # made locally. To commit them to Riak, we have to use the
        # store() method. You can alter Riak Data Types as much as you
        # wish on the client side prior to committing those changes to
        # Riak.
        self.inode_map.store()

    def as_json(self):
        m = self.inode_map.reload()
        inode_dict = {
            'path': m.key,
            'size': m.registers['size'].value,
            'uid': m.registers['uid'].value,
            'gid': m.registers['gid'].value,
            'type': m.registers['type'].value,
            'atime': m.registers['atime'].value,
            'mtime': m.registers['mtime'].value,
            'ctime': m.registers['ctime'].value,
        }
        return json.dumps(inode_dict)

if __name__ == "__main__":

    # test the adding stuff to riak
    # assumes you are piping in data that has been
    # created by the old style mpistat
    # i.e. lines containing tab seperated lstat info
    # with one entry per line and the path being
    # base64 encoded
    import fileinput
    import base64
    
    rc = riak.RiakClient(nodes=[
        {'host':'127.0.0.1','pb_port':11087,'http_port':11098},
        {'host':'127.0.0.1','pb_port':12087,'http_port':12098},
        {'host':'127.0.0.1','pb_port':13087,'http_port':13098},
        {'host':'127.0.0.1','pb_port':14087,'http_port':14098},
        {'host':'127.0.0.1','pb_port':15087,'http_port':15098}
    ])
    count=0
    for line in fileinput.input() :
    	bits=line.split('\t')
        inode = Inode(
            client=rc,
            path=base64.b64decode(bits[1]),
            size=bits[2],
            uid=bits[3],
            gid=bits[4],
            type=bits[8],
            atime=bits[5],
            mtime=bits[6],
            ctime=bits[7]
        )
        count += 1
        if (count % 1000 == 0) :
            print "%d lines processed" % (count,)
        #print inode.as_json()
