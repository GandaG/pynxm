import pynxm
import pytest
import responses

TEST_INSTANCE = pynxm.Nexus("test-key")
TEST_JSON = {"test": "content"}


@responses.activate
def test_errors():
    responses.add(
        responses.GET,
        pynxm.BASE_URL + "test_endpoint1",
        json={"error": "error message"},
        status=404,
    )
    with pytest.raises(pynxm.RequestError) as excinfo:
        TEST_INSTANCE._make_request("get", "test_endpoint1")
        assert excinfo.value == "error message"
    responses.add(
        responses.GET,
        pynxm.BASE_URL + "test_endpoint2",
        json={"message": "error message"},
        status=422,
    )
    with pytest.raises(pynxm.RequestError) as excinfo:
        TEST_INSTANCE._make_request("get", "test_endpoint2")
        assert excinfo.value == "error message"
    responses.add(responses.GET, pynxm.BASE_URL + "test_endpoint3", status=429)
    with pytest.raises(pynxm.LimitReachedError) as excinfo:
        TEST_INSTANCE._make_request("get", "test_endpoint3")
        assert (
            excinfo.value == "You have reached your request limit. "
            "Please wait one hour before trying again."
        )


@responses.activate
def test_colour_schemes_list():
    responses.add(responses.GET, pynxm.BASE_URL + "colourschemes.json", json=TEST_JSON)
    assert TEST_INSTANCE.colour_schemes_list() == TEST_JSON


@responses.activate
def test_user_details():
    responses.add(responses.GET, pynxm.BASE_URL + "users/validate.json", json=TEST_JSON)
    assert TEST_INSTANCE.user_details() == TEST_JSON


@responses.activate
def test_user_tracked_list():
    responses.add(
        responses.GET, pynxm.BASE_URL + "user/tracked_mods.json", json=TEST_JSON
    )
    assert TEST_INSTANCE.user_tracked_list() == TEST_JSON


@responses.activate
def test_user_tracked_add():
    test_url = pynxm.BASE_URL + "user/tracked_mods.json"
    responses.add(responses.POST, test_url, json=TEST_JSON)
    TEST_INSTANCE.user_tracked_add("game", "mod_id")
    request = responses.calls[0].request
    assert request.headers.get("content-type") == "application/x-www-form-urlencoded"
    assert request.url == test_url + "?{}={}".format("domain_name", "game")
    assert request.body == "{}={}".format("mod_id", "mod_id")


@responses.activate
def test_user_tracked_delete():
    test_url = pynxm.BASE_URL + "user/tracked_mods.json"
    responses.add(responses.DELETE, test_url, json=TEST_JSON)
    TEST_INSTANCE.user_tracked_delete("game", "mod_id")
    request = responses.calls[0].request
    assert request.headers.get("content-type") == "application/x-www-form-urlencoded"
    assert request.url == test_url + "?domain_name=game"
    assert request.body == "mod_id=mod_id"


@responses.activate
def test_user_endorsements_list():
    responses.add(
        responses.GET, pynxm.BASE_URL + "user/endorsements.json", json=TEST_JSON
    )
    assert TEST_INSTANCE.user_endorsements_list() == TEST_JSON


@responses.activate
def test_game_details():
    responses.add(responses.GET, pynxm.BASE_URL + "games/game_id.json", json=TEST_JSON)
    assert TEST_INSTANCE.game_details("game_id") == TEST_JSON


@responses.activate
def test_game_list():
    test_url = pynxm.BASE_URL + "games.json"
    responses.add(responses.GET, test_url, json=TEST_JSON)
    assert TEST_INSTANCE.game_list() == TEST_JSON
    assert responses.calls[0].request.url == test_url + "?include_unapproved=False"


@responses.activate
def test_game_updated_list():
    test_url = pynxm.BASE_URL + "games/game_id/mods/updated.json"
    responses.add(responses.GET, test_url, json=TEST_JSON)
    assert TEST_INSTANCE.game_updated_list("game_id", "1d") == TEST_JSON
    assert responses.calls[0].request.url == test_url + "?period=1d"


@responses.activate
def test_game_latest_added_list():
    responses.add(
        responses.GET,
        pynxm.BASE_URL + "games/game_id/mods/latest_added.json",
        json=TEST_JSON,
    )
    assert TEST_INSTANCE.game_latest_added_list("game_id") == TEST_JSON


@responses.activate
def test_game_latest_updated_list():
    responses.add(
        responses.GET,
        pynxm.BASE_URL + "games/game_id/mods/latest_updated.json",
        json=TEST_JSON,
    )
    assert TEST_INSTANCE.game_latest_updated_list("game_id") == TEST_JSON


@responses.activate
def test_game_trending_list():
    responses.add(
        responses.GET,
        pynxm.BASE_URL + "games/game_id/mods/trending.json",
        json=TEST_JSON,
    )
    assert TEST_INSTANCE.game_trending_list("game_id") == TEST_JSON


@responses.activate
def test_mod_details():
    responses.add(
        responses.GET, pynxm.BASE_URL + "games/game_id/mods/mod_id.json", json=TEST_JSON
    )
    assert TEST_INSTANCE.mod_details("game_id", "mod_id") == TEST_JSON


@responses.activate
def test_mod_search():
    responses.add(
        responses.GET, pynxm.BASE_URL + "games/game_id/mods/mod_id.json", json=TEST_JSON
    )
    assert TEST_INSTANCE.mod_details("game_id", "mod_id") == TEST_JSON


@responses.activate
def test_mod_endorse():
    responses.add(
        responses.POST,
        pynxm.BASE_URL + "games/game_id/mods/mod_id/endorse.json",
        json=TEST_JSON,
    )
    assert TEST_INSTANCE.mod_endorse("game_id", "mod_id") == TEST_JSON


@responses.activate
def test_mod_abstain():
    responses.add(
        responses.POST,
        pynxm.BASE_URL + "games/game_id/mods/mod_id/abstain.json",
        json=TEST_JSON,
    )
    assert TEST_INSTANCE.mod_abstain("game_id", "mod_id") == TEST_JSON


@responses.activate
def test_mod_file_list():
    test_url = pynxm.BASE_URL + "games/game_id/mods/mod_id/files.json"
    responses.add(responses.GET, test_url, json=TEST_JSON)
    assert (
        TEST_INSTANCE.mod_file_list("game_id", "mod_id", categories="main,update")
        == TEST_JSON
    )
    assert responses.calls[0].request.url == test_url + "?category=main%2Cupdate"


@responses.activate
def test_mod_file_details():
    responses.add(
        responses.GET,
        pynxm.BASE_URL + "games/game_id/mods/mod_id/files/file_id.json",
        json=TEST_JSON,
    )
    assert TEST_INSTANCE.mod_file_details("game_id", "mod_id", "file_id") == TEST_JSON


@responses.activate
def test_mod_file_download_link():
    test_url = (
        pynxm.BASE_URL + "games/game_id/mods/mod_id/files/file_id/download_link.json"
    )
    responses.add(responses.GET, test_url, json=TEST_JSON)
    assert (
        TEST_INSTANCE.mod_file_download_link(
            "game_id", "mod_id", "file_id", nxm_key="key", expires="expires"
        )
        == TEST_JSON
    )
    assert responses.calls[0].request.url == test_url + "?key=key&expires=expires"


@responses.activate
def test_mod_changelog_list():
    responses.add(
        responses.GET,
        pynxm.BASE_URL + "games/game_id/mods/mod_id/changelogs.json",
        json=TEST_JSON,
    )
    assert TEST_INSTANCE.mod_changelog_list("game_id", "mod_id") == TEST_JSON
