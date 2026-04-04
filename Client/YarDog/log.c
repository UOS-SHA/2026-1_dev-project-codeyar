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
	wprintf(LOG_ALERT_PREFIX L"%s\n", szString);
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

VOID	(*Loggers[])(LPCWSTR) = {
	[LOG_ALERT] = AlertLog,
	[LOG_WARN] = WarnLog,
	[LOG_INFO] = InfoLog
};

VOID
InitLog(
	LPARGS	pa
)
{
	uiLogLevel = pa->uiLogLevel;
}

VOID
Log(
	UINT	errorlevel,
	LPCWSTR	szString
)
{
	if (errorlevel > uiLogLevel)
		return;
	if (errorlevel > LOG_INFO || errorlevel < LOG_ALERT)
		return;
	Loggers[errorlevel](szString);
}