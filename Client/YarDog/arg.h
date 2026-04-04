#pragma once

#include <Windows.h>

typedef struct
{
	WCHAR	szPolicyFileName[MAX_PATH];
	UINT	uiLogLevel;
}	ARGS, *LPARGS;