#include <libcircle.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <string.h>
#include <errno.h>
#include <dirent.h>
#include <limits.h>

// globals
// dirty... but KISS for now...
FILE *out; // rank specific output file handle
char start_dir[4096]; // absolute path of start directory
char item_buf[5000]; // buffer to construct type / path combos for queue items

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

    // skip . and ..

    // lstat it and dump the lstat data
    // for now, just print the filename to the
    // output file

    // if it's a directory call readdir on it
    // and add all the items in the directory to the work queue

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
    if (argc != 2) {
        fprintf(stderr, "Usage : mpistat <data dir> <start dir>\n");
        return 1;
    }
    realpath(argv[1],start_dir);
    DIR *sd=opendir(start_dir);
    if (!sd) {
        fprintf (stderr, "Cannot open directory '%s': %s\n",
            argv[1], strerror (errno));
        exit (EXIT_FAILURE);
    }
    sprintf(item_buf,"%c%s",'d',start_dir);

	// initialise MPI and the libcircle stuff	
	int rank = CIRCLE_init(CIRCLE_SPLIT_RANDOM);

	// open output file for this particular rank
    // (colllated at the end)
	char *file_name=(char*) malloc(200);;
	sprintf(file_name,"%s/%02d.out",argv[1],rank);
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
