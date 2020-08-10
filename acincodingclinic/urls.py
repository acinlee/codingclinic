from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import EditBoard

app_name = 'acincodingclinic'
urlpatterns = [
    path('', views.main, name='main'),
    path('CDC/mainpage', views.mainpage, name='mainpage'),
    path('CDC/loginpage', views.loginpage, name='loginpage'),
    path('CDC/Login', views.login, name='login'),
    path('CDC/Loginout', views.logout, name='logout'),
    path('CDC/find_userinfo_id', views.find_userinfo_id, name='find_userinfo_id'), #아이디 찾기 
    path('CDC/find_userinfo_pw', views.find_userinfo_pw, name='find_userinfo_pw'), #비밀번호 찾기
    path('CDC/toSignUp', views.toSignUp, name='toSignUp'),
    path('CDC/SignUp', views.SignUp, name='signup'),
    path("CDC/topersonalmodify", views.to_personal_modify, name='to_personal_modify'),
    path("CDC/personalmodify", views.personal_modify, name='personal_modify'),
    path("CDC/CodingClinicInfo", views.codingclinic_info_page, name='codingclinic_info_page'),#소개 페이지
    
    #마이페이지
    path("CDC/GoMypage", views.gomypage, name='gomypage'),
    path("CDC/MypageUsrInfo", views.mypage, name='mypage'),
    path("CDC/MypageUsrCoaching", views.mypage_usrcoaching, name='mypage_usrcoaching'),
    path("CDC/MypageUsrPoint", views.mypage_usrpoing, name='mypage_usrpoing'),

    #공지사항
    path('notice/page/<page_num>', views.Notice_menu, name='Notice_menu'),
    path('notice/page/1', views.Notice_menu, name='Notice_menu_default'),
    path("CDC/WriteNotice", views.WriteNotice, name="WriteNotice"),
    path('notice/view/<notice_num>', views.ViewNotice, name='ViewNotice'),
    path('notice/edit/<notice_num>/', views.EditNotice, name='EditNotice'),
    path("CDC/FindNotice", views.findNotice, name="findNotice"), #공지사항 검색 기능
    path("CDC/SortNotice", views.sortNotice, name="sortNotice"), #공지사항 정렬 기능
    path("notice/delete/<notice_num>/", views.DeleteNotice, name="DeleteNotice"),#공지사항 삭제

    #게시판(커뮤니티)
    path('board/page/<page_num>', views.board_menu, name='board_menu'),
    path("CDC/Writeboard", views.write_board, name="write_board"),
    path('board/page/1', views.board_menu, name='board_menu_default'),
    path('board/view/<board_num>', views.ViewBoard, name='viewBoard'),
    path('board/edit/<board_num>/', views.EditBoard, name='editBoard'),
    path("CDC/FindBoard", views.findBoard, name="findBoard"), #커뮤니티 검색 기능
    path("CDC/SortBoard", views.sortBoard, name="sortBoard"), #커뮤니티 정렬 기능
    path("board/delete/<board_num>/", views.DeleteBoard, name="DeleteBoard"),#커뮤니티 삭제
    path("CDC/SelectBoard/<type_num>/<page_num>/", views.SelectBoard, name="SelectBoard"), #커뮤니티 게시글 종류 선택 
    
    #커뮤니티 댓글, 대댓글
    path('CDC/comment_write/<board_num>/',views.comment_write,name='comment_write'),#댓글 쓰기
    path('CDC/comment_edit/<str:board_num>/',views.comment_edit,name='comment_edit'),#댓글 수정
    path('CDC/comment_remove/<str:board_num>/',views.comment_remove,name='comment_remove'),#댓글 삭제
    path('CDC/comment_reply/<board_num>/',views.comment_reply,name='comment_reply'), #대댓글 쓰기
    path('CDC/comment_reply_edit/<str:board_num>',views.comment_reply_edit,name='comment_reply_edit'),#대댓글 수정
    path('CDC/comment_reply_remove/<board_num>',views.comment_reply_remove,name='comment_reply_remove'),#대댓글 삭제

    #신고 및 문의 
    path('errorboard/page/<page_num>', views.Error_board_menu, name='Error_board_menu'),
    path("CDC/errorWriteboard", views.write_errorboard, name="write_errorboard"),
    path('errorboard/page/1', views.Error_board_menu, name='errorboard_menu_default'),
    path('errorboard/view/<board_num>', views.ViewErrorBoard, name='viewErrorBoard'),
    
    #상담
    path('coaching/page/<page_num>', views.Coaching_menu, name="Coaching_menu"),
    path('coaching/page/1', views.Coaching_menu, name="Coaching_menu_default"),
    path('CDC/toWriteCoaching', views.toWriteCoaching, name="toWriteCoaching"), #상담 작성 이동
    path('CDC/writeCoaching', views.writeCoaching, name="writeCoaching"), #맨 처음 상담 작성
    path('coaching/view/<coaching_num>', views.ViewCoaching, name="ViewCoaching"), #상담확인
    path('coaching/answer/<coaching_num>', views.AnswerCoaching, name="AnswerCoaching"), #답변 
    path('coaching/answermodify/<coaching_num>', views.ModifyAnswer, name="ModifyAnswer"), #질문 및 답변 수정
    path('coaching/answerdelete/<coaching_num>', views.DeleteAnswer, name="DeleteAnswer"), #질문 및 답변 삭제
    path("CDC/FindCoaching", views.findCoaching, name="findCoaching"), #상담 검색 기능
    path("CDC/SortCoaching", views.sortCoaching, name="sortCoaching"), #상담 정렬 기능
  
    #관리자
    path('CDC/adminMyage', views.adminMypage, name='adminMypage'),

    #이메일
    path('CDC/activate/<uid64>/<token>', views.activate, name='activate'),
    path('CDC/findID', views.find_id, name='find_id'), #아이디 찾기 메일
    path('CDC/findPW', views.find_pw, name='find_pw'), #비밀번호 찾기 메일

    #회원가입 완료
    path('CDC/SignUpGo', views.SignUpGo, name='SignUpGo'),
    #ajax
    path('SignUp_idcheck', views.SignUp_idcheck, name='SignUp_idcheck'), #user id 중복 확인
    path('SignUp_emailcheck', views.SignUp_emailcheck, name='SignUp_emailcheck'), #회원 가입시 이메일 중복 방지
    path('NewAnswerAdd', views.NewAnswerAdd, name='NewAnswerAdd'), #답변 생성
    path('Usrmodify_emailcheck', views.Usrmodify_emailcheck, name='Usrmodify_emailcheck'), #회원 정보 수정시 이메일 중복 방지

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
