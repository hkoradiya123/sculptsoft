"""
Groq AI integration for performance insights and analysis.
"""
from groq import Groq
from app.config import settings
from app.utils.logger import log_action


class GroqAI:
    def __init__(self):
        self.client = None
        if not settings.GROQ_API_KEY:
            return
        
        try:
            # Initialize Groq client with API key
            self.client = Groq(api_key=settings.GROQ_API_KEY)
        except Exception as e:
            log_action(f"Warning: Failed to initialize Groq client: {str(e)}")
            self.client = None

    def is_available(self) -> bool:
        """Check if Groq API is configured."""
        return self.client is not None

    def _extract_text(self, response) -> str:
        """Extract text from Groq completion response safely across SDK versions."""
        try:
            choices = getattr(response, "choices", None)
            if choices and len(choices) > 0:
                message = getattr(choices[0], "message", None)
                content = getattr(message, "content", "") if message else ""
                if isinstance(content, str) and content.strip():
                    return content.strip()
        except Exception:
            pass
        return ""

    def _chat(self, prompt: str, max_tokens: int = 600, temperature: float = 0.7) -> str:
        """Call Groq chat completions with fallback model handling."""
        if not self.is_available():
            return ""

        models_to_try = [settings.GROQ_MODEL, "llama-3.1-8b-instant"]
        last_error = None

        for model in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                text = self._extract_text(response)
                if text:
                    return text
            except Exception as e:
                last_error = e

        if last_error:
            raise last_error
        return ""

    def generate_performance_insights(self, player_stats: dict) -> str:
        """
        Generate AI-based performance insights for a player.
        
        Args:
            player_stats: Dictionary containing player statistics
                {
                    'name': str,
                    'matches': int,
                    'runs': int,
                    'wickets': int,
                    'centuries': int,
                    'half_centuries': int,
                    'highest_score': int,
                    'average_runs': float,
                    'role': str (batsman/bowler/all-rounder)
                }
        """
        if not self.is_available():
            return "AI insights unavailable. Groq API not configured."

        try:
            prompt = f"""
Analyze the cricket performance statistics and provide brief, actionable insights:

Player: {player_stats.get('name', 'Unknown')}
Role: {player_stats.get('role', 'All-rounder')}
Matches: {player_stats.get('matches', 0)}
Total Runs: {player_stats.get('runs', 0)}
Average Score: {player_stats.get('average_runs', 0):.2f}
Highest Score: {player_stats.get('highest_score', 0)}
Centuries: {player_stats.get('centuries', 0)}
Half-Centuries: {player_stats.get('half_centuries', 0)}
Wickets Taken: {player_stats.get('wickets', 0)}

Provide:
1. Performance Summary (1-2 sentences)
2. Strengths (2 key areas)
3. Areas to Improve (2 suggestions)
4. Recommendation (brief)

Keep it concise and cricket-specific.
            """.strip()

            text = self._chat(prompt, max_tokens=500, temperature=0.7)
            return text or "Unable to generate insights at this moment. Please try again later."

        except Exception as e:
            error_msg = f"Error generating performance insights: {str(e)}"
            log_action(error_msg)
            return f"Unable to generate insights at this moment. Please try again later."

    def generate_team_performance_pulse(self, team_stats: dict) -> str:
        """
        Generate team-level performance analysis.
        
        Args:
            team_stats: Dictionary containing aggregated team statistics
                {
                    'team_name': str,
                    'total_players': int,
                    'total_matches': int,
                    'avg_runs_per_match': float,
                    'top_batsmen': list,
                    'top_bowlers': list,
                    'form_trend': str (improving/declining/stable)
                }
        """
        if not self.is_available():
            return "Team pulse unavailable. Groq API not configured."

        try:
            prompt = f"""
Provide a team performance pulse analysis based on:

Team: {team_stats.get('team_name', 'Team')}
Players: {team_stats.get('total_players', 0)}
Total Matches: {team_stats.get('total_matches', 0)}
Average Runs/Match: {team_stats.get('avg_runs_per_match', 0):.2f}
Form Trend: {team_stats.get('form_trend', 'stable')}
Top Batsmen: {', '.join(team_stats.get('top_batsmen', []))}
Top Bowlers: {', '.join(team_stats.get('top_bowlers', []))}

Return ONLY plain text. No markdown, no **, no headings.
Keep it concise and actionable.
Output exactly 5 lines:
1) Form: one sentence
2) Batting: one sentence
3) Bowling: one sentence
4) Tactical: one sentence
5) Outlook: one sentence
Each line must be under 20 words.
            """.strip()

            text = self._chat(prompt, max_tokens=600, temperature=0.7)
            return text or "Unable to generate team pulse at this moment. Please try again later."

        except Exception as e:
            error_msg = f"Error generating team pulse: {str(e)}"
            log_action(error_msg)
            return f"Unable to generate team pulse at this moment. Please try again later."

    def generate_match_analysis(self, match_data: dict) -> str:
        """
        Generate AI-based post-match analysis.
        
        Args:
            match_data: Dictionary containing match details
        """
        if not self.is_available():
            return "Match analysis unavailable. Groq API not configured."

        try:
            prompt = f"""
Analyze this cricket match and provide insights:

Date: {match_data.get('date', 'Unknown')}
Teams: {match_data.get('team1', 'Team A')} vs {match_data.get('team2', 'Team B')}
Result: {match_data.get('result', 'Not completed')}
Team 1 Score: {match_data.get('team1_score', 0)}/{match_data.get('team1_wickets', 10)}
Team 2 Score: {match_data.get('team2_score', 0)}/{match_data.get('team2_wickets', 10)}

Key Performances:
- Man of the Match: {match_data.get('mom', 'N/A')}
- Best Bowler: {match_data.get('best_bowler', 'N/A')}

Provide:
1. Match Summary (1-2 sentences)
2. Turning Points (key moments)
3. Outstanding Performances (players and why)
4. What went wrong for losing team (2 factors)
5. Learning Points for next match

Be analytical and cricket-expert tone.
            """.strip()

            text = self._chat(prompt, max_tokens=700, temperature=0.7)
            return text or "Unable to generate match analysis at this moment. Please try again later."

        except Exception as e:
            error_msg = f"Error generating match analysis: {str(e)}"
            log_action(error_msg)
            return f"Unable to generate match analysis at this moment. Please try again later."


# Single instance for app-wide use
groq_ai = GroqAI()
