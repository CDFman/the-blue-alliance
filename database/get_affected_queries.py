from database.award_query import EventAwardsQuery, TeamAwardsQuery, TeamYearAwardsQuery, TeamEventAwardsQuery
from database.event_query import EventListQuery, DistrictEventsQuery, TeamEventsQuery, TeamYearEventsQuery
from database.match_query import EventMatchesQuery, TeamEventMatchesQuery
from database.team_query import TeamListQuery, TeamListYearQuery, DistrictTeamsQuery, EventTeamsQuery

from models.district_team import DistrictTeam
from models.event_team import EventTeam


def _get_team_page_num(team_key):
    return int(team_key[3:]) / TeamListQuery.PAGE_SIZE


def award_updated(affected_refs):
    event_keys = filter(None, affected_refs['event'])
    team_keys = filter(None, affected_refs['team_list'])
    years = filter(None, affected_refs['year'])

    queries_and_keys = []
    for event_key in event_keys:
        queries_and_keys.append((EventAwardsQuery(event_key.id())))
        for team_key in team_keys:
            queries_and_keys.append((TeamEventAwardsQuery(team_key.id(), event_key.id())))

    for team_key in team_keys:
        queries_and_keys.append((TeamAwardsQuery(team_key.id())))
        for year in years:
            queries_and_keys.append((TeamYearAwardsQuery(team_key.id(), year)))

    return queries_and_keys


def event_updated(affected_refs):
    event_keys = filter(None, affected_refs['key'])
    years = filter(None, affected_refs['year'])
    event_district_keys = filter(None, affected_refs['event_district_key'])

    event_team_keys_future = EventTeam.query(EventTeam.event.IN([event_key for event_key in event_keys])).fetch_async(None, keys_only=True)

    queries_and_keys = []
    for year in years:
        queries_and_keys.append((EventListQuery(year)))

    for event_district_key in event_district_keys:
        queries_and_keys.append((DistrictEventsQuery(event_district_key)))

    for event_key in event_keys:
        queries_and_keys.append((EventListQuery(event_key.id())))

    for et_key in event_team_keys_future.get_result():
        team_key = et_key.id().split('_')[1]
        year = int(et_key.id()[:4])
        queries_and_keys.append((TeamEventsQuery(team_key)))
        queries_and_keys.append((TeamYearEventsQuery(team_key, year)))

    return queries_and_keys


def match_updated(affected_refs):
    event_keys = filter(None, affected_refs['event'])
    team_keys = filter(None, affected_refs['team_keys'])

    queries_and_keys = []
    for event_key in event_keys:
        queries_and_keys.append((EventMatchesQuery(event_key.id())))
        for team_key in team_keys:
            queries_and_keys.append((TeamEventMatchesQuery(team_key.id(), event_key.id())))

    return queries_and_keys


def team_updated(affected_refs):
    team_keys = filter(None, affected_refs['key'])

    event_team_keys_future = EventTeam.query(EventTeam.team.IN([team_key for team_key in team_keys])).fetch_async(None, keys_only=True)
    district_team_keys_future = DistrictTeam.query(DistrictTeam.team.IN([team_key for team_key in team_keys])).fetch_async(None, keys_only=True)

    queries_and_keys = []
    for team_key in team_keys:
        page_num = _get_team_page_num(team_key.id())
        queries_and_keys.append((TeamListQuery(page_num)))

    for et_key in event_team_keys_future.get_result():
        year = int(et_key.id()[:4])
        event_key = et_key.id().split('_')[0]
        page_num = _get_team_page_num(et_key.id().split('_')[1])
        queries_and_keys.append((TeamListYearQuery(year, page_num)))
        queries_and_keys.append((EventTeamsQuery(event_key)))

    for dt_key in district_team_keys_future.get_result():
        district_key = dt_key.district_key
        queries_and_keys.append((DistrictTeamsQuery(district_key)))

    return queries_and_keys


def eventteam_updated(affected_refs):
    event_keys = filter(None, affected_refs['event'])
    team_keys = filter(None, affected_refs['team'])
    years = filter(None, affected_refs['year'])

    queries_and_keys = []
    for team_key in team_keys:
        queries_and_keys.append(TeamEventsQuery(team_key.id()))
        page_num = _get_team_page_num(team_key.id())
        for year in years:
            queries_and_keys.append(TeamYearEventsQuery(team_key.id(), year))
            queries_and_keys.append(TeamListYearQuery(year, page_num))

    for event_key in event_keys:
        queries_and_keys.append(EventTeamsQuery(event_key.id()))

    return queries_and_keys

def districtteam_updated(affected_refs):
    district_keys = filter(None, affected_refs['district_key'])

    queries_and_keys = []
    for district_key in district_keys:
        queries_and_keys.append(DistrictTeamsQuery(district_key))

    return queries_and_keys
