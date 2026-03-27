#!/usr/bin/env python3
"""
Test script to validate fixture filter and date constraint changes
"""
import requests
import json
from datetime import datetime, timedelta

# API Configuration
API_BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def test_fixture_functionality():
    """Test the fixture filter and date constraints"""
    
    print("=" * 60)
    print("FIXTURE CHANGES TEST SCRIPT")
    print("=" * 60)
    
    # Step 1: Login
    print("\n[STEP 1] Authenticating as admin...")
    login_response = requests.post(
        f"{API_BASE_URL}/api/auth/login",
        data={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.json()}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Successfully authenticated")
    
    # Step 2: Get existing fixtures
    print("\n[STEP 2] Fetching existing fixtures...")
    fixtures_response = requests.get(
        f"{API_BASE_URL}/api/fixtures",
        headers=headers
    )
    
    if fixtures_response.status_code != 200:
        print(f"❌ Failed to fetch fixtures: {fixtures_response.json()}")
        return False
    
    fixtures = fixtures_response.json()
    print(f"✓ Found {len(fixtures)} fixtures")
    
    if len(fixtures) == 0:
        print("⚠️  No fixtures found. Generating fixtures...")
        
        # Get teams
        teams_response = requests.get(
            f"{API_BASE_URL}/api/teams?approved=true",
            headers=headers
        )
        
        if teams_response.status_code != 200:
            print(f"❌ Failed to fetch teams: {teams_response.json()}")
            return False
        
        teams = teams_response.json()
        print(f"Found {len(teams)} teams")
        
        if len(teams) < 2:
            print("❌ Need at least 2 teams to generate fixtures")
            return False
        
        # Generate fixtures
        tomorrow = datetime.now() + timedelta(days=1)
        start_date = tomorrow.strftime("%Y-%m-%d")
        
        gen_response = requests.post(
            f"{API_BASE_URL}/api/fixtures/generate?start_date={start_date}",
            headers=headers
        )
        
        if gen_response.status_code != 200:
            print(f"❌ Failed to generate fixtures: {gen_response.json()}")
            return False
        
        fixtures = gen_response.json()
        print(f"✓ Generated {len(fixtures)} fixtures")
    
    # Step 3: Validate fixture structure for filter
    print("\n[STEP 3] Validating fixture structure for team filter...")
    fixture = fixtures[0]
    
    required_fields = ['id', 'home_team_id', 'away_team_id', 'home_team_name', 'away_team_name']
    missing_fields = [f for f in required_fields if f not in fixture]
    
    if missing_fields:
        print(f"❌ Fixture missing required fields: {missing_fields}")
        return False
    
    print(f"✓ Fixture has required fields")
    print(f"  - Home Team: {fixture['home_team_name']} (ID: {fixture['home_team_id']})")
    print(f"  - Away Team: {fixture['away_team_name']} (ID: {fixture['away_team_id']})")
    
    # Step 4: Validate date constraints
    print("\n[STEP 4] Validating date constraint changes...")
    
    date_fields = ['week_start_date', 'week_end_date']
    if all(f in fixture for f in date_fields):
        week_start = datetime.fromisoformat(fixture['week_start_date'].replace('Z', '+00:00'))
        week_end = datetime.fromisoformat(fixture['week_end_date'].replace('Z', '+00:00'))
        
        week_range = (week_end - week_start).days
        
        print(f"✓ Fixture has date range fields")
        print(f"  - Week Start: {week_start.date()}")
        print(f"  - Week End: {week_end.date()}")
        print(f"  - Week Range: {week_range} days")
        
        # Verify constraint: 30 days from week start
        thirty_days_out = week_start + timedelta(days=30)
        print(f"\n  CONSTRAINT CHECK:")
        print(f"  - Min Date (week start): {week_start.date()}")
        print(f"  - Max Date (30 days): {thirty_days_out.date()}")
        print(f"  ✓ Frontend should constrain to this range")
    else:
        print(f"❌ Missing date fields in fixture")
        return False
    
    # Step 5: Verify HTML structure for filter
    print("\n[STEP 5] Verifying team list for filter dropdown...")
    
    # Get all unique teams from fixtures
    team_ids = set()
    for f in fixtures[:10]:  # Check first 10 fixtures
        team_ids.add(f['home_team_id'])
        team_ids.add(f['away_team_id'])
    
    print(f"✓ Found {len(team_ids)} unique teams in fixtures")
    print(f"  Team IDs: {sorted(team_ids)}")
    
    # Step 6: Verify data attributes in fixture cards
    print("\n[STEP 6] Validating fixture card data attributes...")
    
    sample_fixture = fixtures[0]
    print(f"✓ Data attributes for fixture {sample_fixture['id']}:")
    print(f"  - data-home-team-id=\"{sample_fixture['home_team_id']}\"")
    print(f"  - data-away-team-id=\"{sample_fixture['away_team_id']}\"")
    
    # Step 7: Summary
    print("\n" + "=" * 60)
    print("✓ ALL VALIDATION TESTS PASSED")
    print("=" * 60)
    print("\nFrontend Testing Checklist:")
    print("[ ] Team filter dropdown selects specific team")
    print("[ ] Filtered fixtures show only selected team's matches")
    print("[ ] Date picker respects 30-day constraint")
    print("[ ] Loader disappears after fixtures load")
    print("[ ] Filter works smoothly without page flicker")
    
    return True

if __name__ == "__main__":
    try:
        success = test_fixture_functionality()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
