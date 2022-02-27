from time import sleep
from typing import Dict, List, Any

from riotwatcher import LolWatcher, ApiError  # type: ignore[import]
import backoff  # type: ignore[import]

from .log import logger

# (Pdb) resp['matches'][0]
# {'platformId': 'NA1', 'gameId': 3517403685, 'champion': 33, 'queue': 1300, 'season': 13, 'timestamp': 1596305310886, 'role': 'DUO_SUPPORT', 'lane': 'NONE'}
def get_matches(
    lol_watcher: LolWatcher, region: str, my_puuid: str
) -> List[Dict[str, Any]]:
    received_entries: bool = True
    beginIndex: int = 0
    entries: List[Dict[str, Any]] = []
    region = fix_region(region) #changed to make it work with new riot API
    while received_entries:
        resp = lol_watcher.match.matchlist_by_puuid(
            region=region,
            puuid=my_puuid,
            start=beginIndex,
            count=100,
        )
        beginIndex += 100
        logger.debug(f"Got {len(resp)} matches from offset {beginIndex}...")
        for d in resp:
            entries.append(d)
        received_entries = len(resp) > 0
        sleep(1)
    return entries


@backoff.on_exception(backoff.expo, ApiError)
def get_match_data(
    lol_watcher: LolWatcher, region: str, match_id: str 
) -> Dict[str, Any]:
    sleep(1)
    region = fix_region(region) #changed to make it work with new riot API
    data: Dict[str, Any] = lol_watcher.match.by_id(region=region, match_id=match_id)
    return data


def export_data(api_key: str, summoner_name: str, region: str) -> List[Dict[str, Any]]:
    # get my info
    logger.debug("Getting encrypted account id...")
    lol_watcher = LolWatcher(api_key)
    me = lol_watcher.summoner.by_name(region, summoner_name)
    my_puuid = me["puuid"]

    # get all matches
    matches: List[Dict[str, Any]] =[]

    tmp_matches = get_matches(
        lol_watcher, region, my_puuid
    )

    for tm in tmp_matches:
        matches.append({"gameId":tm})


    # attach lots of metadata to each match Dict response
    for i, m in enumerate(matches, 1):
        logger.debug(f"[{i}/{len(matches)}] Requesting match_id => {m['gameId']}")
        # make sure were not overwriting some key from the API
        assert "matchData" not in m
        m["matchData"] = get_match_data(lol_watcher, region, m["gameId"])

    return matches


def fix_region(region):
    region_upper = region.upper()
    if (region_upper =="BR1"):
        region ="americas"
    if (region_upper =="EUN1"):
        region ="europe"
    if (region_upper =="EUW1"):
        region ="europe"
    if (region_upper =="JP1"):
        region ="asia"
    if (region_upper =="KR"):
        region ="asia"
    if (region_upper =="LA1"):
        region ="americas"
    if (region_upper =="LA2"):
        region ="americas"
    if (region_upper =="NA1"):
        region ="americas"
    if (region_upper =="OC1"):
        region ="asia"
    if (region_upper =="TR1"):
        region ="europe"
    if (region_upper =="RU"):
        region ="europe"
    return region
