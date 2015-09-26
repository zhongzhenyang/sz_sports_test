# coding:utf-8

# id对应的运动项目不存在
athletic_item_id_nonexistent = '10001'
# 运动项目的名称重复
athletic_item_name_duplicate = '10002'

# 用户绑定的运动项目不存在
account_bind_athletic_nonexistent = '20001'
# 用户重复绑定对应的运动项目
account_bind_athletic_duplicate = '20002'

# id对应的球队不存在
team_id_nonexistent = '30001'
# 球队的创建者已经创建了对应运动项目的球队
team_more_one_athletic_team_by_creator = '30002'
# 球队已经解散
team_dismissed = '30003'
# 私人球队,不能加入
team_private = '30004'

# 无对应的 team_member
team_member_athlete_nonexistent = '40001'
# 已经加入球队
team_member_athlete_joined = '40002'
# 已经离开球队
team_member_athlete_left = '40003'

# 无对应的竞赛
competition_id_noexistent = '50001'
# 参与者的资格不够
competition_participant_no_qualify = '50002'
# 参与者已经报名
competition_participant_registered = '50003'
# 竞赛已经结束
competition_finished = '50004'
# 比赛不存在
competition_fixture_id_noexistent = '50005'
# 比赛已经完成
competition_fixture_finished = '50006'
# 比赛进球不存在
match_goal_id_noexistent = '50007'
# 精彩瞬间不存在
match_highlight_id_noexistent = '50008'
# 不能提升为联赛
competition_cannot_promote_as_league = '50009'
# 已经在申请提升为联赛
competition_in_apply_league = '50010'
# 没有申请提升为联赛
competition_not_in_apply_league = '50011'
# 已经设置为置顶,不能重复设置
competition_sticked = '50012'
# 没有设置为置顶,不能取消置顶
competition_unsticked = '50013'
# 竞赛已经开始
competition_started = '50014'
# 该用户没有报名这项竞赛
competition_participant_unregistered = '50015'
# 分局记录不存在
match_section_id_noexistent = '50016'
# 不能根据比赛双方创建对阵
competition_fixture_cannot_create = '50017'

# 无对应的球场
site_id_noexistent = '60001'


# 无对应的消息
message_id_noexistent = '70001'
# 消息尚未处理
message_pending = '70002'
# 该消息类型不能处理
message_category_cannot_handle = '70003'


# id对应的用户不存在
account_id_noexistent = '80001'
# 该用户不在关注列表中
user_relation_noexistent = '80002'
# 密码不匹配
account_password_not_match = '80003'
# 该用户已经在关注列表
user_relation_duplicate = '80004'



# 该操作未经授权
operation_unauthorized = '99001'
# 当前用户已经登录,注册请先登出
logined_account_register = '99002'
# 找不到对应的资源
resource_not_found = '99003'
# 严重错误
fatal_error = '99004'
# 用户未通过验证,请先登录
user_unauthenticated = '99005'
