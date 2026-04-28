from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Union
from datetime import datetime

from app.middleware.auth import get_admin_user, get_current_user
from app.schemas import (
    PerformanceLogCreate,
    PerformanceLogUpdate,
    PerformanceLogResponse,
    PlayerInsightsResponse,
    TeamPerformancePulseResponse,
    MatchAnalysisResponse,
)
from app.utils.firestore_data import COLL, as_obj, create_doc, first_doc, list_docs, now_utc, update_doc, delete_doc
from app.utils.groq_ai import groq_ai
from app.utils.logger import log_action

router = APIRouter(prefix="/performance", tags=["Performance"])


def _same_id(left, right) -> bool:
    if left is None or right is None:
        return False
    return str(left) == str(right)


def _matches_user_identity(row: dict, value: Union[int, str]) -> bool:
    return _same_id(row.get("id"), value) or _same_id(row.get("uid"), value)


def _matches_log_user(log_row: dict, value: Union[int, str]) -> bool:
    return _same_id(log_row.get("user_id"), value) or _same_id(log_row.get("uid"), value)


def _clamp_number(value, low: float, high: float, default: float = 0.0) -> float:
    try:
        num = float(value)
    except (TypeError, ValueError):
        num = default
    return max(low, min(high, num))


def recalculate_user_career_stats(user_id: Union[int, str]) -> None:
    logs = list_docs(COLL.performance_logs, predicate=lambda row: _matches_log_user(row, user_id))

    matches = len(logs)
    runs = sum(int(log.get("runs_scored", 0)) for log in logs)
    wickets = sum(int(log.get("wickets_taken", 0)) for log in logs)
    centuries = sum(1 for log in logs if int(log.get("runs_scored", 0)) >= 100)
    half_centuries = sum(1 for log in logs if 50 <= int(log.get("runs_scored", 0)) < 100)
    highest_score = max([int(log.get("runs_scored", 0)) for log in logs], default=0)
    average_runs = round(runs / matches, 2) if matches else 0.0

    update_doc(
        COLL.users,
        user_id,
        {
            "matches": matches,
            "runs": runs,
            "wickets": wickets,
            "centuries": centuries,
            "half_centuries": half_centuries,
            "highest_score": highest_score,
            "average_runs": average_runs,
            "updated_at": now_utc(),
        },
    )


def build_ai_insights(logs: List[dict]) -> dict:
    if not logs:
        return {
            "headline": "No recent match data",
            "form": "insufficient_data",
            "consistency_score": 0,
            "strengths": [],
            "focus_areas": ["Log at least 3 matches to unlock AI insights"],
            "recommendations": [
                "Track match stats after each game.",
                "Add batting and bowling notes for better insights.",
            ],
        }

    recent = logs[:5]
    avg_runs = sum(float(item.get("runs_scored", 0)) for item in recent) / len(recent)
    avg_wickets = sum(float(item.get("wickets_taken", 0)) for item in recent) / len(recent)
    avg_rating = sum(float(item.get("performance_rating", 0)) for item in recent) / len(recent)

    first_runs = float(recent[-1].get("runs_scored", 0))
    latest_runs = float(recent[0].get("runs_scored", 0))
    run_trend = latest_runs - first_runs

    if avg_rating >= 8:
        form = "hot"
    elif avg_rating >= 6:
        form = "steady"
    else:
        form = "needs_work"

    strengths = []
    focus_areas = []

    if avg_runs >= 45:
        strengths.append("Strong batting output in recent matches")
    else:
        focus_areas.append("Improve shot selection in first 20 balls")

    if avg_wickets >= 1.2:
        strengths.append("Consistent wicket-taking impact")
    else:
        focus_areas.append("Work on death-over bowling plans")

    if run_trend > 0:
        strengths.append("Positive scoring trend over last few matches")
    elif run_trend < 0:
        focus_areas.append("Recent scoring is dropping - revisit batting routine")

    consistency_score = int(min(100, max(0, (avg_rating * 10) + (avg_runs * 0.8) + (avg_wickets * 8))))

    recommendations = [
        "Schedule one focused nets session before the next fixture.",
        "Set a single-match target and review it after every innings.",
        "Track opponent-specific plans in the notes section.",
    ]

    return {
        "headline": "AI performance snapshot ready",
        "form": form,
        "consistency_score": consistency_score,
        "recent_average_runs": round(avg_runs, 2),
        "recent_average_wickets": round(avg_wickets, 2),
        "recent_average_rating": round(avg_rating, 2),
        "strengths": strengths,
        "focus_areas": focus_areas,
        "recommendations": recommendations,
    }


@router.post("", response_model=PerformanceLogResponse)
async def log_performance(
    performance: PerformanceLogCreate,
    player_id: Union[int, str],
    current_user=Depends(get_admin_user),
):
    if performance.runs_scored < 0 or performance.wickets_taken < 0:
        raise HTTPException(status_code=400, detail="Runs and wickets cannot be negative")

    target_player = first_doc(COLL.users, predicate=lambda row: _matches_user_identity(row, player_id))
    if not target_player:
        raise HTTPException(status_code=404, detail="Target player not found")

    target_player_id = target_player.get("id")

    perf_log = create_doc(
        COLL.performance_logs,
        {
            "user_id": target_player_id,
            "match_date": performance.match_date,
            "runs_scored": performance.runs_scored,
            "wickets_taken": performance.wickets_taken,
            "match_type": performance.match_type,
            "opponent": performance.opponent,
            "performance_rating": performance.performance_rating,
            "notes": performance.notes,
            "created_at": now_utc(),
        },
    )

    recalculate_user_career_stats(target_player_id)
    log_action(
        "Performance logged by admin",
        user_id=current_user.id,
        details=f"target_player_id={target_player_id}, runs={performance.runs_scored}",
    )
    return as_obj(perf_log)


@router.get("/my-logs", response_model=List[PerformanceLogResponse])
async def get_my_performance_logs(
    current_user=Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
):
    logs = list_docs(
        COLL.performance_logs,
        predicate=lambda row: _matches_log_user(row, current_user.id),
        sort_key="match_date",
        reverse=True,
        offset=skip,
        limit=limit,
    )
    return [as_obj(row) for row in logs]


@router.get("/match-history")
async def get_my_match_history(
    current_user=Depends(get_current_user),
    skip: int = 0,
    limit: int = 30,
):
    logs = list_docs(
        COLL.performance_logs,
        predicate=lambda row: _matches_log_user(row, current_user.id),
        sort_key="match_date",
        reverse=True,
        offset=skip,
        limit=limit,
    )

    total_runs = sum(int(log.get("runs_scored", 0)) for log in logs)
    total_wickets = sum(int(log.get("wickets_taken", 0)) for log in logs)
    average_rating = round(
        sum(float(log.get("performance_rating", 0)) for log in logs) / len(logs), 2
    ) if logs else 0.0

    best_match = None
    if logs:
        top = max(logs, key=lambda item: (int(item.get("runs_scored", 0)) + (int(item.get("wickets_taken", 0)) * 20)))
        best_match = {
            "id": top.get("id"),
            "match_date": top.get("match_date"),
            "opponent": top.get("opponent"),
            "runs_scored": top.get("runs_scored"),
            "wickets_taken": top.get("wickets_taken"),
            "performance_rating": top.get("performance_rating"),
        }

    return {
        "summary": {
            "matches_logged": len(logs),
            "total_runs": total_runs,
            "total_wickets": total_wickets,
            "average_rating": average_rating,
            "best_match": best_match,
        },
        "logs": [as_obj(row) for row in logs],
    }


@router.put("/{log_id}", response_model=PerformanceLogResponse)
async def update_performance_log(
    log_id: int,
    payload: PerformanceLogUpdate,
    current_user=Depends(get_current_user),
):
    perf_log = first_doc(
        COLL.performance_logs,
        predicate=lambda row: _same_id(row.get("id"), log_id) and _same_id(row.get("user_id"), current_user.id),
    )

    if not perf_log:
        raise HTTPException(status_code=404, detail="Performance log not found")

    updates = payload.model_dump(exclude_unset=True)

    if "runs_scored" in updates and updates["runs_scored"] < 0:
        raise HTTPException(status_code=400, detail="Runs cannot be negative")
    if "wickets_taken" in updates and updates["wickets_taken"] < 0:
        raise HTTPException(status_code=400, detail="Wickets cannot be negative")

    perf_log = update_doc(COLL.performance_logs, log_id, updates)
    recalculate_user_career_stats(current_user.id)

    log_action("Performance log updated", user_id=current_user.id, details=f"log_id={log_id}")
    return as_obj(perf_log)


@router.delete("/{log_id}")
async def delete_performance_log(
    log_id: int,
    current_user=Depends(get_current_user),
):
    perf_log = first_doc(
        COLL.performance_logs,
        predicate=lambda row: _same_id(row.get("id"), log_id) and _same_id(row.get("user_id"), current_user.id),
    )

    if not perf_log:
        raise HTTPException(status_code=404, detail="Performance log not found")

    delete_doc(COLL.performance_logs, log_id)
    recalculate_user_career_stats(current_user.id)

    log_action("Performance log deleted", user_id=current_user.id, details=f"log_id={log_id}")
    return {"message": "Performance log deleted"}


@router.get("/player/{player_id}", response_model=List[PerformanceLogResponse])
async def get_player_performance_logs(
    player_id: Union[int, str],
    skip: int = 0,
    limit: int = 20,
):
    player = first_doc(COLL.users, predicate=lambda row: _matches_user_identity(row, player_id))
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

    logs = list_docs(
        COLL.performance_logs,
        predicate=lambda row: _matches_log_user(row, player_id),
        sort_key="match_date",
        reverse=True,
        offset=skip,
        limit=limit,
    )

    return [as_obj(row) for row in logs]


@router.get("/stats/{player_id}")
async def get_player_stats(player_id: Union[int, str]):
    player = first_doc(COLL.users, predicate=lambda row: _matches_user_identity(row, player_id))

    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

    return {
        "id": player.get("id"),
        "name": player.get("name"),
        "runs": player.get("runs", 0),
        "matches": player.get("matches", 0),
        "wickets": player.get("wickets", 0),
        "centuries": player.get("centuries", 0),
        "half_centuries": player.get("half_centuries", 0),
        "average_runs": player.get("average_runs", 0.0),
        "highest_score": player.get("highest_score", 0),
    }


# ==================== AI-POWERED INSIGHTS ENDPOINTS ====================


@router.get("/ai-insights/my-performance", response_model=PlayerInsightsResponse)
async def get_my_ai_performance_insights(
    current_user=Depends(get_current_user),
):
    """
    Generate AI-based performance insights for the current player.
    Uses Groq AI to analyze recent match statistics.
    """
    logs = list_docs(
        COLL.performance_logs,
        predicate=lambda row: _matches_log_user(row, current_user.id),
        sort_key="match_date",
        reverse=True,
        limit=10,
    )

    if not logs:
        return PlayerInsightsResponse(
            player_name=current_user.name,
            insights="No match data available yet. Log some performances to get AI insights!",
            matches_analyzed=0,
            timestamp=now_utc(),
        )

    player_stats = {
        "name": current_user.name,
        "matches": current_user.get("matches", 0),
        "runs": current_user.get("runs", 0),
        "wickets": current_user.get("wickets", 0),
        "centuries": current_user.get("centuries", 0),
        "half_centuries": current_user.get("half_centuries", 0),
        "highest_score": current_user.get("highest_score", 0),
        "average_runs": current_user.get("average_runs", 0.0),
        "role": current_user.get("role", "all-rounder"),
    }

    insights_text = groq_ai.generate_performance_insights(player_stats)

    log_action(
        "AI performance insights generated",
        user_id=current_user.id,
        details=f"analyzed {len(logs)} matches",
    )

    return PlayerInsightsResponse(
        player_name=current_user.name,
        insights=insights_text,
        matches_analyzed=len(logs),
        timestamp=now_utc(),
    )


@router.get("/ai-insights/player/{player_id}", response_model=PlayerInsightsResponse)
async def get_player_ai_insights(
    player_id: Union[int, str],
    force_refresh: bool = False,
):
    """
    Generate AI-based performance insights for a specific player.
    """
    player = first_doc(COLL.users, predicate=lambda row: _matches_user_identity(row, player_id))

    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

    normalized_player_id = player.get("id") if player.get("id") is not None else player_id
    today_key = now_utc().date().isoformat()
    cache_doc_id = f"player_perf::{normalized_player_id}::{today_key}"

    if not force_refresh:
        cached = first_doc(
            COLL.ai_summaries,
            predicate=lambda row: _same_id(row.get("id"), cache_doc_id)
            and row.get("summary_type") == "player_performance",
        )
        if cached and cached.get("insights"):
            return PlayerInsightsResponse(
                player_name=cached.get("player_name", player.get("name", "Player")),
                insights=cached.get("insights", ""),
                matches_analyzed=int(cached.get("matches_analyzed", 0) or 0),
                timestamp=cached.get("generated_at") or cached.get("created_at") or now_utc(),
            )

    logs = list_docs(
        COLL.performance_logs,
        predicate=lambda row: _matches_log_user(row, normalized_player_id),
        sort_key="match_date",
        reverse=True,
        limit=10,
    )

    if not logs:
        return PlayerInsightsResponse(
            player_name=player.get("name", "Player"),
            insights="No match data available for this player.",
            matches_analyzed=0,
            timestamp=now_utc(),
        )

    player_stats = {
        "name": player.get("name", "Player"),
        "matches": player.get("matches", 0),
        "runs": player.get("runs", 0),
        "wickets": player.get("wickets", 0),
        "centuries": player.get("centuries", 0),
        "half_centuries": player.get("half_centuries", 0),
        "highest_score": player.get("highest_score", 0),
        "average_runs": player.get("average_runs", 0.0),
        "role": player.get("role", "all-rounder"),
    }

    insights_text = groq_ai.generate_performance_insights(player_stats)

    generated_at = now_utc()
    create_doc(
        COLL.ai_summaries,
        {
            "summary_type": "player_performance",
            "day_key": today_key,
            "player_id": normalized_player_id,
            "player_name": player.get("name", "Player"),
            "insights": insights_text,
            "matches_analyzed": len(logs),
            "generated_by_user_id": player.get("id"),
            "generated_at": generated_at,
            "updated_at": generated_at,
        },
        doc_id=cache_doc_id,
    )

    return PlayerInsightsResponse(
        player_name=player.get("name", "Player"),
        insights=insights_text,
        matches_analyzed=len(logs),
        timestamp=generated_at,
    )


@router.get("/ai-insights/team-pulse", response_model=TeamPerformancePulseResponse)
async def get_team_performance_pulse(
    current_user=Depends(get_current_user),
    force_refresh: bool = False,
):
    """
    Generate team-level AI performance analysis.
    Aggregates stats from all players and provides team insights.
    """
    today_key = now_utc().date().isoformat()
    cache_doc_id = f"team_pulse::{today_key}"

    if not force_refresh:
        cached = first_doc(
            COLL.ai_summaries,
            predicate=lambda row: _same_id(row.get("id"), cache_doc_id)
            and row.get("summary_type") == "team_pulse",
        )
        if cached and cached.get("pulse"):
            return TeamPerformancePulseResponse(
                team_name=cached.get("team_name", "Cricket Team"),
                pulse=cached.get("pulse", ""),
                total_players=int(cached.get("total_players", 0) or 0),
                timestamp=cached.get("generated_at") or cached.get("created_at") or now_utc(),
            )

    all_users = list_docs(
        COLL.users,
        predicate=lambda row: row.get("is_active", True) and row.get("role") == "player",
        limit=200,
    )
    recent_logs = list_docs(COLL.performance_logs, sort_key="match_date", reverse=True, limit=300)

    if not all_users:
        return TeamPerformancePulseResponse(
            team_name="Cricket Team",
            pulse="No team data available yet.",
            total_players=0,
            timestamp=now_utc(),
        )

    # Calculate team statistics with sanity caps to avoid outlier/corrupted values.
    total_matches = len(recent_logs)
    if total_matches > 0:
        capped_runs = [_clamp_number(log.get("runs_scored", 0), 0, 300) for log in recent_logs]
        avg_runs_per_match = round(sum(capped_runs) / total_matches, 2)
        capped_ratings = [_clamp_number(log.get("performance_rating", 0), 0, 10) for log in recent_logs]
        avg_rating = round(sum(capped_ratings) / total_matches, 2)
    else:
        # Fallback for empty logs; keep values bounded.
        total_runs = sum(_clamp_number(u.get("runs", 0), 0, 100000) for u in all_users)
        total_profile_matches = sum(_clamp_number(u.get("matches", 0), 0, 1000) for u in all_users)
        avg_runs_per_match = round((total_runs / total_profile_matches), 2) if total_profile_matches > 0 else 0.0
        avg_runs_per_match = _clamp_number(avg_runs_per_match, 0, 300)
        avg_rating = _clamp_number(
            sum(_clamp_number(u.get("average_runs", 0), 0, 120) for u in all_users) / len(all_users),
            0,
            10,
        ) if all_users else 0.0

    # Get top performers
    top_batsmen = sorted(
        [
            (u.get("name"), _clamp_number(u.get("runs", 0), 0, 100000))
            for u in all_users
            if u.get("runs", 0) > 0
        ],
        key=lambda x: x[1],
        reverse=True,
    )[:3]

    top_bowlers = sorted(
        [
            (u.get("name"), _clamp_number(u.get("wickets", 0), 0, 2000))
            for u in all_users
            if u.get("wickets", 0) > 0
        ],
        key=lambda x: x[1],
        reverse=True,
    )[:3]

    # Determine form trend from bounded rating scale.
    if avg_rating >= 7.5:
        form_trend = "improving"
    elif avg_rating >= 6.0:
        form_trend = "stable"
    else:
        form_trend = "declining"

    team_stats = {
        "team_name": "Cricket Team",
        "total_players": len(all_users),
        "total_matches": total_matches,
        "avg_runs_per_match": avg_runs_per_match,
        "top_batsmen": [name for name, _ in top_batsmen],
        "top_bowlers": [name for name, _ in top_bowlers],
        "form_trend": form_trend,
    }

    pulse_text = groq_ai.generate_team_performance_pulse(team_stats)

    generated_at = now_utc()
    create_doc(
        COLL.ai_summaries,
        {
            "summary_type": "team_pulse",
            "day_key": today_key,
            "team_name": "Cricket Team",
            "total_players": len(all_users),
            "pulse": pulse_text,
            "generated_by_user_id": current_user.id,
            "generated_at": generated_at,
            "updated_at": generated_at,
        },
        doc_id=cache_doc_id,
    )

    log_action(
        "Team performance pulse generated",
        user_id=current_user.id,
        details=f"team of {len(all_users)} players",
    )

    return TeamPerformancePulseResponse(
        team_name="Cricket Team",
        pulse=pulse_text,
        total_players=len(all_users),
        timestamp=generated_at,
    )


@router.post("/ai-insights/match-analysis", response_model=MatchAnalysisResponse)
async def generate_match_analysis(
    match_data: dict,
    current_user=Depends(get_current_user),
):
    """
    Generate AI-based post-match analysis.
    
    Expected match_data keys:
    - date: str
    - team1: str
    - team2: str
    - result: str
    - team1_score: int
    - team1_wickets: int
    - team2_score: int
    - team2_wickets: int
    - mom: str (Man of the Match)
    - best_bowler: str
    """
    analysis_text = groq_ai.generate_match_analysis(match_data)

    log_action(
        "Match analysis generated",
        user_id=current_user.id,
        details=f"{match_data.get('team1')} vs {match_data.get('team2')}",
    )

    return MatchAnalysisResponse(
        match_id=match_data.get("match_id"),
        analysis=analysis_text,
        analysis_date=now_utc(),
    )


@router.get("/ai-insights/status")
async def check_ai_insights_status():
    """
    Check if AI insights feature is available.
    Returns the status of Groq API integration.
    """
    return {
        "status": "available" if groq_ai.is_available() else "unavailable",
        "model": "groq_" + (groq_ai.client.models.list().data[0].id if groq_ai.is_available() else "unknown"),
        "message": "AI-powered insights are ready!" if groq_ai.is_available() else "Groq API key not configured",
    }


@router.get("/ai-insights/{player_id}")
async def get_player_ai_insights(player_id: Union[int, str]):
    player = first_doc(COLL.users, predicate=lambda row: _matches_user_identity(row, player_id))

    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

    logs = list_docs(
        COLL.performance_logs,
        predicate=lambda row: _matches_log_user(row, player_id),
        sort_key="match_date",
        reverse=True,
        limit=10,
    )

    return {
        "player_id": player.get("id"),
        "player_name": player.get("name"),
        "insights": build_ai_insights(logs),
    }
