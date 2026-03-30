#pragma once

#include <Windows.h>
#include "arg.h"

VOID
InitPolicy(
	LPARGS	pa
);

VOID
CheckPolicy(
	LPKBDLLHOOKSTRUCT	pkhs
);