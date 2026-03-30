#include <Windows.h>

#include "arg.h"
#include "hook.h"
#include "policy.h"

HHOOK	hook;

LRESULT
CALLBACK
KeyboardHookProc(
	int		nCode,
	WPARAM	wParam,
	LPARAM	lParam
);

VOID
InitHook(
	LPARGS	pa
)
{
	UNREFERENCED_PARAMETER(pa);

	hook = SetWindowsHookExW(
		WH_KEYBOARD_LL,
		KeyboardHookProc,
		NULL,
		0
	);
}

#include <stdio.h>

LRESULT
CALLBACK
KeyboardHookProc(
	int		nCode,
	WPARAM	wParam,
	LPARAM	lParam
)
{
	LPKBDLLHOOKSTRUCT p = (LPKBDLLHOOKSTRUCT)lParam;

	if (nCode == HC_ACTION && wParam == WM_KEYDOWN)
		CheckPolicy(p);

	return CallNextHookEx(hook, nCode, wParam, lParam);
}