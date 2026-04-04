#pragma once

#include <Windows.h>

#define LOG_ALERT	1
#define LOG_WARN	2
#define LOG_INFO	3

#define LOG_ALERT_PREFIX	L"[x]"
#define LOG_WARN_PREFIX		L"[!]"
#define LOG_INFO_PREFIX		L"[i]"

#define LOG_LEVEL_QUIET		0
#define LOG_LEVEL_DEFAULT	1
#define LOG_LEVEL_TALKATIVE	2
#define LOG_LEVEL_VERBOSE	3

VOID
InitLog(
	LPARGS	pa
);

VOID
Log(
	UINT	errorlevel,
	LPCWSTR	szString
);