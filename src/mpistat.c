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

// this is the initialise work function
// it's run on rank 0 once, right at the start
// to kick things off
void my_create_some_work(CIRCLE_handle *handle)
{
	handle->enqueue(start_dir);
}

// this does some work
// basically grabs the next item from the queue and process it
// accordingly. we stick strings on the queue, the first character
// is 0 or 1 depending on if we have a directory or not
// the rest is the full path
void my_process_some_work(CIRCLE_handle *handle)
{
	// get the next item from the queue and determine
	// if it's a directory or not

	// if it's a directory, write out info about it
	// and then do a readdir and add all the children to the queue

	// if it's not a directory, lstat it and write out the info

}

int main(int argc, char **argv) {
	// initialise MPI and the libcircle stuff	
	int rank = CIRCLE_init(CIRCLE_SPLIT_RANDOM);

	// open output file
	char *file_name=(char*) malloc(200);;
	sprintf(file_name,"%s/%02d.out",argv[1],rank);
	printf("%s\n",file_name);

	// the create work callback - basically readdir and adding files &
	// directories to the work queue	
	CIRCLE_cb_create(&my_create_some_work);

	// the process work callback - this is where the lstat / copy or whatever it
	// is you want to do happens
	CIRCLE_cb_process(&my_process_some_work);

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
