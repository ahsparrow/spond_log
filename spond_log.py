import asyncio
from datetime import date
import json
import os
from spond import spond

groupid = "DFD7AD3B53E2406FB51E0C81728ADC2F"


async def spond_log(username=username, password=password):
    session = spond.Spond(username=username, password=password)

    year = date.today().year
    log_file = f"lockerley_{year}.json"
    if not os.path.isfile(log_file):
        log = {"members": [], "events": []}
    else:
        with open(log_file) as f:
            log = json.load(f)

    existing_event_ids = [e["id"] for e in log["events"]]

    def get_existing_member_ids():
        return [m["id"] for m in log["members"]]

    min_start = date(year, 1, 1)
    events = await session.get_events(
        group_id=groupid,
        min_start=min_start,
    )
    events.sort(key=lambda x: x["startTimestamp"])

    for e in events:
        if e["id"] in existing_event_ids or not e["expired"]:
            continue

        for m in e["recipients"]["group"]["members"]:
            if m["id"] in get_existing_member_ids():
                continue

            log["members"].append(
                {"id": m["id"], "firstName": m["firstName"], "lastName": m["lastName"]}
            )

        event = {
            "id": e["id"],
            "heading": e["heading"],
            "startTimestamp": e["startTimestamp"],
            "accepted": e["responses"]["acceptedIds"],
            "declined": e["responses"]["declinedIds"],
            "unanswered": e["responses"]["unansweredIds"],
        }
        if "cancelled" in e:
            event["cancelled"] = e["cancelled"]

        log["events"].append(event)

    with open(log_file, "wt") as f:
        json.dump(log, f, sort_keys=True, indent=4)

    await session.clientsession.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("username")
    parser.add_argument("password")
    args = parser.parse_args()

    asyncio.run(spond_log(args.username, args.password))
