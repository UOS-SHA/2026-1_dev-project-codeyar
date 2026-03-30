#pragma once

#include "arg.h"

#define TAG_MAX_LEN	32
#define ARG_MAX_LEN	64

typedef struct
{
	char tag;
	char longtag[TAG_MAX_LEN];
	void (*handler)(LPARGS, char*);
}	PAIR, *LPPAIR;

LPARGS
parse(
	int		argc,
	char*	argv[]
);