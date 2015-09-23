#include <libcircle.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <string.h>
#include <errno.h>
#include <dirent.h>
#include <limits.h>
#include <sys/stat.h>
// globals
// dirty... but KISS for now...
FILE *out; // rank specific output file handle
char start_dir[8192]; // absolute path of start directory
char item_buf[8192]; // buffer to construct type / path combos for queue items

char file_type(unsigned char c) {
    switch (c) {
        case DT_BLK :
            return 'b';
        case DT_CHR :
            return 'c';
        case DT_DIR :
            return 'd';
        case DT_FIFO :
            return 'F';
        case DT_LNK :
            return 'l';
        case DT_REG :
            return 'f';
        case DT_SOCK :
            return 's';
        default :
            return 'u';
    }
}

void do_lstat(char *path) {
    static struct stat buf;
    if (lstat(path+1,&buf) == 0) {
        fprintf(out,"%s\t%c\t%d\t%d\t%d\t%d\t%d\t%d\n", path+1, *path,
                buf.st_size, buf.st_uid, buf.st_gid, buf.st_atime,
                buf.st_mtime, buf.st_ctime);
    } else {
        fprintf (stderr, "Cannot lstat '%s': %s\n", path+1, strerror (errno));
    }

}

void do_readdir(char *path, CIRCLE_handle *handle) {
    int path_len=strlen(path+1);
    DIR *d = opendir (path+1);
    if (!d) {
        fprintf (stderr, "Cannot open '%s': %s\n", path+1, strerror (errno));
        return;
    }
    while (1) {
        struct dirent *entry;
        entry = readdir(d);
        if (entry==0) {
            break;
        }
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") ==0) {
            continue;
        }
        char *tmp=(char*) malloc(path_len+strlen(entry->d_name)+3);
        *tmp=file_type(entry->d_type);
        strcpy(tmp+1,path+1);
        *(tmp+path_len+1)='/';
        strcpy(tmp+path_len+2,entry->d_name);
        handle->enqueue(tmp);
    }
    closedir(d);
}

// create work callback
// this is called once at the start on rank 0
// use to seed rank 0 with the initial dir to start
// searching from
void create_work(CIRCLE_handle *handle) {
    handle->enqueue(item_buf);
}

// process work callback
void process_work(CIRCLE_handle *handle)
{
    // dequeue the next item
    handle->dequeue(item_buf);
    do_lstat(item_buf);
    if (*item_buf == 'd') {
        do_readdir(item_buf,handle);
    }
}

// arguments :
// first argument is data directory to store the lstat files
// second argument is directory to start lstating from
int main(int argc, char **argv) {

    // verify that the start directory is a real directory
    // and that we can open it, make a string consisting of
    // d/path/to/start/dir
    // every queue element is a string where the first letter is
    // the type of the file and the rest is the full path in plain text
    // i.e. not b64 encoded. only need to b64 encode when printing into
    // final output file
    // the resulting string will be used to seed the queue in the
    // create work callback
    if (argc != 3) {
        fprintf(stderr, "Usage : mpistat <data dir> <start dir>\n");
        return 1;
    }
    realpath(argv[1],start_dir);
    DIR *sd=opendir(start_dir);
    if (!sd) {
        fprintf (stderr, "Cannot open directory '%s': %s\n",
            start_dir, strerror (errno));
        exit (EXIT_FAILURE);
    }
    sprintf(item_buf,"%c%s",'d',start_dir);

	// initialise MPI and the libcircle stuff	
	int rank = CIRCLE_init(argc,argv,CIRCLE_SPLIT_RANDOM);

	// open output file for this particular rank
    // (colllated at the end)
	char *file_name=(char*) malloc(200);;
	sprintf(file_name,"%s/%02d.out",argv[2],rank);
	out=fopen(file_name, "w");

    // set the create work callback
    CIRCLE_cb_create(&create_work);

	// set the process work callback
	CIRCLE_cb_process(&process_work);

	// enter the processing loop
	CIRCLE_begin();

	// wait for all processing to finish and then clean up
	CIRCLE_finalize();
	fclose(out);

	return 0;
}
