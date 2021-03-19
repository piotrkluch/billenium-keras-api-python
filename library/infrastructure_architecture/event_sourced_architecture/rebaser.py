from functools import singledispatch

from infrastructure.event_sourced_repos.work_item_repository import WorkItemRepository
from kanban.domain.model.workitem import WorkItem, register_new_work_item


class RebaseError(Exception):
    pass


def rebase(unit_of_work, events):
    r = Rebaser(unit_of_work)
    r.rebase(events)

class Rebaser:
    """Rebase an event stream onto a domain model.

    Wanna grow
    Up to be
    Be a rebaser (rebaser)
    Rebaser, (rebaser)
    Rebaser, (rebaser)
    Rebaser, (rebaser)
    Rebaser, (rebaser)
    Rebaser, (rebaser)
    """

    def __init__(self, unit_of_work):
        self._unit_of_work = unit_of_work
        self._id_map = {}  # {old_id: new_id}

    def rebase(self, events):
        # Interpret the event stream and dispatch equivalent commands.
        for event in events:
            reapply(event, self)

    def add_id_mapping(self, old_id, new_id):
        if old_id in self._id_map:
            raise ValueError("ID {} is already mapped to ID {} so cannot be mapped to ID {}"
                             .format(old_id, self._id_map[old_id], new_id))
        return self._id_map[old_id, new_id]

    def map_id(self, old_id):
        return self._id_map.get(old_id, old_id)


@singledispatch
def reapply(event, rebaser):
    raise NotImplementedError


@reapply.register(WorkItem.Created)
def _(event, rebaser):
    work_item_id = event.aggregate_id
    work_item_repo = rebaser._unit_of_work.using(WorkItemRepository)
    try:
        work_item_repo.work_item_with_id(work_item_id)
    except ValueError:
        pass  # In this case we're expecting failure
    else:
        raise RebaseError("WorkItem with id {} already exists".format(work_item_id))
    work_item = register_new_work_item(event.name, event.due_date, event.content)
    rebaser.add_id_mapping(work_item_id, work_item.id)
    work_item_repo.put(work_item)


@reapply.register(WorkItem.Discarded)
def _(event, rebaser):
    work_item_id = rebaser.map_id(event.aggregate_id)
    work_item_repo = rebaser._unit_of_work.using(WorkItemRepository)
    work_item_repo.discard(work_item_id)


@reapply.register(WorkItem.NameChanged)
def _(event, rebaser):
    work_item_id = rebaser.map_id(event.aggregate_id)
    work_item_repo = rebaser._unit_of_work.using(WorkItemRepository)
    work_item = work_item_repo.work_item_with_id(work_item_id)
    work_item.name = event.name


@reapply.register(WorkItem.DueDateChanged)
def _(event, rebaser):
    work_item_id = rebaser.map_id(event.aggregate_id)
    work_item_repo = rebaser._unit_of_work.using(WorkItemRepository)
    work_item = work_item_repo.work_item_with_id(work_item_id)
    work_item.due_date = event.due_date


@reapply.register(WorkItem.ContentChanged)
def _(event, rebaser):
    work_item_id = rebaser.map_id(event.aggregate_id)
    work_item_repo = rebaser._unit_of_work.using(WorkItemRepository)
    work_item = work_item_repo.work_item_with_id(work_item_id)
    work_item.content = event.content

