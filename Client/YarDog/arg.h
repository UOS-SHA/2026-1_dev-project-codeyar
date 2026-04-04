#pragma once

#include <Windows.h>

#define WORKER_COUNT_MIN		1
#define WORKER_COUNT_DEFAULT	5
#define WORKER_COUNT_MAX		10

typedef struct
{
	WCHAR	szPolicyFileName[MAX_PATH];
	UINT	uiLogLevel;
	WCHAR	szStudentID[16];
	WCHAR	szStudentName[16];
	UINT	uiWorkerCount;
}	ARGS, *LPARGS;