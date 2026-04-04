#include <Windows.h>
#include <stdlib.h>

#include "tree.h"

inline
LPTREE
CreateNode(
	BOOL	bIsAllowed,
	INT		vkey
)
{
	LPTREE	ret;

	ret = malloc(sizeof(TREE));
	if (!ret)
		return NULL;

	ret->bIsAllowed = bIsAllowed;
	ret->vkey = vkey;
	memset(ret->children, 0, VK_LEN * sizeof(LPTREE));
	memset(ret->szLog, 0, LOG_TEXT_MAX_LEN * sizeof(WCHAR));

	return ret;
}

LPTREE
CreateRootNode(
	VOID
)
{
	return CreateNode(FALSE, DEF_VK_STAR);
}

VOID
InsertShortcutRecursive(
	LPTREE	root,
	LPINT	sentence,
	INT		len,
	BOOL	bIsAllowed,
	LPWSTR	szLog
)
{
	LPTREE	child;

	if (!root)
		return;

	if (len == 0)
	{
		root->bIsAllowed = bIsAllowed;
		root->vkey = DEF_VK_END;
		wcscpy_s(root->szLog, LOG_TEXT_MAX_LEN, szLog);

		return;
	}

	child = root->children[sentence[0]];
	if (!child)
		child = CreateNode(FALSE, sentence[0]);
	if (!child)
		return;
	root->children[sentence[0]] = child;

	InsertShortcutRecursive(
		child, sentence + 1,
		len - 1, bIsAllowed,
		szLog
	);
}

VOID
InsertShortcut(
	LPTREE	root,
	LPINT	sentence,
	INT		len,
	BOOL	bIsAllowed,
	LPWSTR	szLog
)
{
	if (!root || len > SHORTCUT_MAX_LEN)
		return;

	InsertShortcutRecursive(
		root, sentence,
		len, bIsAllowed,
		szLog
	);
}

#include <stdio.h>

BOOL
FindShortcut(
	LPTREE	root,
	LPINT	sentence,
	INT		len,
	LPBOOL	pIsAllowed,
	LPWSTR*	dpLog
)
{
	LPTREE	child;

	if (!root || len > SHORTCUT_MAX_LEN)
		return FALSE;

	if (len == 0)
	{
		if (root->vkey != DEF_VK_END)
			return FALSE;
		*pIsAllowed = root->bIsAllowed;
		*dpLog = root->szLog;

		return TRUE;
	}

	child = root->children[sentence[0]];
	if (!child)
		child = root->children[DEF_VK_STAR];

	return FindShortcut(
		child, sentence + 1,
		len - 1, pIsAllowed,
		dpLog
	);
}