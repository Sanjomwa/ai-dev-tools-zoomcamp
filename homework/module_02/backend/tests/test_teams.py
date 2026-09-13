import re

HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")


def test_list_teams_returns_seeded_teams(client):
    resp = client.get("/api/teams")
    assert resp.status_code == 200
    teams = resp.json()
    assert len(teams) == 6
    assert teams[0] == {"name": "Ironclad FC", "color": "#6ee7a0"}
    for team in teams:
        assert HEX_COLOR.match(team["color"])


def test_add_team_returns_created_team_with_assigned_color(client):
    existing_colors = {t["color"] for t in client.get("/api/teams").json()}

    resp = client.post("/api/teams", json={"name": "New Team FC"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "New Team FC"
    assert HEX_COLOR.match(body["color"])
    assert body["color"] not in existing_colors

    listed = client.get("/api/teams").json()
    assert listed[-1] == body
    assert len(listed) == 7


def test_every_team_gets_a_distinct_color_even_past_the_base_palette(client):
    # 6 seed teams already use the full 6-color palette; adding a 7th
    # forces the fallback generator — every team must still be distinct.
    for i in range(3):
        resp = client.post("/api/teams", json={"name": f"Extra FC {i}"})
        assert resp.status_code == 201

    colors = [t["color"] for t in client.get("/api/teams").json()]
    assert len(colors) == len(set(colors))
    for color in colors:
        assert HEX_COLOR.match(color)


def test_add_team_rejects_empty_name(client):
    resp = client.post("/api/teams", json={"name": ""})
    assert resp.status_code == 422
    assert "detail" in resp.json()
    assert isinstance(resp.json()["detail"], str)


def test_add_team_rejects_duplicate_name(client):
    resp = client.post("/api/teams", json={"name": "Ironclad FC"})
    assert resp.status_code == 422
    assert isinstance(resp.json()["detail"], str)
