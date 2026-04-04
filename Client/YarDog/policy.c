#include <Windows.h>

#include "arg.h"
#include "log.h"
#include "policy.h"
#include "tree.h"

/*
* Siho's Awesome Policy File Format
* 
* +: allow
* !: special action
* -: ban
* ,: combination
* *: any
* $: log message (at the end)
* 
* ex)
* +CTRL,C,$asdf
* !CTRL,V,$846cf704-6728-4b16-99a1-6e514c362845
* -CTRL,*,$asdf
* -ALT,TAB,$asdf
* -WIN,*,$asdf
*/

typedef struct
{
	LPCWSTR	szKeyname;
	UINT	vkey;
}	KEYMAP, * LPKEYMAP;

WCHAR	szPolicyFileBuffer[POLICY_FILE_MAX_LEN];
WCHAR	szPolicyOriginalBuffer[POLICY_FILE_MAX_LEN];
LPTREE	root;

KEYMAP		keymap[] = {
	{ L"CTRL", VK_CONTROL },
	{ L"ALT", VK_MENU },
	{ L"SHIFT", VK_SHIFT },
	{ L"TAB", VK_TAB },
	{ L"DEL", VK_DELETE },
	{ L"ENTER", VK_RETURN },
	{ L"WIN", VK_LWIN },
	{ L"ESC", VK_ESCAPE },
};

VOID
ReadDefaultPolicy(
	VOID
)
{
	wcscpy_s(szPolicyFileBuffer, POLICY_FILE_MAX_LEN, DEFAULT_POLICY);
}

VOID
ReadPolicy(
	LPWSTR	szFileName
)
{
	HANDLE	file;
	WCHAR	buffer[MAX_PATH];

	file = CreateFileW(
		szFileName,
		GENERIC_READ,
		FILE_SHARE_DELETE,
		NULL, OPEN_EXISTING,
		FILE_ATTRIBUTE_NORMAL,
		NULL
	);

	if (file == INVALID_HANDLE_VALUE)
	{
		GetCurrentDirectoryW(MAX_PATH, buffer);
		wcscat_s(buffer, MAX_PATH, L"\\");
		wcscat_s(buffer, MAX_PATH, szFileName);
		file = CreateFileW(
			buffer,
			GENERIC_READ,
			FILE_SHARE_DELETE,
			NULL, OPEN_EXISTING,
			FILE_ATTRIBUTE_NORMAL,
			NULL
		);

		if (file == INVALID_HANDLE_VALUE)
		{
			Log(LOG_INFO, L"Using default policy.");
			ReadDefaultPolicy();
			return;
		}
	}

	Log(LOG_INFO, L"File is loaded.");
	ReadFile(file, szPolicyFileBuffer, 2, NULL, NULL);
	ReadFile(file, szPolicyFileBuffer, POLICY_FILE_MAX_LEN, NULL, NULL);
	CloseHandle(file);
}

INT
BatchCompare(
	LPWSTR	szComp
)
{
	INT	i;

	for (i = sizeof(keymap) / sizeof(KEYMAP) - 1; i >= 0; i--)
		if (!wcscmp(keymap[i].szKeyname, szComp))
			break;
	return i;
}

VOID
ReadOneLine(
	LPWSTR	szLine
)
{
	wchar_t*	token;
	wchar_t*	context;
	BOOL		bIsAllowed;
	INT			sentence[SHORTCUT_MAX_LEN] = { 0, };
	INT			sentptr;
	INT			i;
	WCHAR		log[LOG_TEXT_MAX_LEN] = { 0, };

	switch (szLine[0])
	{
	case '+':
		bIsAllowed = TRUE;
		break;
	case '!':
	case '-':
		bIsAllowed = FALSE;
		break;
	default:
		return;
	}

	sentptr = 0;
	token = context = NULL;
	token = wcstok_s(szLine + 1, L",", &context);
	do
	{
		if (token[0] == ' ')
			token++;
		if (token[0] == 0)
			continue;

		if (token[0] == L'$')
		{
			wcscpy_s(log, LOG_TEXT_MAX_LEN, token + 1);
			break;
		}

		// Check for CTRL, ALT, ...
		for (i = 0; i < sizeof(keymap) / sizeof(KEYMAP); i++)
			if (!wcscmp(token, keymap[i].szKeyname))
				break;
		if (i < sizeof(keymap) / sizeof(KEYMAP))
		{
			sentence[sentptr++] = keymap[i].vkey;
			continue;
		}

		// Check for *
		if (!wcscmp(token, L"*"))
		{
			sentence[sentptr++] = DEF_VK_STAR;
			continue;
		}

		// Alphabets
		if (wcslen(token) == 1 && token[0] >= L'0' && token[0] <= L'Z')
		{
			sentence[sentptr++] = token[0];
			continue;
		}

		Log(LOG_ALRT, L"A line of policy is invalid!");
		return;
	} while (token = wcstok_s(NULL, L",", &context));

	InsertShortcut(root, sentence, sentptr, bIsAllowed, log);
}

VOID
InitPolicyTree(
	VOID
)
{
	wchar_t* token;
	wchar_t* context;

	token = context = NULL;
	token = wcstok_s(szPolicyFileBuffer, L"\r\n", &context);
	do
	{
		ReadOneLine(token);
	} while (token = wcstok_s(NULL, L"\r\n", &context));
}

VOID
InitPolicy(
	LPARGS	pa
)
{
	root = CreateRootNode();
	ReadPolicy(pa->szPolicyFileName);
	memcpy_s(
		szPolicyOriginalBuffer, POLICY_FILE_MAX_LEN,
		szPolicyFileBuffer, POLICY_FILE_MAX_LEN
	);
	InitPolicyTree();
}

INT	vkeys[] = {
	VK_CONTROL, VK_SHIFT, VK_MENU, VK_LWIN,
	VK_TAB, VK_RETURN, VK_DELETE, VK_ESCAPE
};

inline
DWORD
ConvertLR(
	DWORD	vkcode
)
{
	switch (vkcode)
	{
	case VK_LSHIFT:
	case VK_RSHIFT:
		return VK_SHIFT;
	case VK_LCONTROL:
	case VK_RCONTROL:
		return VK_CONTROL;
	case VK_LMENU:
	case VK_RMENU:
		return VK_MENU;
	}

	return vkcode;
}

inline
INT
MakeSentence(
	LPINT	sentence,
	DWORD	vkcode
)
{
	INT		i;
	INT		sentptr;
	INT		toadd;
	BOOL	vkInserted;
	BOOL	dict[256] = { 0, };

	vkcode = ConvertLR(vkcode);

	for (i = 0, sentptr = 0, vkInserted = FALSE; i < sizeof(vkeys) / sizeof(INT); i++)
	{
		if (GetAsyncKeyState(vkeys[i]) & 0x8000)
			toadd = vkeys[i];
		else
			continue;

		if (dict[toadd])
			continue;

		dict[toadd] = TRUE;
		sentence[sentptr++] = toadd;
	}
	if (!dict[vkcode])
		sentence[sentptr++] = vkcode;
	
	return sentptr;
}

typedef struct
{
	LPCWSTR		szGUID;
	DWORD		(*pHandler)(LPVOID);
}	GUIDPAIR;

GUIDPAIR	GUIDs[] = {
	[0] = { NULL, NULL },
	{ CLIPBOARD_INSPECTION_GUID, ClipboardHandler },
};

INT
CheckGUID(
	LPWSTR	szLog
)
{
	INT		i;

	if (wcslen(szLog) != wcslen(GUIDs[1].szGUID))
		return 0;

	for (i = sizeof(GUIDs) / sizeof(GUIDPAIR) - 1; i > 0; i--)
		if (!wcscmp(szLog, GUIDs[i].szGUID))
			break;
	return i;
}

VOID
RunGUID(
	LPWSTR	szLog
)
{
	INT		ret;
	HANDLE	hThread;

	ret = CheckGUID(szLog);
	if (!ret)
		return;

	hThread = CreateThread(
		NULL, 0, GUIDs[ret].pHandler,
		NULL, 0, NULL
	);
	if (hThread)
		CloseHandle(hThread);
}

#include <stdio.h>		// DEBUG!!

VOID
CheckPolicy(
	LPKBDLLHOOKSTRUCT	p
)
{
	INT		sentence[SHORTCUT_MAX_LEN] = { 0, };
	INT		len;
	BOOL	bIsAllowed;
	LPWSTR	szLog;

	len = MakeSentence(sentence, p->vkCode);
	
	if (!FindShortcut(root, sentence, len, &bIsAllowed, &szLog)
		|| bIsAllowed)
		return;

	// NOT ALLOWED!!
	// DO SOMETHING!!
	wprintf(L"%s\n", szLog);
	RunGUID(szLog);
}

LPWSTR
GetPolicyBufferAddress(
	VOID
)
{
	return szPolicyOriginalBuffer;
}