import asyncio
import requests
import time
from datetime import date, timedelta

baseUrl = 'http://ncaa-api.henrygd.me'

class GameData():
    def __init__(self, homeTeam: str, homeScore: str, awayTeam: str, awayScore: str, currentStatus: str, other: str = '') -> None:
        self.update(homeTeam, homeScore, awayTeam, awayScore, currentStatus, other=other)

    def update(self, homeTeam: str, homeScore: str, awayTeam: str, awayScore: str, currentStatus: str, other: str = '') -> None:
        self.homeTeam = homeTeam
        self.homeScore = homeScore
        self.awayTeam = awayTeam
        self.awayScore = awayScore
        self.currentStatus = currentStatus
        self.other = other

        self.filled = True if self.homeTeam != '' else False


def printScoreboard(sport: str, gameList: list[GameData]) -> None:
    '''
    sport
    hometeam       score
    awayteam       score
    currentstatus  other
    '''
    col1Values = [len(sport)]
    col2Values = []
    for game in gameList:
        col1Values += [len(game.homeTeam), len(game.awayTeam), len(game.currentStatus)]
        col2Values += [len(game.homeScore), len(game.awayScore), len(game.other)]
    col1Len = max(col1Values)
    col2Len = max(col2Values) + 2
    print(f'{sport:<{col1Len}}')
    for i in range(len(gameList)):
        game = gameList[i]
        print(f'{game.homeTeam:<{col1Len}}{game.homeScore:>{col2Len}}')
        print(f'{game.awayTeam:<{col1Len}}{game.awayScore:>{col2Len}}')
        print(f'{game.currentStatus:<{col1Len}}{game.other:>{col2Len}}')
        if i != len(gameList) - 1:
            print()

def processGame(game: dict) -> tuple[GameData, GameData]:
    awayTeam = game["game"]["away"]["names"]["short"]
    homeTeam = game["game"]["home"]["names"]["short"]
    awayScore = game["game"]["away"]["score"]
    homeScore = game["game"]["home"]["score"]
    gameState = game["game"]["gameState"] # pre, live, final
    currentPeriod = game["game"]["currentPeriod"] # current quarter
    contestClock = game["game"]["contestClock"] # minutes left in quarter
    startDate = game["game"]["startDate"] # games start date
    if homeTeam == "Florida" or awayTeam == "Florida":
        if gameState == 'pre':
            return GameData('', '', '', '', ''), GameData(homeTeam, homeScore, awayTeam, awayScore, 'Upcoming', startDate)
        elif gameState == 'live':
            return GameData(homeTeam, homeScore, awayTeam, awayScore, currentPeriod, contestClock), GameData('', '', '', '', '')
        else:
            # gameState == 'final'
            return GameData(homeTeam, homeScore, awayTeam, awayScore, currentPeriod, startDate), GameData('', '', '', '', '')
    else:
        return GameData('', '', '', '', ''), GameData('', '', '', '', '')

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
    j = await getHttp(f'/schedule-alt/football/fbs/{currentYear}') # TODO: get current year
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
            currentGame, preGame = processGame(game)
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
            currentGame, preGame = processGame(game)
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

async def mainGators():
    await asyncio.gather(getGatorsFootballData(), getGatorsBasketballData())

if __name__ == '__main__':
    start = time.time()
    asyncio.run(mainGators())
    end = time.time()

    print(f'Time elapsed: {end - start:.02f}s')
