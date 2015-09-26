# coding:utf-8

import datetime
import sqlalchemy as sa
from ..core import BaseService, AppError, db
from ..models import Competition, CompetitionTeam, CompetitionAthlete, CompetitionTeamRank, Team, TeamMember
from .. import errors


class CompetitonTeamService(BaseService):
    __model__ = CompetitionTeam

    def add_competition_team(self, competition, team_id):
        competition_team = CompetitionTeam(competition_id=competition.id, team_id=team_id)
        self.save(competition_team)
        competition_team_rank = CompetitionTeamRank(c_team_id=competition_team.id, stage=competition.stage, pts=0)
        db.session.add(competition_team_rank)
        for (team_member_id,) in TeamMember.query.with_entities(TeamMember.id). \
                filter(TeamMember.team_id == team_id, TeamMember.status == 1).all():
            db.session.add(CompetitionAthlete(competition_team_id=competition_team.id, team_member_id=team_member_id))

        return competition_team

    def do_register(self, account_id, competition_id):
        competition, team = self._check(account_id, competition_id)
        if self.count_by(filters=[CompetitionTeam.competition_id == competition_id,
                                  CompetitionTeam.team_id == team.id]) > 0:
            raise AppError(error_code=errors.competition_participant_registered)
        today = datetime.date.today()
        if (today - competition.date_reg_end).days >= 1:
            raise AppError(error_code=errors.competition_started)
        return self.add_competition_team(competition, team.id)

    def undo_register(self, account_id, competition_id):
        competition, team = self._check(account_id, competition_id)
        competition_team = CompetitionTeam.query.filter(CompetitionTeam.competition_id == competition_id,
                                                        CompetitionTeam.team_id == team.id).first()
        if competition_team is None:
            raise AppError(error_code=errors.competition_participant_unregistered)
        else:
            for competition_athlete in CompetitionAthlete.query.filter(
                            CompetitionAthlete.competition_team_id == competition_team.id).all():
                db.session.delete(competition_athlete)
            competition_team_ranks = CompetitionTeamRank.query.filter(
                CompetitionTeamRank.c_team_id == competition_team.id).all()
            for competition_team_rank in competition_team_ranks:
                db.session.delete(competition_team_rank)
            db.session.delete(competition_team)

    def get_register_status(self, account_id, competition_id):
        competition, team = self._check(account_id, competition_id)
        if self.count_by(filters=[CompetitionTeam.competition_id == competition_id,
                                  CompetitionTeam.team_id == team.id]) > 0:
            status = "yes"
        else:
            status = "no"
        return status

    def _check(self, account_id, competition_id):
        competition = Competition.query.get(competition_id)
        if not competition:
            raise AppError(error_code=errors.competition_id_noexistent)
        if competition.options.get('individual', None) == 'true':
            team = Team.query.filter(Team.creator_id == account_id, Team.type == 0, Team.status == 1).first()
        else:
            team = Team.query.filter(Team.creator_id == account_id, Team.type == 1, Team.status == 1).first()

        if not team:
            raise AppError(error_code=errors.competition_participant_no_qualify)
        if team.status == -1:
            raise AppError(error_code=errors.team_dismissed)
        return competition, team
