# coding:utf-8

import sqlalchemy as sa
from ..core import db, get_model, regions, FromCache, after_commit


class CompetitionTeamPrize(db.Model):
    __tablename__ = 'competition_team_prizes'

    competition_team_id = db.Column(db.Integer(), db.ForeignKey('competition_teams.id', ondelete='cascade'),
                                    primary_key=True)
    prize = db.Column(db.Unicode(32))

    @property
    def competition_team(self):
        competition_team_model = get_model('CompetitionTeam')
        return db.session.query(competition_team_model). \
            options(FromCache('model', 'competition_team:%d' % self.competition_team_id)). \
            filter_by(id=self.competition_team_id).first()

    def __eq__(self, other):
        if isinstance(other, CompetitionTeamPrize) and self.competition_team_id == other.competition_team_id:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.competition_team_id)

    def __repr__(self):
        return u"<CompetitionTeamPrize(competition_team_id=%s)>" % (self.competition_team_id)


@sa.event.listens_for(CompetitionTeamPrize, 'after_insert')
@sa.event.listens_for(CompetitionTeamPrize, 'after_update')
def on_competition_team_prize_insert_or_update(mapper, connection, competition_team_prize):
    def do_after_commit():
        invalidate_on_competition_team_prize(competition_team_prize)

    after_commit(do_after_commit)


@sa.event.listens_for(CompetitionTeamPrize, 'before_delete')
def on_competition_team_prize_delete(mapper, connection, competition_team_prize):
    invalidate_on_competition_team_prize(competition_team_prize)


def invalidate_on_competition_team_prize(competition_team_prize):
    competition_model = get_model('Competition')
    competition_team_model = get_model('CompetitionTeam')
    competition = db.session.query(competition_model). \
        join(competition_team_model,
             sa.and_(
                 competition_team_model.competition_id == competition_model.id,
                 competition_team_model.id == competition_team_prize.competition_team_id)). \
        first()

    if competition.c_type == 2:
        regions['model'].delete('competition_team:%d:prize' % competition_team_prize.competition_team_id)
        competition_team = db.session.query(competition_team_model).get(competition_team_prize.competition_team_id)

        competition_athlete_model = get_model('CompetitionAthlete')
        team_member_model = get_model('TeamMember')
        athlete_model = get_model('Athlete')

        athletes = db.session.query(athlete_model). \
            select_from(CompetitionTeamPrize). \
            join(competition_athlete_model,
                 sa.and_(competition_athlete_model.competition_team_id == CompetitionTeamPrize.competition_team_id,
                         CompetitionTeamPrize.competition_team_id == competition_team_prize.competition_team_id)). \
            join(competition_team_model,
                 competition_team_model.id == competition_athlete_model.competition_team_id). \
            join(team_member_model,
                 team_member_model.id == competition_athlete_model.team_member_id). \
            join(athlete_model,
                 team_member_model.athlete_id == athlete_model.id). \
            all()
        account_prizes_keys = ['account:%d:prizes' % athlete.account_id for athlete in athletes]
        if account_prizes_keys:
            regions['model'].delete_multi(account_prizes_keys)
        athlete_prizes_keys = ['athlete:%d:prizes' % athlete.id for athlete in athletes]
        if athlete_prizes_keys:
            regions['model'].delete_multi(athlete_prizes_keys)
        regions['model'].delete('team:%d:prizes' % competition_team.team_id)
