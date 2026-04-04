#pragma once

#include <Windows.h>
#include "arg.h"

#define POLICY_FILE_MAX_LEN		4096
#define DEFAULT_POLICY			L"+CTRL,C,$Copy\n"		\
								L"+CTRL,V,$Paste\n"		\
								L"-CTRL,*,$Control\n"	\
								L"-ALT,*,$ALT\n"		\
								L"-WIN,*,$WIN\n"

VOID
InitPolicy(
	LPARGS	pa
);

VOID
CheckPolicy(
	LPKBDLLHOOKSTRUCT	pkhs
);