#include <Windows.h>
#include <stdio.h>

#include "arg.h"
#include "hook.h"
#include "parse.h"
#include "policy.h"

void init(LPARGS pa)
{
	InitHook(pa);
	InitPolicy(pa);
}

int main(int argc, char* argv[])
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