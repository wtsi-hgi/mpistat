CFLAGS=-O2 -Wall -I/software/hgi/pkglocal/libcircle/include
LIBS=-L/software/hgi/pkglocal/libcircle/lib -lcircle
all : bin/mpistat

bin/mpistat : src/mpistat.c
	mpicc $(CFLAGS) -o bin/mpistat src/mpistat.c $(LIBS)

clean :
	rm bin/mpistat
