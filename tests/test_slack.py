import pytest
import random
import requests
from unittest import TestCase
from dotted_dict import DottedDict as dot
from generic.utilities import (LEGACY_TOKEN, BASE_URL, get_channel_list)


CREATOR_ID = "UNS8F9SE7"
channel_id = ""
new_channel_name = ""
common_params = {"token": LEGACY_TOKEN,
                 "validate": "true"}

"""
● Signup for Slack API and sign in
● Generate API Token https://api.slack.com/custom-integrations/legacy-tokens
● Please refer the API Doc @ https://api.slack.com/methods
"""

class TestSlackChannels(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = requests.session()
        cls.channel_name = "testchannel" + str(random.randint(100000, 999999))

    def setUp(self):
        self.params = common_params

    @pytest.mark.order1
    def test1_create_channel(self):
        """Create a new Channel"""
        print("name of the channel is: " + self.channel_name)
        self.params["name"] = self.channel_name
        resp = self.session.get(BASE_URL + "/api/channels.create", params=self.params)
        print(resp.json())
        self.assertTrue(resp.status_code == 200)
        resp = dot(resp.json())

        # verifying creator id in response
        self.assertEquals(resp.channel.creator, CREATOR_ID)

        self.assertTrue(resp.channel.is_channel)

        # get channel id for later use
        global channel_id
        channel_id = resp.channel.id

    @pytest.mark.order2
    def test2_join_channel(self):
        """Join the newly created Channel"""
        self.params['name'] = self.channel_name
        resp = self.session.post(BASE_URL + "/api/channels.join", params=self.params)
        assert resp.status_code == 200
        resp = dot(resp.json())
        # verifying channel id in response
        self.assertEquals(resp.channel.id, channel_id)
        # verifying creator id in response
        self.assertEquals(resp.channel.creator, CREATOR_ID)
        # verifying that person is in the list of channel members
        self.assertTrue(CREATOR_ID in resp.channel.members)

    @pytest.mark.order3
    def test3_rename_channel(self):
        """Rename the Channel and
        List all Channels and Validate if the Channel name has changed successfully
        """
        global new_channel_name
        new_channel_name = "newchannel" + str(random.randint(100000, 999999))
        self.params["channel"] = channel_id
        self.params["name"] = new_channel_name
        resp = self.session.post(BASE_URL + "/api/channels.rename", params=self.params)
        print(resp.json())
        assert resp.status_code == 200
        resp = dot(resp.json())
        # verifying creator id in response
        self.assertEquals(resp.channel.creator, CREATOR_ID)
        # verifying channel id in response
        self.assertEquals(resp.channel.id, channel_id)

        # verify channel's new name
        self.assertEquals(resp.channel.name, new_channel_name)

        # get list of all the channels
        channel_names = get_channel_list(self.session)
        print(channel_names)
        assert new_channel_name in channel_names

    @pytest.mark.order4
    def test4_archive_channel(self):
        """
        Archive the Channel
        Validate if the Channel is archived successfully
        """
        params = {"token": LEGACY_TOKEN,
                  "channel": channel_id}
        resp = self.session.post(BASE_URL + "/api/channels.archive", params)
        assert resp.status_code == 200
        self.assertTrue(resp.json()["ok"])

        # to verify whether channel is archived
        # get list of all the channels including archived
        all_channels = get_channel_list(self.session, exclude_archives=False)
        # get list of all the channels excluding archive
        channel_excluding_archives = get_channel_list(self.session)

        # taking the difference will give only archived channels list
        archived_channels = list(set(all_channels) - set(channel_excluding_archives))
        print(archived_channels)
        assert new_channel_name in archived_channels
