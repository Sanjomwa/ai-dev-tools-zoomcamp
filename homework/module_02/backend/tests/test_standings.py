def test_standings_computed_from_seeded_results_ranked_by_points(client):
    resp = client.get("/api/standings")
    assert resp.status_code == 200
    rows = resp.json()

    assert [r["name"] for r in rows] == [
        "Ironclad FC",
        "Dockside United",
        "Harbor Rovers",
        "Maple Street AC",
        "Northgate Athletic",
        "The Wanderers",
    ]
    points = [r["points"] for r in rows]
    assert points == sorted(points, reverse=True)

    leader = rows[0]
    assert leader == {
        "name": "Ironclad FC",
        "color": "#6ee7a0",
        "played": 2,
        "won": 2,
        "drawn": 0,
        "lost": 0,
        "points": 6,
    }

    last = rows[-1]
    assert last["name"] == "The Wanderers"
    assert last["played"] == 2
    assert last["won"] == 0
    assert last["lost"] == 2
    assert last["points"] == 0


def test_standings_ignore_scheduled_games(client):
    before = client.get("/api/standings").json()
    total_played_before = sum(r["played"] for r in before)

    client.post(
        "/api/games",
        json={"home": "Ironclad FC", "away": "Harbor Rovers", "date": "2026-10-01"},
    )

    after = client.get("/api/standings").json()
    total_played_after = sum(r["played"] for r in after)
    assert total_played_after == total_played_before
