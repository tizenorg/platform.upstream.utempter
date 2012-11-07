#define _GNU_SOURCE 1

#include <errno.h>
#include <fcntl.h>
#include <pty.h>
#include <pwd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <utmp.h>
#include <utmpx.h>
#include <unistd.h>

static void usage(void) {
    fprintf(stderr, "Usage:     -a <slave-device-name> <host>\n"
	            "           -d <slave-device-name>\n");
    exit(1); 
}

static void checkDevice(const char * device) {
    struct stat sb1, sb2;
    int flags;
    
    if (strstr(device, "/../") || strstr(device, "/./") || 
	strstr(device, "//")) {
	fprintf(stderr, "a simple path is required\n");
	exit(1);
    }

    if (strncmp(device, "/dev/", 5)) {
	fprintf(stderr, "the device must begin with /dev/\n");
	exit(1);
    }

    if (fstat(3, &sb1)) {
	fprintf(stderr, "error stat'ing fd 3: %s\n", strerror(errno));
	exit(1);
    }

    if (major(sb1.st_rdev) == 2) {
	if (lstat(device, &sb2)) {
	    fprintf(stderr, "error stat'ing %s: %s\n", device, strerror(errno));
	    exit(1);
	}

	if (major(sb2.st_rdev) != 3) {
	    fprintf(stderr, "%s is not the slave for the master pty on fd 3\n",
		    device);
	    exit(1);
	}

	if (minor(sb1.st_rdev) != minor(sb2.st_rdev)) {
	    fprintf(stderr, "fd 3 and %s are not the same device\n",
		    device);
	    exit(1);
	}
    } else if (major(sb1.st_rdev) == 5 && minor(sb1.st_rdev) == 2) {
	char * dev2 = ptsname(3);

	if (!dev2 || strcmp(dev2, device)) { 
	    fprintf(stderr, "passed master doesn't match slave name\n");
	    exit(1);
	}
    } else {
	fprintf(stderr, "fd 3 is not a master pty device (it is %d, %d)\n",
		major(sb1.st_rdev), minor(sb1.st_rdev));
	exit(1);
    }

    if ((flags = fcntl(3, F_GETFL, 0)) < 0) {
	fprintf(stderr, "error getting flags for fd 3: %s\n", strerror(errno));
	exit(1);
    }

    if ((flags & O_RDWR) != O_RDWR) {
	fprintf(stderr, "fd 3 is not read/writeable\n");
	exit(1);
    }
}

int main(int argc, const char ** argv) {
    struct utmpx utx;
    int add;
    const char * device, * host;
    struct passwd * pw;
    int i;
    struct stat sb;
    char * id;
 
    if (argc < 3) usage();

    for (i = 0; i < 3; i++) {
	if (fstat(i, &sb)) {
	    fprintf(stderr, "error: failed to stat %d\n", i);
	    exit(1);
	}
    }

    if (!strcmp(argv[1], "-a")) {
	if (argc > 4) usage();
	add = 1;
    } else if (!strcmp(argv[1], "-d")) {
	if (argc != 3) usage();
	add = 0;
    } else
	usage();

    device = argv[2];

    if (!getuid()) {
	host = argv[3];		/* either NULL or something real */
    } else { 
	host = NULL;
    }

    memset(&utx, 0, sizeof(utx));
    if (add)
	utx.ut_type = USER_PROCESS;
    else
	utx.ut_type = DEAD_PROCESS;

    utx.ut_pid = getppid();
    if (utx.ut_pid == 1) {
	fprintf(stderr, "error: parent pid should not be init\n");
	exit(1);
    }

    checkDevice(device);

    strncpy(utx.ut_line, device + 5, sizeof(utx.ut_line));

    pw = getpwuid(getuid());
    if (!pw) {
	fprintf(stderr, "cannot find user w/ uid %d\n", getuid());
	exit(1);
    }

    strncpy(utx.ut_user, pw->pw_name, sizeof(utx.ut_user));

    if (host) 
	strncpy(utx.ut_host, host, sizeof(utx.ut_host));

    if (!strncmp("pts/", utx.ut_line, 4)) {
	id = utx.ut_line + 3;
	if (strlen(id) > 4) id++;
    } else {
	id = utx.ut_line + 2;
    }

    strncpy(utx.ut_id, id, sizeof(utx.ut_id));

    gettimeofday(&utx.ut_tv, NULL);

    pututxline(&utx);
    updwtmpx(_PATH_WTMP, &utx);

    return 0;
}
