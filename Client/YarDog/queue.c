#include <stdlib.h>

#include "event_queue.h"

typedef struct __event_node
{
	ITEM					item;
	struct __event_node*	next;
}	NODE, * LPNODE;

LPNODE	head;
LPNODE	tail;
/*
* a <- b <- c <- d
* ^              ^
* |              |
* head           tail
*/

LPNODE
CreateQueueNode(
	ITEM	item
)
{
	LPNODE	ret;

	ret = malloc(sizeof(NODE));
	if (!ret)
		return NULL;

	ret->item = item;
	ret->next = NULL;
}

VOID
Enqueue(
	ITEM	item
)
{
	LPNODE	newnode;

	newnode = CreateQueueNode(item);
	if (!newnode)
		return;

	if (!head)
		head = tail = newnode;
	else
	{
		head->next = newnode;
		head = newnode;
	}
}

ITEM
Dequeue(
	VOID
)
{
	LPNODE	delnode;
	ITEM	temp = {
		.bIsValid = FALSE
	};

	delnode = tail;
	if (!delnode)
		return temp;
	
	tail = delnode->next;
	if (!tail)
		head = NULL;

	temp = delnode->item;
	free(delnode);
	return temp;
}