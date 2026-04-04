#pragma once

#include <Windows.h>

#define LOG_ALRT	1
#define LOG_WARN	2
#define LOG_INFO	3

#define LOG_ALRT_PREFIX		L"[x] "
#define LOG_WARN_PREFIX		L"[!] "
#define LOG_INFO_PREFIX		L"[i] "

#define LOG_LEVEL_QUIET		1
#define LOG_LEVEL_DEFAULT	2
#define LOG_LEVEL_TALKATIVE	3
#define LOG_LEVEL_VERBOSE	4

VOID
InitLog(
	LPARGS	pa
);

VOID
Die(
	LPCWSTR	szString
);

VOID
Log(
	UINT	errorlevel,
	LPCWSTR	szString
);