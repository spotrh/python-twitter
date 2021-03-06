# encoding: utf-8

import json
import sys
import unittest

import twitter

import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)

import responses


class ErrNull(object):
    """ Suppress output of tests while writing to stdout or stderr. This just
    takes in data and does nothing with it.
    """

    def write(self, data):
        pass


class ApiTest(unittest.TestCase):

    def setUp(self):
        self.api = twitter.Api(
            consumer_key='test',
            consumer_secret='test',
            access_token_key='test',
            access_token_secret='test',
            sleep_on_rate_limit=False)
        self.base_url = 'https://api.twitter.com/1.1'
        self._stderr = sys.stderr
        sys.stderr = ErrNull()

    def tearDown(self):
        sys.stderr = self._stderr
        pass

    def testApiSetUp(self):
        self.assertRaises(
            twitter.TwitterError,
            lambda: twitter.Api(consumer_key='test'))

    def testSetAndClearCredentials(self):
        api = twitter.Api()
        api.SetCredentials(consumer_key='test',
                           consumer_secret='test',
                           access_token_key='test',
                           access_token_secret='test')
        self.assertEqual(api._consumer_key, 'test')
        self.assertEqual(api._consumer_secret, 'test')
        self.assertEqual(api._access_token_key, 'test')
        self.assertEqual(api._access_token_secret, 'test')

        api.ClearCredentials()

        self.assertFalse(all([
            api._consumer_key,
            api._consumer_secret,
            api._access_token_key,
            api._access_token_secret
        ]))

    @responses.activate
    def testApiRaisesAuthErrors(self):
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/search/tweets.json?count=15&result_type=mixed&q=python',
            body='',
            match_querystring=True,
            status=200)
        api = twitter.Api()
        api.SetCredentials(consumer_key='test',
                           consumer_secret='test',
                           access_token_key='test',
                           access_token_secret='test')
        api._Api__auth = None
        self.assertRaises(twitter.TwitterError, lambda: api.GetFollowers())

    @responses.activate
    def testGetHelpConfiguration(self):
        with open('testdata/get_help_configuration.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/help/configuration.json',
            body=resp_data,
            status=200)
        resp = self.api.GetHelpConfiguration()
        self.assertEqual(resp.get('short_url_length_https'), 23)

    @responses.activate
    def testGetShortUrlLength(self):
        with open('testdata/get_help_configuration.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/help/configuration.json',
            body=resp_data,
            status=200)
        resp = self.api.GetShortUrlLength()
        self.assertEqual(resp, 23)
        resp = self.api.GetShortUrlLength(https=True)
        self.assertEqual(resp, 23)

    @responses.activate
    def testGetSearch(self):
        with open('testdata/get_search.json') as f:
            resp_data = f.read()
            responses.add(
                responses.GET,
                'https://api.twitter.com/1.1/search/tweets.json?count=15&result_type=mixed&q=python',
                body=resp_data,
                match_querystring=True,
                status=200)
        resp = self.api.GetSearch(term='python')
        self.assertEqual(len(resp), 1)
        self.assertTrue(type(resp[0]), twitter.Status)
        self.assertEqual(resp[0].id, 674342688083283970)

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetSearch(since_id='test'))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetSearch(max_id='test'))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetSearch(term='test', count='test'))
        self.assertFalse(self.api.GetSearch())

    @responses.activate
    def testGetSeachRawQuery(self):
        with open('testdata/get_search_raw.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/search/tweets.json?q=twitter%20&result_type=recent&since=2014-07-19&count=100',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetSearch(raw_query="q=twitter%20&result_type=recent&since=2014-07-19&count=100")
        self.assertTrue([type(status) is twitter.Status for status in resp])
        self.assertTrue(['twitter' in status.text for status in resp])

    @responses.activate
    def testGetSearchGeocode(self):
        with open('testdata/get_search_geocode.json') as f:
            resp_data = f.read()
            responses.add(
                responses.GET,
                'https://api.twitter.com/1.1/search/tweets.json?result_type=mixed&count=15&geocode=37.781157%2C-122.398720%2C100mi&q=python',
                body=resp_data,
                match_querystring=True,
                status=200)
        resp = self.api.GetSearch(
            term="python",
            geocode=('37.781157', '-122.398720', '100mi'))
        status = resp[0]
        self.assertTrue(status, twitter.Status)
        self.assertTrue(status.geo)
        self.assertEqual(status.geo['type'], 'Point')

    @responses.activate
    def testGetUsersSearch(self):
        with open('testdata/get_users_search.json') as f:
            resp_data = f.read()
            responses.add(
                responses.GET,
                'https://api.twitter.com/1.1/users/search.json?count=20&q=python',
                body=resp_data,
                match_querystring=True,
                status=200)
        resp = self.api.GetUsersSearch(term='python')
        self.assertEqual(type(resp[0]), twitter.User)
        self.assertEqual(len(resp), 20)
        self.assertEqual(resp[0].id, 63873759)
        self.assertRaises(twitter.TwitterError,
                          lambda: self.api.GetUsersSearch(term='python',
                                                          count='test'))

    @responses.activate
    def testGetTrendsCurrent(self):
        with open('testdata/get_trends_current.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/trends/place.json?id=1',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetTrendsCurrent()
        self.assertTrue(type(resp[0]) is twitter.Trend)

    @responses.activate
    def testGetHomeTimeline(self):
        with open('testdata/get_home_timeline.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/home_timeline.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetHomeTimeline()
        status = resp[0]
        self.assertEqual(type(status), twitter.Status)
        self.assertEqual(status.id, 674674925823787008)

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetHomeTimeline(count='literally infinity'))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetHomeTimeline(count=4000))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetHomeTimeline(max_id='also infinity'))
        self.assertRaises(twitter.TwitterError,
                          lambda: self.api.GetHomeTimeline(
                              since_id='still infinity'))


        # TODO: Get data for this call against which we can test exclusions.
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/home_timeline.json?count=100&max_id=674674925823787008&trim_user=1',
            body=resp_data,
            match_querystring=True,
            status=200)
        self.assertTrue(self.api.GetHomeTimeline(count=100,
                                                 trim_user=True,
                                                 max_id=674674925823787008))

    @responses.activate
    def testGetUserTimeline(self):
        with open('testdata/get_user_timeline.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/user_timeline.json?user_id=673483',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetUserTimeline(user_id=673483)
        self.assertTrue(type(resp[0]) is twitter.Status)
        self.assertTrue(type(resp[0].user) is twitter.User)
        self.assertEqual(resp[0].user.id, 673483)

        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=dewitt',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetUserTimeline(screen_name='dewitt')
        self.assertEqual(resp[0].id, 675055636267298821)
        self.assertTrue(resp)

    @responses.activate
    def testGetRetweets(self):
        with open('testdata/get_retweets.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/retweets/397.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetRetweets(statusid=397)
        self.assertTrue(type(resp[0]) is twitter.Status)
        self.assertTrue(type(resp[0].user) is twitter.User)

    @responses.activate
    def testGetRetweeters(self):
        with open('testdata/get_retweeters.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/retweeters/ids.json?id=397',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetRetweeters(status_id=397)
        self.assertTrue(type(resp) is list)
        self.assertTrue(type(resp[0]) is int)

    @responses.activate
    def testGetBlocks(self):
        with open('testdata/get_blocks.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/blocks/list.json?cursor=-1',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetBlocks()
        self.assertTrue(type(resp) is list)
        self.assertTrue(type(resp[0]) is twitter.User)
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0].screen_name, 'RedScareBot')

    @responses.activate
    def testGetFriendIDs(self):
        # First request for first 5000 friends
        with open('testdata/get_friend_ids_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/friends/ids.json?screen_name=EricHolthaus&count=5000&stringify_ids=False&cursor=-1'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        # Second (last) request for remaining friends
        with open('testdata/get_friend_ids_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/friends/ids.json?count=5000&screen_name=EricHolthaus&stringify_ids=False&cursor=1417903878302254556'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        resp = self.api.GetFriendIDs(screen_name='EricHolthaus')
        self.assertTrue(type(resp) is list)
        self.assertEqual(len(resp), 6452)
        self.assertTrue(type(resp[0]) is int)

        # Error checking
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetFriendIDs(total_count='infinity'))

    @responses.activate
    def testGetFriendIDsPaged(self):
        with open('testdata/get_friend_ids_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/friends/ids.json?count=5000&cursor=-1&screen_name=EricHolthaus&stringify_ids=False'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        ncursor, pcursor, resp = self.api.GetFriendIDsPaged(screen_name='EricHolthaus')
        self.assertLessEqual(len(resp), 5000)
        self.assertTrue(ncursor)
        self.assertFalse(pcursor)

    @responses.activate
    def testGetFriendsPaged(self):
        with open('testdata/get_friends_paged.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/friends/list.json?screen_name=codebear&count=200&cursor=-1&skip_status=False&include_user_entities=True'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        ncursor, pcursor, resp = self.api.GetFriendsPaged(screen_name='codebear', count=200)
        self.assertEqual(ncursor, 1494734862149901956)
        self.assertEqual(pcursor, 0)
        self.assertEqual(len(resp), 200)
        self.assertTrue(type(resp[0]) is twitter.User)

        with open('testdata/get_friends_paged_uid.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/friends/list.json?user_id=12&skip_status=False&cursor=-1&include_user_entities=True&count=200'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        ncursor, pcursor, resp = self.api.GetFriendsPaged(user_id=12, count=200)
        self.assertEqual(ncursor, 1510410423140902959)
        self.assertEqual(pcursor, 0)
        self.assertEqual(len(resp), 200)
        self.assertTrue(type(resp[0]) is twitter.User)

        with open('testdata/get_friends_paged_additional_params.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/friends/list.json?include_user_entities=True&user_id=12&count=200&cursor=-1&skip_status=True'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        ncursor, pcursor, resp = self.api.GetFriendsPaged(user_id=12,
                                                          count=200,
                                                          skip_status=True,
                                                          include_user_entities=True)
        self.assertEqual(ncursor, 1510492845088954664)
        self.assertEqual(pcursor, 0)
        self.assertEqual(len(resp), 200)
        self.assertTrue(type(resp[0]) is twitter.User)

    @responses.activate
    def testGetFriends(self):

        """
        This is tedious, but the point is to add a responses endpoint for
        each call that GetFriends() is going to make against the API and
        have it return the appropriate json data.
        """

        cursor = -1
        for i in range(0, 5):
            with open('testdata/get_friends_{0}.json'.format(i)) as f:
                resp_data = f.read()
            endpoint = '/friends/list.json?screen_name=codebear&count=200&skip_status=False&include_user_entities=True&cursor={0}'.format(cursor)

            responses.add(
                responses.GET,
                '{base_url}{endpoint}'.format(
                    base_url=self.api.base_url,
                    endpoint=endpoint),
                body=resp_data, match_querystring=True, status=200)

            cursor = json.loads(resp_data)['next_cursor']

        resp = self.api.GetFriends(screen_name='codebear')
        self.assertEqual(len(resp), 819)

    @responses.activate
    def testGetFriendsWithLimit(self):
        with open('testdata/get_friends_0.json') as f:
            resp_data = f.read()

        responses.add(
            responses.GET,
            '{base_url}/friends/list.json?include_user_entities=True&skip_status=False&screen_name=codebear&count=200&cursor=-1'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        resp = self.api.GetFriends(screen_name='codebear', total_count=200)
        self.assertEqual(len(resp), 200)

    def testFriendsErrorChecking(self):
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetFriends(screen_name='jack',
                                        total_count='infinity'))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetFriendsPaged(screen_name='jack',
                                             count='infinity'))

    @responses.activate
    def testGetFollowersIDs(self):
        # First request for first 5000 followers
        with open('testdata/get_follower_ids_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/ids.json?count=5000&cursor=-1&screen_name=GirlsMakeGames'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        # Second (last) request for remaining followers
        with open('testdata/get_follower_ids_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/ids.json?cursor=1482201362283529597&count=5000&screen_name=GirlsMakeGames'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        resp = self.api.GetFollowerIDs(screen_name='GirlsMakeGames')
        self.assertTrue(type(resp) is list)
        self.assertEqual(len(resp), 7885)
        self.assertTrue(type(resp[0]) is int)

        # Error checking
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetFollowerIDs(count='infinity'))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetFollowerIDs(total_count='infinity'))

    @responses.activate
    def testGetFollowers(self):
        # First request for first 200 followers
        with open('testdata/get_followers_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/list.json?include_user_entities=True&count=200&screen_name=himawari8bot&skip_status=False&cursor=-1'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        # Second (last) request for remaining followers
        with open('testdata/get_followers_1.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/list.json?include_user_entities=True&skip_status=False&count=200&screen_name=himawari8bot&cursor=1516850034842747602'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetFollowers(screen_name='himawari8bot')
        self.assertTrue(type(resp) is list)
        self.assertTrue(type(resp[0]) is twitter.User)
        self.assertEqual(len(resp), 335)

    @responses.activate
    def testGetFollowersPaged(self):
        with open('testdata/get_followers_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/list.json?include_user_entities=True&count=200&screen_name=himawari8bot&skip_status=False&cursor=-1'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        ncursor, pcursor, resp = self.api.GetFollowersPaged(screen_name='himawari8bot')

        self.assertTrue(type(resp) is list)
        self.assertTrue(type(resp[0]) is twitter.User)
        self.assertEqual(len(resp), 200)

    @responses.activate
    def testGetFollowerIDsPaged(self):
        with open('testdata/get_follower_ids_0.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/ids.json?count=5000&stringify_ids=False&screen_name=himawari8bot&cursor=-1'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        ncursor, pcursor, resp = self.api.GetFollowerIDsPaged(
            screen_name='himawari8bot')

        self.assertTrue(type(resp) is list)
        self.assertTrue(type(resp[0]) is int)
        self.assertEqual(len(resp), 5000)

        with open('testdata/get_follower_ids_stringify.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{base_url}/followers/ids.json?count=5000&stringify_ids=True&user_id=12&cursor=-1'.format(
                base_url=self.api.base_url),
            body=resp_data,
            match_querystring=True,
            status=200)

        ncursor, pcursor, resp = self.api.GetFollowerIDsPaged(
            user_id=12,
            stringify_ids=True)

        self.assertTrue(type(resp) is list)
        if sys.version_info.major >= 3:
            self.assertTrue(type(resp[0]) is str)
        else:
            self.assertTrue(type(resp[0]) is unicode)
        self.assertEqual(len(resp), 5000)

    @responses.activate
    def testUsersLookup(self):
        with open('testdata/users_lookup.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/users/lookup.json?user_id=718443',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.UsersLookup(user_id=[718443])
        self.assertTrue(type(resp) is list)
        self.assertEqual(len(resp), 1)
        user = resp[0]
        self.assertTrue(type(user) is twitter.User)
        self.assertEqual(user.screen_name, 'kesuke')
        self.assertEqual(user.id, 718443)

    @responses.activate
    def testGetUser(self):
        with open('testdata/get_user.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/users/show.json?user_id=718443',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetUser(user_id=718443)
        self.assertTrue(type(resp) is twitter.User)
        self.assertEqual(resp.screen_name, 'kesuke')
        self.assertEqual(resp.id, 718443)

    @responses.activate
    def testGetDirectMessages(self):
        with open('testdata/get_direct_messages.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/direct_messages.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetDirectMessages()
        self.assertTrue(type(resp) is list)
        direct_message = resp[0]
        self.assertTrue(type(direct_message) is twitter.DirectMessage)
        self.assertEqual(direct_message.id, 678629245946433539)

    @responses.activate
    def testGetSentDirectMessages(self):
        with open('testdata/get_sent_direct_messages.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/direct_messages/sent.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetSentDirectMessages()
        self.assertTrue(type(resp) is list)
        direct_message = resp[0]
        self.assertTrue(type(direct_message) is twitter.DirectMessage)
        self.assertEqual(direct_message.id, 678629283007303683)
        self.assertTrue([dm.sender_screen_name == 'notinourselves' for dm in resp])

    @responses.activate
    def testGetFavorites(self):
        with open('testdata/get_favorites.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/favorites/list.json?include_entities=True',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetFavorites()
        self.assertTrue(type(resp) is list)
        fav = resp[0]
        self.assertEqual(fav.id, 677180133447372800)
        self.assertIn("Extremely", fav.text)

    @responses.activate
    def testGetMentions(self):
        with open('testdata/get_mentions.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/statuses/mentions_timeline.json',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetMentions()
        self.assertTrue(type(resp) is list)
        self.assertTrue([type(mention) is twitter.Status for mention in resp])
        self.assertEqual(resp[0].id, 676148312349609985)

    @responses.activate
    def testGetListTimeline(self):
        with open('testdata/get_list_timeline.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            'https://api.twitter.com/1.1/lists/statuses.json?slug=space-bots&owner_screen_name=inky',
            body=resp_data,
            match_querystring=True,
            status=200)
        resp = self.api.GetListTimeline(list_id=None,
                                        slug='space-bots',
                                        owner_screen_name='inky')
        self.assertTrue(type(resp) is list)
        self.assertTrue([type(status) is twitter.Status for status in resp])
        self.assertEqual(resp[0].id, 677891843946766336)

        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetListTimeline(
                list_id=None,
                slug=None,
                owner_id=None))
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.GetListTimeline(
                list_id=None,
                slug=None,
                owner_screen_name=None))

    @responses.activate
    def testPostUpdate(self):
        with open('testdata/post_update.json') as f:
            resp_data = f.read()
        responses.add(
            responses.POST,
            'https://api.twitter.com/1.1/statuses/update.json',
            body=resp_data,
            status=200)
        post = self.api.PostUpdate(
            status="blah Longitude coordinate of the tweet in degrees.")
        self.assertTrue(type(post) is twitter.Status)
        self.assertEqual(
            post.text, "blah Longitude coordinate of the tweet in degrees.")
        self.assertTrue(post.geo is None)
        self.assertEqual(post.user.screen_name, 'notinourselves')

    @responses.activate
    def testPostUpdateExtraParams(self):
        with open('testdata/post_update_extra_params.json') as f:
            resp_data = f.read()
        responses.add(
            responses.POST,
            'https://api.twitter.com/1.1/statuses/update.json',
            body=resp_data,
            status=200)
        post = self.api.PostUpdate(
            status="Not a dupe. Longitude coordinate of the tweet in degrees.",
            in_reply_to_status_id=681496308251754496,
            latitude=37.781157,
            longitude=-122.398720,
            place_id="1",
            display_coordinates=True,
            trim_user=True)
        self.assertEqual(post.in_reply_to_status_id, 681496308251754496)
        self.assertIsNotNone(post.coordinates)

    @responses.activate
    def testVerifyCredentials(self):
        with open('testdata/verify_credentials.json') as f:
            resp_data = f.read()
        responses.add(
            responses.GET,
            '{0}/account/verify_credentials.json'.format(self.api.base_url),
            body=resp_data,
            status=200)

        resp = self.api.VerifyCredentials()
        self.assertEqual(type(resp), twitter.User)
        self.assertEqual(resp.name, 'notinourselves')

    @responses.activate
    def testUpdateBanner(self):
        responses.add(
            responses.POST,
            '{0}/account/update_profile_banner.json'.format(self.api.base_url),
            body=b'',
            status=201
        )
        resp = self.api.UpdateBanner(image='testdata/168NQ.jpg')
        self.assertTrue(resp)

    @responses.activate
    def testUpdateBanner422Error(self):
        responses.add(
            responses.POST,
            '{0}/account/update_profile_banner.json'.format(self.api.base_url),
            body=b'',
            status=422
        )
        self.assertRaises(
            twitter.TwitterError,
            lambda: self.api.UpdateBanner(image='testdata/168NQ.jpg')
        )
        try:
            self.api.UpdateBanner(image='testdata/168NQ.jpg')
        except twitter.TwitterError as e:
            self.assertTrue("The image could not be resized or is too large." in str(e))

    @responses.activate
    def testUpdateBanner400Error(self):
        responses.add(
            responses.POST,
            '{0}/account/update_profile_banner.json'.format(self.api.base_url),
            body=b'',
            status=400
        )
        try:
            self.api.UpdateBanner(image='testdata/168NQ.jpg')
        except twitter.TwitterError as e:
            self.assertTrue("Image data could not be processed" in str(e))
