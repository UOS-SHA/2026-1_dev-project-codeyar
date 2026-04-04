#include <stdlib.h>
#include <string.h>

#include "arg.h"
#include "log.h"
#include "parse.h"

#define false	0
#define true	1

#define MUST_BE_HANDLED		(1 << 8)
#define HAS_BEEN_HANDLED	(1 << 4)
#define NEEDS_DEFAULT		(1 << 2)

#define HANDLED(pair)		((pair).handled |= HAS_BEEN_HANDLED)
#define CHECK(pair)			(!(((pair).handled & MUST_BE_HANDLED) && !((pair).handled & HAS_BEEN_HANDLED)))
#define CHECK_DEFAULT(pair)	(((pair).handled & NEEDS_DEFAULT) && (!HANDLED(pair)))

typedef struct
{
	wchar_t tag;
	wchar_t longtag[TAG_MAX_LEN];
	int (*handler)(LPARGS, wchar_t*);
	int handled;
}	PAIR, * LPPAIR;

int dummy_handler(LPARGS, wchar_t*);
int policy_handler(LPARGS, wchar_t*);
int loglevel_handler(LPARGS, wchar_t*);
int id_handler(LPARGS, wchar_t*);
int name_handler(LPARGS, wchar_t*);
int worker_handler(LPARGS, wchar_t*);

PAIR pairs[] =
{
	{ 0, L"", dummy_handler, 0 },
	{ L'p', L"policy", policy_handler, 0 },						// file name follows
	{ L'l', L"log-level", loglevel_handler, NEEDS_DEFAULT },	// log level follows (quiet, default, talkative, verbose)
	{ 0, L"student-id", id_handler, MUST_BE_HANDLED },			// id
	{ 0, L"student-name", name_handler, MUST_BE_HANDLED },		// name
	{ L'w', L"worker-count", worker_handler, NEEDS_DEFAULT },
};

int compare_tag(wchar_t tag)
{
	int i;

	for (i = sizeof(pairs) / sizeof(PAIR) - 1; i > 0; i--)
		if (tag == pairs[i].tag)
			break;

	return i;
}

int compare_longtag(wchar_t* tag)
{
	int i;

	for (i = sizeof(pairs) / sizeof(PAIR) - 1; i > 0; i--)
		if (!wcscmp(tag, pairs[i].longtag))
			break;

	return i;
}

LPARGS parse(int argc, wchar_t* argv[])
{
	LPARGS	pa;
	int		i;
	int		index;

	pa = malloc(sizeof(ARGS));
	memset(pa, 0, sizeof(ARGS));

	for (i = 1; i < argc; i += 2)
	{
		index = 0;

		if (!wcsncmp(L"--", argv[i], 2))
			index = compare_longtag(argv[i] + 2);
		if (argv[i][0] == L'-' && argv[i][2] == 0)
			index = compare_tag(argv[i][1]);
		if (!index)
			continue;

		pairs[index].handler(pa, argv[i + 1]);
		HANDLED(pairs[index]);
	}

	for (i = 0; i < sizeof(pairs) / sizeof(PAIR); i++)
	{
		if (!CHECK(pairs[i]))
		{
			Die(L"Necessary argument not passed!");
			return NULL;
		}
		if (CHECK_DEFAULT(pairs[i]))
		{
			pairs[i].handler(pa, NULL);
			continue;
		}
	}

	return pa;
}

int dummy_handler(LPARGS pa, wchar_t* vec)
{
	return true;
}

int policy_handler(LPARGS pa, wchar_t* vec)
{
	wcscpy_s(pa->szPolicyFileName, MAX_PATH, vec);
	return true;
}

int loglevel_handler(LPARGS pa, wchar_t* vec)
{
	int			i;
	wchar_t*	loglevels[] = {
		[LOG_LEVEL_QUIET] = L"quiet",
		[LOG_LEVEL_DEFAULT] = L"default",
		[LOG_LEVEL_TALKATIVE] = L"talkative",
		[LOG_LEVEL_VERBOSE] = L"verbose"
	};

	if (!vec)
	{
		pa->uiLogLevel = LOG_LEVEL_DEFAULT;
		return true;
	}

	for (i = 1; i < sizeof(loglevels) / sizeof(wchar_t*); i++)
		if (!wcscmp(vec, loglevels[i]))
			break;
	if (i == sizeof(loglevels) / sizeof(wchar_t*))
		return false;
	
	pa->uiLogLevel = i;
	return true;
}

int id_handler(LPARGS pa, wchar_t* vec)
{
	wcscpy_s(pa->szStudentID, 16, vec);
	return true;
}

int name_handler(LPARGS pa, wchar_t* vec)
{
	wcscpy_s(pa->szStudentName, 16, vec);
	return true;
}

int worker_handler(LPARGS pa, wchar_t* vec)
{
	if (!vec)
	{
		pa->uiWorkerCount = WORKER_COUNT_DEFAULT;
		return true;
	}
	
	pa->uiWorkerCount = _wtoi(vec);
	if (pa->uiWorkerCount == 0)
		pa->uiWorkerCount = WORKER_COUNT_DEFAULT;
	else if (pa->uiWorkerCount < WORKER_COUNT_MIN)
		pa->uiWorkerCount = WORKER_COUNT_MIN;
	else if (pa->uiWorkerCount > WORKER_COUNT_MAX)
		pa->uiWorkerCount = WORKER_COUNT_MAX;

	return true;
}