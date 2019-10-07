BASE_URL = "https://slack.com"
LEGACY_TOKEN = "xoxp-785774634720-774287332483-785305125732-6805609eb0911b3cae48dbf028d0ffcc"


def get_channel_list(session, exclude_archives=True):
    resp = session.get(BASE_URL + "/api/channels.list",
                            params={"token": LEGACY_TOKEN,
                                    'exclude_archived': exclude_archives})
    channel_names = [channel["name"] for channel in resp.json()['channels']]
    return channel_names
