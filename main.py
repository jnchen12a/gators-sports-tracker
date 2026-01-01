import asyncio
import requests
import time
from datetime import date, timedelta
import argparse

'''
Things to add:

'''

baseUrl = 'http://ncaa-api.henrygd.me'

class GameData():
    def __init__(self, homeTeam: str, homeScore: str, awayTeam: str, awayScore: str, currentStatus: str, startTime: str, other: str = '') -> None:
        self.update(homeTeam, homeScore, awayTeam, awayScore, currentStatus, startTime, other=other)

    def update(self, homeTeam: str, homeScore: str, awayTeam: str, awayScore: str, currentStatus: str, startTime: str, other: str = '') -> None:
        self.homeTeam = homeTeam
        self.homeScore = homeScore
        self.awayTeam = awayTeam
        self.awayScore = awayScore
        self.currentStatus = currentStatus
        self.startTime = startTime
        self.other = other

        self.filled = True if self.homeTeam != '' else False

def extractSeedOrRank(seed: str, rank: str) -> str:
    # assumes that seed and rank are the same, just that only one is used at a time
    if seed != '':
        return seed
    elif rank != '':
        return rank
    else:
        return ''


def printScoreboard(sport: str, gameList: list[GameData]) -> None:
    '''
    sport
    hometeam       score
    awayteam       score
    currentstatus  other
    '''
    col1Values = [len(sport)]
    col2Values = [0]
    for game in gameList:
        if 'UPCOMING' in game.currentStatus:
            statusString = game.currentStatus + ' ' + game.startTime
        else:
            statusString = game.currentStatus
        col1Values += [len(game.homeTeam), len(game.awayTeam), len(statusString)]
        col2Values += [len(game.homeScore), len(game.awayScore), len(game.other)]
    col1Len = max(col1Values)
    col2Len = max(col2Values) + 2
    print(f'{sport:<{col1Len}}')
    for i in range(len(gameList)):
        game = gameList[i]
        print(f'{game.awayTeam:<{col1Len}}{game.awayScore:>{col2Len}}')
        print('at')
        print(f'{game.homeTeam:<{col1Len}}{game.homeScore:>{col2Len}}')
        if 'UPCOMING' in game.currentStatus:
            statusString = game.currentStatus + ' ' + game.startTime
        else:
            statusString = game.currentStatus
        print(f'{statusString:<{col1Len}}{game.other:>{col2Len}}')
        if i != len(gameList) - 1:
            print()

def processGameGators(game: dict) -> tuple[GameData, GameData]:
    awayTeam = game["game"]["away"]["names"]["short"]
    homeTeam = game["game"]["home"]["names"]["short"]
    awayScore = game["game"]["away"]["score"]
    homeScore = game["game"]["home"]["score"]
    gameState = game["game"]["gameState"] # pre, live, final
    currentPeriod = game["game"]["currentPeriod"] # current quarter
    contestClock = game["game"]["contestClock"] if currentPeriod != 'HALFTIME' else '' # minutes left in quarter
    startDate = game["game"]["startDate"] # games start date
    startTime = game["game"]["startTime"]
    if homeTeam == "Florida" or awayTeam == "Florida":
        awayRank = extractSeedOrRank(game["game"]["away"]["seed"], game["game"]["away"]["rank"])
        awayTeam = f'{awayTeam} ({awayRank})' if awayRank != '' else awayTeam
        homeRank = extractSeedOrRank(game["game"]["home"]["seed"], game["game"]["home"]["rank"])
        homeTeam = f'{homeTeam} ({homeRank})' if homeRank != '' else homeTeam
        if gameState == 'pre':
            return GameData('', '', '', '', '', ''), GameData(homeTeam, homeScore, awayTeam, awayScore, 'UPCOMING', startTime, startDate)
        elif gameState == 'live':
            return GameData(homeTeam, homeScore, awayTeam, awayScore, currentPeriod, startTime, contestClock), GameData('', '', '', '', '', '')
        else:
            # gameState == 'final'
            return GameData(homeTeam, homeScore, awayTeam, awayScore, currentPeriod, startTime, startDate), GameData('', '', '', '', '', '')
    else:
        return GameData('', '', '', '', '', ''), GameData('', '', '', '', '', '')
    
def checkT25Rank(rank: str) -> bool:
    if rank == '':
        return False
    elif int(rank) <= 25:
        return True
    else:
        return False

def processGameT25Football(game: dict) -> GameData:
    awayTeam = game["game"]["away"]["names"]["short"]
    homeTeam = game["game"]["home"]["names"]["short"]
    awayScore = game["game"]["away"]["score"]
    homeScore = game["game"]["home"]["score"]
    awayRank = extractSeedOrRank(game["game"]["away"]["seed"], game["game"]["away"]["rank"])
    homeRank = extractSeedOrRank(game["game"]["home"]["seed"], game["game"]["home"]["rank"])
    gameState = game["game"]["gameState"] # pre, live, final
    currentPeriod = game["game"]["currentPeriod"] # current quarter
    contestClock = game["game"]["contestClock"] if currentPeriod != 'HALFTIME' else '' # minutes left in quarter
    startDate = game["game"]["startDate"] # games start date
    startTime = game["game"]["startTime"]
    if checkT25Rank(awayRank) or checkT25Rank(homeRank):
        # return a game
        awayTeam = f'{awayTeam} ({awayRank})' if awayRank != '' else awayTeam
        homeTeam = f'{homeTeam} ({homeRank})' if homeRank != '' else homeTeam
        if gameState == 'pre':
            return GameData(homeTeam, homeScore, awayTeam, awayScore, 'UPCOMING', startTime, startDate)
        elif gameState == 'live':
            return GameData(homeTeam, homeScore, awayTeam, awayScore, currentPeriod, startTime, contestClock)
        else:
            # gameState == 'final'
            return GameData(homeTeam, homeScore, awayTeam, awayScore, currentPeriod, startTime, startDate)
    else:
        return GameData('', '', '', '', '', '')
    
def processGameT25Basketball(game: dict) -> GameData:
    awayTeam = game["game"]["away"]["names"]["short"]
    homeTeam = game["game"]["home"]["names"]["short"]
    awayScore = game["game"]["away"]["score"]
    homeScore = game["game"]["home"]["score"]
    awayRank = extractSeedOrRank(game["game"]["away"]["seed"], game["game"]["away"]["rank"])
    homeRank = extractSeedOrRank(game["game"]["home"]["seed"], game["game"]["home"]["rank"])
    gameState = game["game"]["gameState"] # pre, live, final
    currentPeriod = game["game"]["currentPeriod"] # current quarter
    contestClock = game["game"]["contestClock"] if currentPeriod != 'HALFTIME' else '' # minutes left in quarter
    startDate = game["game"]["startDate"] # games start date
    startTime = game["game"]["startTime"]
    bracketRound = game["game"]["bracketRound"]
    if checkT25Rank(awayRank) or checkT25Rank(homeRank) or bracketRound != '':
        # return a game
        awayTeam = f'{awayTeam} ({awayRank})' if awayRank != '' else awayTeam
        homeTeam = f'{homeTeam} ({homeRank})' if homeRank != '' else homeTeam
        if gameState == 'pre':
            return GameData(homeTeam, homeScore, awayTeam, awayScore, f'UPCOMING ({bracketRound})', startTime, startDate)
        elif gameState == 'live':
            return GameData(homeTeam, homeScore, awayTeam, awayScore, f'{currentPeriod} ({bracketRound})', startTime, contestClock)
        else:
            # gameState == 'final'
            return GameData(homeTeam, homeScore, awayTeam, awayScore, f'{currentPeriod} ({bracketRound})', startTime, startDate)
    else:
        return GameData('', '', '', '', '', '')

async def getHttp(s: str) -> dict:
    response = requests.get(baseUrl + s)
    if response.status_code == 200:
        j = response.json()
        if len(j) == 0:
            print('HTTPS ERROR: Resulting json is empty.')
            print(f'Request: {baseUrl + s}')
            return {}
        else:
            return j
    else:
        print(f'HTTPS ERROR: {response.status_code}')
        print(f'Request: {baseUrl + s}')
        return {}
    
async def getGatorsFootballData() -> None:
    currentYear = date.today().year
    # get current week from schedule-alt endpoint
    j = await getHttp(f'/schedule-alt/football/fbs/{currentYear}')
    if len(j) == 0:
        return
    week = int(j["data"]["schedules"]["today"]["week"])
    gatorsFound = False
    gameList = []
    while not gatorsFound and week >= 0:
        j = await getHttp(f'/scoreboard/football/fbs/{currentYear}/{week:02}/all-conf')
        if len(j) == 0:
            return
        games = j['games']
        for game in games:
            currentGame, preGame = processGameGators(game)
            if not currentGame.filled and not preGame.filled:
                continue
            elif not currentGame.filled:
                # pregame
                gameList.append(preGame)
            else:
                # found current gators game
                gatorsFound = True
                gameList.append(currentGame)
        
        week -= 1

    printScoreboard('Football', gameList[::-1])
    print('-' * 10)

async def getGatorsBasketballData() -> None:
    # basketball-men d1
    # get date today
    d = date.today() + timedelta(weeks=1)
    gatorsFound = False
    gameList = []
    while not gatorsFound:
        j = await getHttp(f'/scoreboard/basketball-men/d1/{d.year}/{d.month:02}/{d.day:02}')
        if len(j) == 0:
            return
        games = j['games']
        for game in games:
            currentGame, preGame = processGameGators(game)
            if not currentGame.filled and not preGame.filled:
                continue
            elif not currentGame.filled:
                # pregame
                gameList.append(preGame)
            else:
                # found current gators game
                gatorsFound = True
                gameList.append(currentGame)
        d -= timedelta(days=1)
    
    printScoreboard("Men's Basketball", gameList[::-1])
    print('-' * 10)

async def getGeneralFootballData(post: bool) -> None:
    currentYear = date.today().year
    # get current week from schedule-alt endpoint
    j = await getHttp(f'/schedule-alt/football/fbs/{currentYear}')
    if len(j) == 0:
        return
    week = int(j["data"]["schedules"]["today"]["week"])
    gameList = []
    j = await getHttp(f'/scoreboard/football/fbs/{currentYear}/{week:02}/all-conf')
    if len(j) == 0:
        return
    games = j['games']
    for game in games:
        currentGame = processGameT25Football(game)
        if not currentGame.filled:
            # not a t25 matchup
            continue
        else:
            # found a t25 matchup
            if post:
                # only add if it is a playoff game
                # check if it is a playoff game
                innerj = await getHttp(f'{game['game']['url']}')
                if innerj['contests'][0]['championship'] is not None or innerj['contests'][0]['championshipGame'] is not None:
                    # it is a playoff game
                    currentGame.currentStatus += ' (CFP)'
                    gameList.append(currentGame)
            else:
                gameList.append(currentGame)

    printScoreboard('Football (T25)', gameList)
    print('-' * 10)

async def getGeneralBasketballData() -> None:
    # basketball-men d1
    # get date today
    d = date.today() + timedelta(days=2)
    t = date.today()
    gameList = []
    while t <= d:
        j = await getHttp(f'/scoreboard/basketball-men/d1/{d.year}/{d.month:02}/{d.day:02}')
        if len(j) == 0:
            return
        games = j['games']
        for game in games:
            currentGame = processGameT25Basketball(game)
            if not currentGame.filled:
                continue
            else:
                # found t25 game
                gameList.append(currentGame)
                # TODO: only get march madness games?
        d -= timedelta(days=1)
    
    printScoreboard("Men's Basketball (T25)", gameList)
    print('-' * 10)

async def mainGators() -> None:
    await asyncio.gather(getGatorsFootballData(), getGatorsBasketballData())

async def main(n: argparse.Namespace) -> None:
    l = n.items
    post = n.post
    if len(l) == 0:
        await mainGators()
    else:
        coroutines = []
        for item in l:
            if item == 'football':
                coroutines.append(lambda: getGeneralFootballData(post))
            elif item == 'basketball':
                coroutines.append(getGeneralBasketballData)
            elif item == 'gators':
                coroutines.append(mainGators)
        
        coroutines = [f() for f in coroutines]
        await asyncio.gather(*coroutines)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Pulls Gator's sports data! Can also pull general college football sports data. Go Gators!")
    ap.add_argument('--post', '-p', action='store_true', help='If set, only returns postseason/playoff games. Only used when general sports games data is returned, not for Gators-specific.')
    ap.add_argument('items', nargs='*', type=str, choices=['gators', 'football', 'basketball'], help="List the sports you'd like to return info for.")
    args = ap.parse_args()
    start = time.time()
    asyncio.run(main(args))
    end = time.time()

    print(f'Time elapsed: {end - start:.02f}s')
