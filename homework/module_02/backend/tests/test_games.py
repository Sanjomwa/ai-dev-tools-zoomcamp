def test_list_games_returns_seeded_games_in_scheduling_order(client):
    resp = client.get("/api/games")
    assert resp.status_code == 200
    games = resp.json()
    assert [g["id"] for g in games] == [7, 8, 9, 1, 2, 3, 4, 5, 6]
    assert games[0]["status"] == "scheduled"
    assert games[3]["status"] == "done"
    assert games[3]["homeScore"] == 3
    assert games[3]["awayScore"] == 1


def test_schedule_game_is_prepended_and_starts_scheduled(client):
    resp = client.post(
        "/api/games",
        json={"home": "Ironclad FC", "away": "Harbor Rovers", "date": "2026-10-01"},
    )
    assert resp.status_code == 201
    game = resp.json()
    assert game["status"] == "scheduled"
    assert game["home"] == "Ironclad FC"
    assert game["away"] == "Harbor Rovers"
    assert game["date"] == "2026-10-01"
    assert game.get("homeScore") is None
    assert game.get("awayScore") is None

    games = client.get("/api/games").json()
    assert games[0]["id"] == game["id"]


def test_schedule_game_rejects_unknown_team(client):
    resp = client.post(
        "/api/games",
        json={"home": "Ghost United", "away": "Harbor Rovers", "date": "2026-10-01"},
    )
    assert resp.status_code == 404
    assert "detail" in resp.json()


def test_schedule_game_rejects_missing_fields(client):
    resp = client.post("/api/games", json={"home": "Ironclad FC"})
    assert resp.status_code == 422
    assert isinstance(resp.json()["detail"], str)


def test_record_score_marks_game_done(client):
    resp = client.post("/api/games/7/score", json={"homeScore": 2, "awayScore": 1})
    assert resp.status_code == 200
    game = resp.json()
    assert game["id"] == 7
    assert game["status"] == "done"
    assert game["homeScore"] == 2
    assert game["awayScore"] == 1


def test_record_score_rejects_unknown_game(client):
    resp = client.post("/api/games/999/score", json={"homeScore": 1, "awayScore": 0})
    assert resp.status_code == 404
    assert "detail" in resp.json()


def test_record_score_rejects_second_call(client):
    first = client.post("/api/games/7/score", json={"homeScore": 2, "awayScore": 1})
    assert first.status_code == 200

    second = client.post("/api/games/7/score", json={"homeScore": 3, "awayScore": 3})
    assert second.status_code == 409
    assert "detail" in second.json()


def test_record_score_rejects_negative_score(client):
    resp = client.post("/api/games/7/score", json={"homeScore": -1, "awayScore": 0})
    assert resp.status_code == 422
    assert isinstance(resp.json()["detail"], str)
