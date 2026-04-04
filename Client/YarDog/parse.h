#pragma once

#include "arg.h"

#define TAG_MAX_LEN	32
#define ARG_MAX_LEN	64

LPARGS
parse(
	int			argc,
	wchar_t*	argv[]
);