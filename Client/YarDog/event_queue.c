#include <Windows.h>

#include "arg.h"
#include "event_queue.h"
#include "log.h"

HANDLE	hMutex;
HANDLE	hThreads[WORKER_COUNT_MAX];
UINT	uiThreadCount;

DWORD
WINAPI
WorkerThread(
	LPVOID	lpParam
)
{

}

VOID
MutexPhase(
	VOID
)
{
	hMutex = CreateMutexW(
		NULL, FALSE, NULL
	);
	if (!hMutex)
	{
		Die(L"Failed to create mutex.");
		return;
	}

	WaitForSingleObject(hMutex, INFINITE);
	Log(LOG_INFO, L"Mutex created.");
}

VOID
ThreadPhase(
	LPARGS	pa
)
{
	INT		i;

	for (i = 0; i < pa->uiWorkerCount; i++)
	{

	}
}

VOID
InitEventQueue(
	LPARGS	pa
)
{
	MutexPhase();
	EventPhase();
	ThreadPhase(pa);

}