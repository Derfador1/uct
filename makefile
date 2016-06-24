FLAGS+=-std=c11 
CFLAGS+=-Wall -Wextra -pedantic -Werror 
CFLAGS+=-Wwrite-strings -fstack-usage -Wstack-usage=1024 -Wfloat-equal -Waggregate-return -Winline

.PHONY: debug profile clean

uct: uct.o

debug: CFLAGS+=-g
debug: uct

profile: CFLAGS+=-pg
profile: LDFLAGS+=-pg
profile: uct

clean: 
	rm -r *.o *.su uct
