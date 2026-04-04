#pragma once

#include <Windows.h>

#define	DEF_VK_END		0x00
#define DEF_VK_STAR		0xFF
#define VK_LEN			256

#define SHORTCUT_MAX_LEN	32
#define LOG_TEXT_MAX_LEN	64

typedef struct __node
{
	BOOL			bIsAllowed;
	INT				vkey;
	struct __node*	children[VK_LEN];
	WCHAR			szLog[LOG_TEXT_MAX_LEN];
}	TREE, * LPTREE;

LPTREE
CreateRootNode(
	VOID
);

VOID
InsertShortcut(
	LPTREE	root,
	LPINT	sentence,
	INT		len,
	BOOL	bIsAllowed,
	LPWSTR	szLog
);

BOOL
FindShortcut(
	LPTREE	root,
	LPINT	sentence,
	INT		len,
	LPBOOL	pIsAllowed
);