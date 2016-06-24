#define _XOPEN_SOURCE 600

#include <errno.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <signal.h>

#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/timeb.h>
#include <sys/wait.h>

#define SIZE_RECV 1024
#define SIZE_SENT 512

int main(void)
{
	struct sockaddr_in sock = {0};

	char recieved[256] = {'\0'};
	char sent[256] = {'\0'};

	//char *recieved = malloc(sizeof(*recieved) * SIZE_RECV);
	//char *sent = malloc(sizeof(*recieved) * SIZE_SENT);

	int sd = socket(AF_INET, SOCK_STREAM, 0);
	if(sd < 0) {
		perror("Socket"); //fix with better error
		return -1;	
	}

	sock.sin_family = AF_INET;
	sock.sin_port = htons(6667);
	sock.sin_addr.s_addr = inet_addr("127.0.0.1");

	if(connect(sd, (struct sockaddr *)&sock, sizeof(sock)) < 0) {
		perror("Connect"); //fix with better error
		return -2;
	}
	
	printf("We have successfully made a connection\n");

	pid_t b;

	b = fork();

	ssize_t msg_sz = 0;
	ssize_t snd_sz = 0;

	if(b < 0) {
		perror("Fork failed");
	}
	else if(b == 0) {
		for(;;)
		{
			while((msg_sz = recv(sd, &recieved, sizeof(recieved)-1, MSG_DONTWAIT)) > 0) {
				recieved[msg_sz] = '\0';
				printf("%s", recieved);
			}

			memset(recieved, '\0', sizeof(recieved));
		}
	}
	else {
		//user
		//nick
		for(;;) {
			sleep(1);

			if(msg_sz > 0) {
				recieved[msg_sz] = '\0';
				printf("here\n");
				if(strstr(recieved, "PING") != NULL) {
					memset(sent, '\0', sizeof(recieved));
					char *pos = malloc(sizeof(pos));
					pos = strstr(recieved, " ")+1;
					sprintf(sent, "PONG %s\r\n", pos);
					if ((snd_sz = send(sd, &sent, strlen(sent), 0)) != (ssize_t)strlen(sent)) {
						perror("Message transmission error");
					}
				}
			}

			printf("What would you like to do: ");
			fgets(sent, sizeof(sent), stdin);

			sent[strlen(sent)] = '\0';

			if ((snd_sz = send(sd, &sent, strlen(sent), 0)) != (ssize_t)strlen(sent)) {
				perror("Message transmission error");
			}

			if(msg_sz > 0) {
				recieved[msg_sz] = '\0';
				printf("here\n");
				if(strstr(recieved, "PING") != NULL) {
					memset(sent, '\0', sizeof(recieved));
					char *pos = malloc(sizeof(pos));
					pos = strstr(recieved, " ")+1;
					sprintf(sent, "PONG %s\r\n", pos);
					if ((snd_sz = send(sd, &sent, strlen(sent), 0)) != (ssize_t)strlen(sent)) {
						perror("Message transmission error");
					}
				}
			}

			if(strncmp(sent, "quit\n", strlen(sent)) == 0) {
				printf("Exitting...");
				kill(b, SIGKILL);
				exit(0);
			}	

			memset(sent, '\0', sizeof(recieved));

		}
	}

	close(sd);
}
