CC      = gcc -g
CC2 = g++ -g
LDIR = lib
DEPS    = $(LDIR)/mcce.h
LIB     = $(LDIR)/mcce.a
AR      = ar
ARFLAGS = rvs
STEP6 = $(LDIR)/analysis.o

SRC = $(wildcard $(LDIR)/*.c)
DELPHI = bin/delphi

bin/mcce: mcce.c $(LIB) $(DEPS) $(DELPHI) $(STEP6)
	$(CC2) -o bin/mcce mcce.c $(STEP6) $(LIB) -lm

$(DELPHI): $(LDIR)/delphi/delphi
	cp $(LDIR)/delphi/delphi $(DELPHI)

$(LDIR)/delphi/delphi:
	$(MAKE) -C $(LDIR)/delphi

OBJ     = $(SRC:.c=.o)

$(LIB): $(OBJ)
	cd $(LDIR)
	$(AR) $(ARFLAGS) $(LIB) $(OBJ)

$(LDIR)/%.o: $(LDIR)/%.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)


$(STEP6): lib/analysis.cpp $(DEPS)
	cd $(LDIR)
	$(CC2) -c -o $@ $< $(CFLAGS)
clean:
	-rm -f bin/mcce bin/delphi $(LIB) $(LDIR)/*.o
	$(MAKE) clean -C $(LDIR)/delphi

cleanbin/mcce:
	-rm -f bin/mcce bin/delphi $(LIB) $(LDIR)/*.o
	$(MAKE) clean -C $(LDIR)/delphi

