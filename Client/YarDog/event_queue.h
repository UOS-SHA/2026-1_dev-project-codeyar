#pragma once

#include "arg.h"
#include "tree.h"

typedef struct
{
	BOOL	bIsValid;
	WCHAR	szLog[LOG_TEXT_MAX_LEN];
}	ITEM, * LPITEM;

VOID
InitEventQueue(
	LPARGS	pa
);