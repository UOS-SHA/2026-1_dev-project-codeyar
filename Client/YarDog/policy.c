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
	printf("Hey: %d\n", p->vkCode);

	// Detecting Ctrl + V
	if ((GetAsyncKeyState(VK_CONTROL) & 0x8000)
		&& p->vkCode == 'V')
		printf("[!] Ctrl + V\n");
	if ((GetAsyncKeyState(VK_MENU) & 0x8000)
		&& p->vkCode == VK_TAB)
		printf("[!] Alt + Tab\n");
}