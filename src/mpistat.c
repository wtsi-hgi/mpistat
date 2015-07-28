#include <libcircle.h>
#include <dirent.h>
#include <stdio.h>
#include <string.h>

struct item { 
	char *path;
	uint8_t type;
};

/* global file pointer */
FILE *out;

// global variable containing the directory to start in
char *start_dir;

// process work callback
void process_work(CIRCLE_handle *handle)
{
	// dequeue the next item

    // lstat it and dump the lstat data

	// if it's a directory call readdir on it
    // and add all the items in the directory to the work queue

}

int main(int argc, char **argv) {
	// initialise MPI and the libcircle stuff	
	int rank = CIRCLE_init(CIRCLE_SPLIT_RANDOM);

	// open output file
	char *file_name=(char*) malloc(200);;
	sprintf(file_name,"%s/%02d.out",argv[1],rank);
	printf("%s\n",file_name);

	// the process work callback
	CIRCLE_cb_process(&process_work);

	// enqueue the initial directory
	if (rank == 0) {
		CIRCLE_enqueue(argv[1]);
	}

	// enter the processing loop
	//CIRCLE_begin();

	// wait for all processing to finish and then clean up
	//CIRCLE_finalize();
	//fclose(out);

	return 0;
}
