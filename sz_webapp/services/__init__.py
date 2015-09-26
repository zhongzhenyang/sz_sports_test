from .users import AccountService, UserService, UserRelationService
from .athletics import AthleticItemService
from .user_athletic import AccountAthleticItemService
from .teams import TeamService
from .team_members import TeamMemberService
from .competitions import CompetitionService
from .competition_teams import CompetitonTeamService
from .competition_fixtures import CompetitionFixtureService, MatchGoalService, MatchSectionService, MatchHighlightService
from .sites import SiteService
from .messages import MessageService

account_service = AccountService()
user_service = UserService()
user_relation_service = UserRelationService()
athletic_item_service = AthleticItemService()
account_athletic_item_service = AccountAthleticItemService()
team_service = TeamService()
team_member_service = TeamMemberService()
competition_service = CompetitionService()
competition_team_service = CompetitonTeamService()
competition_fixture_service = CompetitionFixtureService()
match_goal_service = MatchGoalService()
match_highlight_service = MatchHighlightService()
match_section_service = MatchSectionService()
site_service = SiteService()
message_service = MessageService()
