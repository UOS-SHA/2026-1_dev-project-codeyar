#include <Windows.h>

#include "arg.h"
#include "policy.h"

#include <stdio.h>	// DEBUG!!

VOID
InitPolicy(
	LPARGS	pa
)
{

}

VOID
CheckPolicy(
	LPKBDLLHOOKSTRUCT	p
)
{
	// Detecting Ctrl + V
	if ((GetAsyncKeyState(VK_CONTROL) & 0x8000)
		&& p->vkCode == 'V')
		printf("[!] Ctrl + V\n");
}