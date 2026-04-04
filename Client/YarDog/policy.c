#include <Windows.h>

#include "arg.h"
#include "log.h"
#include "policy.h"
#include "tree.h"

/*
* Siho's Awesome Policy File Format
* 
* +: allow
* -: ban
* ,: combination
* *: any
* $: log message (at the end)
* 
* ex)
* +CTRL,C,$asdf
* +CTRL,V,$asdf
* -CTRL,*,$asdf
* -ALT,TAB,$asdf
* -WIN,*,$asdf
* 
* CTRL + C and CTRL + V is an exception; they are recorded anyways.
*/

typedef struct
{
	LPCWSTR	szKeyname;
	UINT	vkey;
}	KEYMAP, * LPKEYMAP;

WCHAR	szPolicyFileBuffer[POLICY_FILE_MAX_LEN];
LPTREE	root;

KEYMAP		keymap[] = {
	{ L"CTRL", VK_CONTROL },
	{ L"ALT", VK_MENU },
	{ L"SHIFT", VK_SHIFT },
	{ L"TAB", VK_TAB },
	{ L"DEL", VK_DECIMAL },
	{ L"ENTER", VK_RETURN },
	{ L"WIN", VK_LWIN },
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
		ReadDefaultPolicy();
		return;
	}

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
	token = wcstok_s(szPolicyFileBuffer, L"\n", &context);
	do
	{
		ReadOneLine(token);
	} while (token = wcstok_s(NULL, L"\n", &context));
}

VOID
InitPolicy(
	LPARGS	pa
)
{
	root = CreateRootNode();
	ReadPolicy(pa->szPolicyFileName);
	InitPolicyTree();
}

INT	vkeys[] = {
	VK_CONTROL, VK_SHIFT, VK_MENU, VK_LWIN,
	VK_TAB, VK_RETURN, VK_DECIMAL
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
	sentence[sentptr++] = vkcode;
	
	return sentptr;
}

#include <stdio.h>

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
	
}