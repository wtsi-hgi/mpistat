#include <libcircle.h>
#include <dirent.h>
#include <stdio.h>
#include <string.h>

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

struct item { 
	char *path;
	unsigned char type;
};

/* global file pointer */
FILE *out;

// create work callback
// this is called once at the start on rank 0
// use to seed rank 0 with the initial dir to start
// searching from
void create_work(CIRCLE_handle *handle) {
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
