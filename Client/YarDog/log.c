#include <Windows.h>
#include <stdio.h>
#include <stdarg.h>

#include "arg.h"
#include "log.h"

UINT	uiLogLevel;

VOID
AlertLog(
	LPCWSTR	szString
)
{
	wprintf(LOG_ALRT_PREFIX L"%s\n", szString);
}

VOID
WarnLog(
	LPCWSTR	szString
)
{
	wprintf(LOG_WARN_PREFIX L"%s\n", szString);
}

VOID
InfoLog(
	LPCWSTR	szString
)
{
	wprintf(LOG_INFO_PREFIX L"%s\n", szString);
}

VOID	(*loggers[])(LPCWSTR) = {
	[LOG_ALRT] = AlertLog,
	[LOG_WARN] = WarnLog,
	[LOG_INFO] = InfoLog
};

VOID
StartupLog(
	LPARGS	pa
)
{
	wprintf(L"============= YarDog =============\n");

	wprintf(L"Log level: %d.\n", pa->uiLogLevel);

	if (pa->szPolicyFileName[0])
		wprintf(L"Policy file path: %s.\n", pa->szPolicyFileName);
	else
		wprintf(L"Using default policy.\n");

	wprintf(L"Student name: %s (ID: %s).\n", pa->szStudentName, pa->szStudentID);

	wprintf(L"============= YarDog =============\n\n\n");
}

VOID
InitLog(
	LPARGS	pa
)
{
	uiLogLevel = pa->uiLogLevel;
	StartupLog(pa);
}

VOID
Die(
	LPCWSTR	szString
)
{
	AlertLog(szString);
	ExitProcess(0);
}

VOID
Log(
	UINT	level,
	LPCWSTR	szString
)
{
	if (level >= uiLogLevel)
		return;
	if (level > LOG_INFO || level < LOG_ALRT)
		return;
	loggers[level](szString);
}