#include <stdlib.h>
#include <string.h>

#include "arg.h"
#include "log.h"
#include "parse.h"

typedef struct
{
	char tag;
	char longtag[TAG_MAX_LEN];
	void (*handler)(LPARGS, char*);
}	PAIR, * LPPAIR;

void dummy_handler(LPARGS, char*);
void policy_handler(LPARGS, char*);
void loglevel_handler(LPARGS, char*);

PAIR pairs[] =
{
	{ 0, "", dummy_handler },
	{ 'p', "policy", policy_handler },				// file name follows
	{ 'l', "log-level", loglevel_handler },			// log level follows (quiet, default, talkative, verbose)
};

int compare_tag(char tag)
{
	int i;

	for (i = sizeof(pairs) / sizeof(PAIR) - 1; i > 0; i--)
		if (tag == pairs[i].tag)
			break;

	return i;
}

int compare_longtag(char* tag)
{
	int i;

	for (i = sizeof(pairs) / sizeof(PAIR) - 1; i > 0; i--)
		if (!strcmp(tag, pairs[i].longtag))
			break;

	return i;
}

LPARGS parse(int argc, char* argv[])
{
	LPARGS	pa;
	int		i;
	int		index;

	pa = malloc(sizeof(ARGS));

	for (i = 1; i < argc; i += 2)
	{
		index = 0;

		if (!strncmp("--", argv[i], 2))
			index = compare_longtag(argv[i] + 2);
		if (argv[i][0] == '-' && argv[i][2] == 0)
			index = compare_tag(argv[i][1]);
		if (!index)
			continue;

		pairs[index].handler(pa, argv[i + 1]);
	}

	return pa;
}

void dummy_handler(LPARGS pa, char* vec)
{
	return;
}

void policy_handler(LPARGS pa, char* vec)
{
	int		i;
	wchar_t buffer[MAX_PATH] = { 0, };

	for (i = 0; vec[i]; i++)
		buffer[i] = 0x00FF & vec[i];
	buffer[i] = 0;

	wcscpy_s(pa->szPolicyFileName, MAX_PATH, buffer);
}

void loglevel_handler(LPARGS pa, char* vec)
{
	int		i;
	char*	loglevels[] = {
		[LOG_LEVEL_QUIET] = "quiet",
		[LOG_LEVEL_DEFAULT] = "default",
		[LOG_LEVEL_TALKATIVE] = "talkative",
		[LOG_LEVEL_VERBOSE] = "verbose"
	};

	for (i = 0; i < sizeof(loglevels) / sizeof(char*); i++)
		if (!strcmp(vec, loglevels[i]))
			break;
	if (i == sizeof(loglevels) / sizeof(char*))
		i = 1;
	
	pa->uiLogLevel = i;
}