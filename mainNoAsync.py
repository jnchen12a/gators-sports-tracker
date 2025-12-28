import asyncio
import requests
import time
from datetime import date, timedelta

baseUrl = 'http://ncaa-api.henrygd.me'

def printScoreboard(sport: str, homeTeam: str, homeScore: str, awayTeam: str, awayScore: str, currentStatus: str, other: str = '') -> None:
    '''
    sport
    hometeam       score
    awayteam       score
    currentstatus  other
    '''
    col1Len = max(len(sport), len(homeTeam), len(awayTeam), len(currentStatus))
    col2Len = max(len(homeScore), len(awayScore), len(other)) + 2
    print(f'{sport:<{col1Len}}')
    print(f'{homeTeam:<{col1Len}}{homeScore:>{col2Len}}')
    print(f'{awayTeam:<{col1Len}}{awayScore:>{col2Len}}')
    print(f'{currentStatus:<{col1Len}}{other:>{col2Len}}')

def processGame(sport: str, game: dict) -> tuple:
    preGame = {}
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
            preGame['awayTeam'] = awayTeam
            preGame['homeTeam'] = homeTeam
            preGame['homeScore'] = homeScore
            preGame['awayScore'] = awayScore
            preGame['gameState'] = gameState
            preGame['startDate'] = startDate
            return True, preGame
        elif gameState == 'live':
            printScoreboard(sport, homeTeam, homeScore, awayTeam, awayScore, currentPeriod, other=contestClock)
            return True, preGame
        else:
            # gameState == 'final'
            printScoreboard(sport, homeTeam, homeScore, awayTeam, awayScore, currentPeriod, other=startDate)
            return True, preGame
    else:
        return False, {}

def getHttp(s: str) -> dict:
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
    
def getGatorsFootballData() -> None:
    currentYear = date.today().year
    # get current week from schedule-alt endpoint
    j = getHttp(f'/schedule-alt/football/fbs/{currentYear}') # TODO: get current year
    if len(j) == 0:
        return
    week = int(j["data"]["schedules"]["today"]["week"])
    gatorsFound = False
    preGame = {}
    while not gatorsFound and week >= 0:
        j = getHttp(f'/scoreboard/football/fbs/{currentYear}/{week:02}/all-conf')
        if len(j) == 0:
            return
        games = j['games']
        for game in games:
            b, preGameTemp = processGame('Football', game)
            if b:
                # found gators game
                if len(preGameTemp) == 0:
                    # found on that is not Upcoming
                    gatorsFound = True
                else:
                    preGame = preGameTemp if len(preGame) == 0 else preGame
        
        week -= 1

        if len(preGame) != 0:
            printScoreboard('', preGame['homeTeam'], preGame['homeScore'], preGame['awayTeam'], preGame['awayScore'], 'Upcoming', preGame['startDate'])

    print('-' * 10)

def getGatorsBasketballData() -> None:
    # basketball-men d1
    # get date today
    d = date.today()
    gatorsFound = False
    preGame = {}
    while not gatorsFound:
        j = getHttp(f'/scoreboard/basketball-men/d1/{d.year}/{d.month:02}/{d.day:02}')
        if len(j) == 0:
            return
        games = j['games']
        for game in games:
            b, preGameTemp = processGame("Men's Basketball", game)
            if b:
                # found gators game
                if len(preGameTemp) == 0:
                    # found on that is not Upcoming
                    gatorsFound = True
                else:
                    preGame = preGameTemp if len(preGame) == 0 else preGame
        d -= timedelta(days=1)
    
    if len(preGame) != 0:
        printScoreboard('', preGame['homeTeam'], preGame['homeScore'], preGame['awayTeam'], preGame['awayScore'], 'Upcoming', preGame['startDate'])
    
    print('-' * 10)

if __name__ == '__main__':
    start = time.time()
    getGatorsFootballData()
    getGatorsBasketballData()
    end = time.time()

    print(f'Time elapsed: {end - start:.02f}s')
