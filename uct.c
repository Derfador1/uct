#define _XOPEN_SOURCE 600

#include <errno.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/timeb.h>

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

	sleep(1);
	for(;;)
	{
		ssize_t msg_sz = 0;
		ssize_t snd_sz = 0;

		while((msg_sz = recv(sd, &recieved, sizeof(recieved)-1, MSG_DONTWAIT)) > 0) {
			recieved[msg_sz] = '\0';
			printf("%s", recieved);
		}

		printf(">");
		fgets(sent, sizeof(sent), stdin);
		if ((snd_sz = send(sd, &sent, strlen(sent), 0)) != (ssize_t)strlen(sent)) {
			perror("Message transmission error");
		}

		memset(recieved, '\0', SIZE_RECV);
		memset(sent, '\0', SIZE_SENT);
	}

	free(recieved);
	free(sent);
}
