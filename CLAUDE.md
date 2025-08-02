# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django REST API backend for a women's sports listings service. The API aggregates sports games/events from various leagues (WNBA, NWSL, NCAA, FIFA, etc.) and provides filtered endpoints for consumption by a separate frontend application.

## Core Architecture

- **Django REST Framework API** with PostgreSQL database
- **Main app**: `games` - contains all models, management commands, and data processing
- **API app**: `api` - contains DRF views, serializers, and URL routing
- **Data Model**: Games belong to Sports and Leagues, have many Teams/Networks/WatchLinks
- **Management Commands**: Extensive scraping and data management commands for different leagues

## Development Environment

The project uses **devbox** for environment management:
```bash
make dev  # Enter devbox shell with Python 3.11 and activated venv
```

## Common Development Commands

### Server Management
```bash
make start                    # Run development server (python manage.py runserver)
make user                     # Create superuser
```

### Data Management
```bash
make data                     # Add fresh data for all leagues
make [league]                 # Add data for specific league (wnba, nwsl, ncaa, fifa, etc.)
make clean                    # Clean old games (keep recent)
make really_clean             # Delete all games and related data
make clean_[league]           # Clean specific league data
```

### Available Leagues
- `wnba`, `nwsl`, `ncaa`, `ncaa_vball`, `fifa`, `us_soccer`, `au`, `pwhl`, `unrivaled`, `rugby`

### Scraping Commands
```bash
make ncaa_scrape             # Scrape NCAA data
make ncaa_vball_scrape       # Scrape NCAA volleyball
make au_scrape               # Scrape Athletes Unlimited
make scrape_rugby_wc         # Scrape Rugby World Cup
```

### Team Management
```bash
make rank                    # Calculate team rankings
make clean_teams             # Clean team data
```

### Dependencies
```bash
make dep                     # Update requirements.txt from current pip freeze
```

## Key Files and Structure

### Models (`games/models.py`)
- **Game**: Central model linking Sports, Leagues, Teams, Networks, WatchLinks
- **Team**: Belongs to League, has ranking and conference
- **League**: Belongs to Sport
- **Sport**: Top-level categorization
- **Network**: TV/streaming networks
- **WatchLink**: URLs for watching games

### API Endpoints (`api/views.py`)
- `/api/games/` - All games with filtering (time, sport, league, team, network)
- `/api/games/today/` - Today's games (with 2hr buffer for live games)
- `/api/games/upcoming/` - Next 7 days
- `/api/games/sport/<sport_name>/` - Games by sport (24hr window)
- `/api/sports/` - All sports
- `/api/teams/` - All teams with filtering and ranking

### Management Commands (`games/management/commands/`)
Each league has dedicated scraping and data processing commands. Key patterns:
- `add_games.py` - Main data ingestion command
- `[league]_scrape.py` - Web scraping for specific leagues
- `[league]_data.py` - Data processing for specific leagues
- `clean_games.py` - Data cleanup utilities
- `rank_teams.py` - Team ranking calculations

## Database Configuration

Uses PostgreSQL with environment variables:
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `SECRET_KEY`, `DEBUG`

## API Features

- **Django Filter Backend**: Filter by sport, time, league
- **Custom Query Parameters**: `start_time`, `end_time`, `current`, `team_includes`, `team`, `network`
- **Pagination**: LimitOffset with 20 items per page
- **CORS**: Configured for localhost:3000 and sheplays.net
- **Caching**: 1-hour cache on sport-specific endpoints
- **Time Zones**: Central Time (America/Chicago)

## Deployment

- **Vercel**: Configured with `vercel.json` and `build_files.sh`
- **Frontend**: Separate repository at https://github.com/ashley-hebler/sheplays
- **Domains**: api.sheplays.net, sheplays.net

## Testing

No specific test framework is configured. Tests can be run with:
```bash
python manage.py test
```