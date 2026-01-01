# gators-sports-tracker
A Gator fan's favorite piece of code!

Pulls and displays recent/future Florida Gators game data from sports including:
* Football
* Basketball
* Baseball

Also has the ability to pull general college sports data.

![](./response.svg)

Go Gators!

## How to Use
Simply run `py main.py [options]`. Run `py main.py --help` for help on the options.

`main.py` holds the most up-to-date functionality.

### Option descriptions
Flags:
* --post or -p: if set, will only return postseason (playoffs, March Madness, etc.) game data
    * Only is meaninful when `football` or `basketball` are passed in
* Positional arguments [`gators`, `football`, `basketball`] (multiple can be passed in at the same time)
    * `gators` - only returns Gator's specific game data, across multiple sports
    * `football` - returns general (t25) football game data
    * `basketball` - returns general (t25) basketball game data