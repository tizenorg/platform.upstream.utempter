#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <unistd.h>

#include "utempter.h"

static char * ptyName = NULL;
static int masterFd;

void addToUtmp(const char *pty, const char *hostname, int cmdfd)
{
    char * argv[] = { "/usr/sbin/utempter", "-a", pty, hostname, NULL};
    pid_t child;
    int status;
    void (*osig) (int) = signal(SIGCHLD, SIG_DFL);

    if (!(child = fork())) {
	signal(SIGCHLD, SIG_DFL);
	/* these have to be open to something */
	dup2(cmdfd, 0);
	dup2(cmdfd, 1);
	dup2(cmdfd, 3);
	execv(argv[0], argv);
	exit(1);
    }

    waitpid(child, &status, 0);
    signal(SIGCHLD, osig);

    ptyName = strdup(pty);
    masterFd = cmdfd;
}

void removeFromUtmp(void) 
{
    if (!ptyName) return;

    removeLineFromUtmp(ptyName, masterFd);

    free(ptyName);
    ptyName = NULL;
}

void removeLineFromUtmp(const char * pty, int fd) {
    char * argv[] = { "/usr/sbin/utempter", "-d", pty, NULL};
    pid_t child;
    void (*osig) (int) = signal(SIGCHLD, SIG_DFL);

    if (!(child = fork())) {
	signal(SIGCHLD, SIG_DFL);
	/* these have to be open to something */
	dup2(fd, 0);
	dup2(fd, 1);
	dup2(fd, 3);
	execv(argv[0], argv);
	fprintf(stderr, "EXEC FAILED!\n");
    }

    waitpid(child, NULL, 0);
    signal(SIGCHLD, osig);
}
