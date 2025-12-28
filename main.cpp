#define _WIN32_WINNT 0x0A00
#include "httplib.h"
#include <iostream>
#include <nlohmann/json.hpp>
#include <format>

std::string baseUrl = "http://ncaa-api.henrygd.me";

/*
{
    "slug": "florida",
    "name": "Florida",
    "long": "University of Florida"
  },

  "today": {
        "date": "2025/P",
        "week": 18,
        "season": 2025
      }

https://ncaa-api.henrygd.me/openapi
short = name
*/

std::pair<bool, httplib::Result> httpGet(std::string s) {
	httplib::Client cli(baseUrl);
	if (auto res = cli.Get(s)) { // get current year
		if (res->status == 200) {
			return {true, std::move(res)};
		} else {
			std::cerr << "Error: " << res->status << std::endl;
			return {false, std::move(res)};
		}
	} else {
		auto err = res.error();
		std::cerr << "Request failed: " << static_cast<int>(err) << std::endl;
		return {false, std::move(res)};
	}
}

std::string weekToInt(int w) {
	std::string s = std::to_string(w);
	if (s.length() < 2) {
		s = "0" + s;
	}
	return s;
}

void getFootballData() {
	std::pair<bool, httplib::Result> p = httpGet("/schedule-alt/football/fbs/2025");
	int weekInt;
	// get the current week
	if (p.first) {
		httplib::Result res = std::move(p.second);
		auto j = nlohmann::json::parse(res->body);
		weekInt = j["data"]["schedules"]["today"]["week"];
	} else {
		return;
	}
	bool foundGators= false;
	while (!foundGators && (weekInt >= 0)) {
		// see if gators exist in the current week
		p = httpGet(std::format("/scoreboard/football/fbs/{}/{}/all-conf", 2025, weekToInt(weekInt)));
		if (p.first) {
			httplib::Result res = std::move(p.second);
			auto j = nlohmann::json::parse(res->body);
			auto games = j["games"];
			for (auto game : games) {
				// data that we want: teams, score, game state
				// if gameState == "live", can also get currentPeriod and contestClock
				// if gameState == "final", just get currentPeriod
				// if gameState == "pre", go back one week to try to get a finished game
				std::string awayTeam = game["game"]["away"]["names"]["short"];
				std::string homeTeam = game["game"]["home"]["names"]["short"];
				std::string awayScore = game["game"]["away"]["score"];
				std::string homeScore = game["game"]["home"]["score"];
				std::string gameState = game["game"]["gameState"];
				std::string currentPeriod = game["game"]["currentPeriod"];
				std::string contestClock = game["game"]["contestClock"];
				std::string startDate = game["game"]["startDate"];
				if (homeTeam == "Florida" || awayTeam == "Florida") {
					std::cout << "Football" << std::endl;
					std::cout << awayTeam << ": " << awayScore << std::endl;
					std::cout << homeTeam << ": " << homeScore << std::endl;
					if (gameState == "pre") {
						std::cout << "Upcoming" << std::endl << std::endl;
					} else if (gameState == "live") {
						std::cout << currentPeriod << " " << contestClock << std::endl;
						foundGators == true;
					} else {
						// gameState == "final"
						std::cout << currentPeriod << " " << startDate << std::endl;
						foundGators = true;
					}
				}
			}
		} else {
			return;
		}
		weekInt--;
	}

	if (!foundGators) {
		std::cout << "Sorry, no Gator games found." << std::endl;
	}
}

int main() {
    // return most recent basketball, baseball, and football scores.
    // need some function to format scores
	getFootballData();
    return 0;
}