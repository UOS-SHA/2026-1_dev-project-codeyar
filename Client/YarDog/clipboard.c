#include <Windows.h>
#include <stdio.h>

#include "policy.h"
#include "log.h"

LPWSTR
RetrieveClipboardContent(
	VOID
)
{
	LPWSTR	szBuffer;
	LPWSTR	szSource;
	HANDLE	hData;
	SIZE_T	len;

	if (!OpenClipboard(NULL))
		return NULL;

	if (!IsClipboardFormatAvailable(CF_UNICODETEXT))
		return NULL;

	hData = GetClipboardData(CF_UNICODETEXT);
	if (!hData)
	{
		CloseClipboard();
		return NULL;
	}

	szSource = GlobalLock(hData);
	if (!szSource)
	{
		CloseClipboard();
		return NULL;
	}

	len = wcslen(szSource);
	szBuffer = malloc((len + 1) * sizeof(WCHAR));
	if (szBuffer)
		wcscpy_s(szBuffer, len + 1, szSource);

	GlobalUnlock(hData);
	CloseClipboard();
	return szBuffer;
}

DWORD
WINAPI
ClipboardHandler(
	LPVOID	unused
)
{
	LPWSTR	szBuffer;

	szBuffer = RetrieveClipboardContent();
	if (!szBuffer)
	{
		Log(LOG_WARN, L"Cannot retrieve user clipboard.");
		return 0;
	}

	Log(LOG_INFO, L"User clipboard data:");
	wprintf(L"%s\n", szBuffer);
	free(szBuffer);

	return 0;
}