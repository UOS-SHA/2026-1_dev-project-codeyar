#pragma once

#include <Windows.h>
#include "arg.h"

#define POLICY_FILE_MAX_LEN		4096
#define DEFAULT_POLICY			L"+CTRL,C,$Copy\n"		\
								L"+CTRL,V,$Paste\n"		\
								L"-CTRL,*,$Control\n"	\
								L"-ALT,TAB,$ALT+TAB\n"	\
								L"-WIN,TAB,$WIN+TAB\n"	\
								L"-ALT,*,$ALT\n"		\
								L"-WIN,*,$WIN\n"

#define CLIPBOARD_INSPECTION_GUID	L"846cf704-6728-4b16-99a1-6e514c362845"

VOID
InitPolicy(
	LPARGS	pa
);

VOID
CheckPolicy(
	LPKBDLLHOOKSTRUCT	pkhs
);

LPWSTR
GetPolicyBufferAddress(
	VOID
);

DWORD
WINAPI
ClipboardHandler(
	LPVOID	unused
);