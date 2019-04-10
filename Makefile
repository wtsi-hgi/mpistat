CFLAGS=-O2 -Wall -I${HOME}/include -std=c++11
LIBS=-L${HOME}/lib -lcircle
all : bin/mpistat

bin/mpistat : src/mpistat.c
	mpic++ $(CFLAGS) -o bin/mpistat src/mpistat.cc $(LIBSC

clean :
	rm bin/mpistat
