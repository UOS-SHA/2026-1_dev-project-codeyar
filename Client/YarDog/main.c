#include <Windows.h>
#include <stdio.h>
#include <locale.h>

#include "arg.h"
#include "hook.h"
#include "log.h"
#include "parse.h"
#include "policy.h"

void init(LPARGS pa)
{
	setlocale(LC_ALL, "ko-kr");

	InitLog(pa);
	InitPolicy(pa);
	InitHook(pa);
}

int wmain(int argc, wchar_t* argv[])
{
	LPARGS	pa;
	MSG		msg;

	pa = parse(argc, argv);
	if (!pa)
		return -1;

	init(pa);
	free(pa);

	while (GetMessageW(&msg, NULL, 0, 0))
	{
		TranslateMessage(&msg);
		DispatchMessageW(&msg);
	}
}