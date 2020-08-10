from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, Http404, HttpResponseRedirect
from .models import *
from .models import CoachingFileMa
from datetime import datetime
import json, random, string
from .forms import *
from django.utils import timezone
from django.utils.encoding import smart_text
from django.core.files.storage import FileSystemStorage
from django.views.generic import UpdateView
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
#이메일 관련 import
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from .tokens import AccountActivationTokenGenerator
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.core.paginator import Paginator

import itertools

# 세션 관리
def addSessions(request, user):
    request.session['cdc_id'] = user.CDC_ID
    request.session['cdc_name'] = user.CDC_Name
    request.session['job'] = user.CDC_job
    request.session['rank'] = user.rank

# 접속자의 유저 객체 반환
def getInfo(request):
    user = User.objects.get(CDC_ID=request.session['cdc_id'])
    return user

def main(request, page_num=1):
    board_list = CDC_Notice.objects.all().order_by('-Notice_CreateDate')[(int(page_num)-1)*3:int(page_num)*3]
    return render(request, 'acincodingclinic/newbase.html',{'board' : board_list ,})

def loginpage(request):
    return render(request, 'acincodingclinic/login/loginpage.html')

def mainpage(request):
    return render(request, 'acincodingclinic/base.html')
    

def login(request, page_num=1):
    
    if request.method == 'POST':
        user_id = request.POST['cdc_id']
        user_pw = request.POST['cdc_pw']
        try:
            user = User.objects.get(CDC_ID=user_id)
            board_list = CDC_Board.objects.all().order_by('-Board_CreateDate')[(int(page_num)-1)*3:int(page_num)*3]
            if ((user.rank == '1' or user.rank == '2') and user_pw == user.CDC_PW and user.is_active==True):
                addSessions(request, user)
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                User.objects.filter(CDC_ID=user_id).update(
                    CDC_ClientAddress = ip
                )    
                return render(request, 'acincodingclinic/newbase.html', {
                    'user_info' : user,
                    'board' : board_list ,
                    })
            elif user_pw != user.CDC_PW:
                return render_to_response('acincodingclinic/Error/Error.html', {
                    'alert_msg' : '비밀번호가 맞지 않습니다.',
                    'url' : '/'
                })
            else:
                return render_to_response('acincodingclinic/Error/Error.html', {
                    'alert_msg' : '이메일 인증이 완료되지 않았습니다.',
                    'url' : '/'
                })
                #raise (Http404("비밀번호가 맞지 않습니다."))
        except User.DoesNotExist:
            return render_to_response('acincodingclinic/Error/Error.html', {
                    'alert_msg' : '해당 아이디가 없습니다.',
                    'url' : '/'
                })
                #raise (Http404("해당 아이디가 없습니다."))
    else:
        return render(request, 'acincodingclinic/login/loginpage.html', {
            'user_info' : getInfo(request),
             })

# 로그아웃 클릭 시 + user_ip + 마지막 접속 시간
def logout(request, page_num=1):
    board_list = CDC_Board.objects.all().order_by('-Board_CreateDate')[(int(page_num)-1)*3:int(page_num)*3]
    #로그아웃 시간 + user_ip
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    User.objects.filter(CDC_ID=request.session['cdc_id']).update(
        CDC_ClientAddress = ip,
        CDC_LastDate = datetime.now()
    )  
    for item in list(request.session.keys()):
        del request.session[item]
       
    return render(request, 'acincodingclinic/newbase.html',{'board' : board_list })

#아이디, 비밀번호 찾기 이동
def find_userinfo_id(request):
    return render(request, 'acincodingclinic/login/find_user_info_id.html')

def find_userinfo_pw(request):
    return render(request, 'acincodingclinic/login/find_user_info_pw.html')

#아이디 비밀번호 찾기 기능
def find_id(request):
    try:
        user = User.objects.get(CDC_Name=request.POST['find_usr_name'], CDC_Email=request.POST['find_usr_email'])
        if user:
            # localhost:8000
            message = render_to_string('acincodingclinic/login/find_id_email.html',                         {
                    'user': user,
            })
            mail_subject = "[코딩클리닉] 아이디 찾기 메일입니다."
            user_email = user.CDC_Email
            email = EmailMessage(mail_subject, message, to=[user_email])
            email.send()
            return render(request, 'acincodingclinic/login/idfindemailok.html')
    except:
        messages.error(request, '해당하는 정보의 아이디가 없습니다.')
        return redirect('acincodingclinic:find_userinfo_id')
    
def find_pw(request):
    try:
        user = User.objects.get(CDC_Name=request.POST['find_usr_name'], CDC_ID=request.POST['find_usr_id'], CDC_Email=request.POST['find_usr_email'])
        _LENGTH = 12 # 12자리

        # 숫자 + 대소문자
        string_pool = string.ascii_letters + string.digits
        # 랜덤한 문자열 생성
        update_usr_pw = "" 
        for i in range(_LENGTH) :
            update_usr_pw += random.choice(string_pool) # 랜덤한 문자열 하나 선택
        
        User.objects.filter(CDC_Name=request.POST['find_usr_name']).filter(CDC_ID=request.POST['find_usr_id']).filter(CDC_Email=request.POST['find_usr_email']).update(
            CDC_PW = update_usr_pw,
        )

        message = render_to_string('acincodingclinic/login/find_pw_email.html', {
            'user_pw':update_usr_pw,
        })
        mail_subject = "[코딩클리닉] 임시 비밀번호 메일입니다."
        user_email = user.CDC_Email
        email = EmailMessage(mail_subject, message, to=[user_email])
        email.send()
        return render(request, 'acincodingclinic/login/pwfindemailok.html')
    except:
        messages.error(request, '해당하는 정보의 회원이 없습니다.')
        return redirect('acincodingclinic:find_userinfo_pw')

#마이페이지 회원 비밀번호 확인
def gomypage(request):
    if request.method == "POST":
        user = User.objects.get(CDC_ID=request.session['cdc_id'])
        if user.CDC_PW==request.POST['cdc_pw']:
            return redirect('acincodingclinic:mypage')
        else:
            messages.error(request, '비밀번호 오류')
            return redirect('acincodingclinic:main')
    else:
        return render(request,'acincodingclinic/mypage/mypagePW.html')

#마이페이지(개인정보 관리)      
def mypage(request):
    user = User.objects.get(CDC_ID=request.session['cdc_id'])
    year = user.CDC_Birth[0:4]
    month = user.CDC_Birth[4:6]
    day = user.CDC_Birth[6:8]
    usr_birth=year+'년 '+month+'월 '+day+'일'
    return render(request, 'acincodingclinic/mypage/mypage.html', {'user_info' : user, 'usr_birth':usr_birth})

#개인 코칭 확인
def mypage_usrcoaching(request, page_num=1):
    user = User.objects.get(CDC_ID=request.session['cdc_id'])
    coaching_list = Coaching_Board.objects.filter(Coaching_User=user).order_by('-Coaching_CreateDate')[(int(page_num)-1)*10:int(page_num)*10]
    return render(request, 'acincodingclinic/mypage/mycoaching.html', {'user_info' : user, 'coaching_list' : coaching_list,})

#개인 포인트 확인
def mypage_usrpoing(request):
    user = User.objects.get(CDC_ID=request.session['cdc_id'])
    return render(request, 'acincodingclinic/mypage/mypoint.html', {'user_info' : user,})

#회원 정보 수정 정보 전달
def to_personal_modify(request):
    user = User.objects.get(CDC_ID=request.session['cdc_id'])
    year = user.CDC_Birth[0:4]
    month = user.CDC_Birth[4:6]
    day = user.CDC_Birth[6:8]
    usr_birth=year+'년 '+month+'월 '+day+'일'
    return render(request, 'acincodingclinic/mypage/personal_modify.html', {'user_info' : user, 'usr_birth':usr_birth})

#회원정보 수정시 이메일 중복 방지
def Usrmodify_emailcheck(request):
    cdc_email = request.POST['usr_modify_email']
    UserList = User.objects.objects(CDC_Email=cdc_email)
    user = User.objects.get(CDC_ID=request.session['cdc_id'])
    if not UserList or UserList.CDC_Email == user.CDC_Email:
        context = {  'msg' : 'Y',  }
    else:
        context = {  'msg' : 'N',  }

    return HttpResponse(json.dumps(context), content_type="application/json")


#회원 정보 수정
def personal_modify(request):
    user = User.objects.get(CDC_ID=request.session['cdc_id'])
    year = user.CDC_Birth[0:4]
    month = user.CDC_Birth[4:6]
    day = user.CDC_Birth[6:8]
    usr_birth=year+'년 '+month+'월 '+day+'일'

    cdc_email = request.POST['usr_modify_email']
    cdc_jobcheck = request.POST['usr_job']
    cdc_jobfinal=''
    if cdc_jobcheck == '초등학생':
        cdc_jobfinal='1'
    elif cdc_jobcheck == '중학생':
        cdc_jobfinal='2'
    elif cdc_jobcheck == '고등학생':
        cdc_jobfinal='3'
    elif cdc_jobcheck == '대학생':
        cdc_jobfinal='4'
    elif cdc_jobcheck == '직장인':
        cdc_jobfinal='5'

    User.objects.filter(CDC_ID=request.session['cdc_id']).update(
    CDC_PW = request.POST['pw_passrule'],
    CDC_PhoneNumber = request.POST['phone_modify'],
    CDC_Email = cdc_email,
    CDC_job = cdc_jobfinal
    )
    return render(request, 'acincodingclinic/mypage/mypage.html',{'user_info' : user, 'usr_birth':usr_birth})


#회원 가입 페이지 이동
def toSignUp(request):
    user = User.objects.all()
    return render(request, 'acincodingclinic/signup/SignUp.html', {'user_info':user})

#회원 가입
def SignUp(request):
    if request.method == "POST":
        #이메일
        email_text = request.POST['email_text']
        email_select = request.POST['email_select']
        cdc_email = email_text+'@'+email_select
        
        #직업
        cdc_jobcheck = request.POST['usr_job']
        cdc_jobfinal=''
        if cdc_jobcheck == '초등학생':
            cdc_jobfinal='1'
        elif cdc_jobcheck == '중학생':
            cdc_jobfinal='2'
        elif cdc_jobcheck == '고등학생':
            cdc_jobfinal='3'
        elif cdc_jobcheck == '대학생':
            cdc_jobfinal='4'
        elif cdc_jobcheck == '직장인':
            cdc_jobfinal='5'

        #생년월일
        user_year = request.POST['usr_year']
        user_month = request.POST['usr_month']
        user_day = request.POST['usr_day']
        if len(user_day) == 1:
            user_day = '0'+user_day
        user_birth = user_year+user_month+user_day
        
        #성별
        cdc_gendercheck = request.POST['usr_gender']
        cdc_gender = ''
        if cdc_gendercheck == '남자':
            cdc_gender = '1'
        else:
            cdc_gender = '2'
        
        #광고성 이메일 수신 동의
        cdc_advertise_check = request.POST['advertisement_email']
        cdc_advertise = ''
        if cdc_advertise_check == 'advertisement_email_agree':
            cdc_advertise = '1'
        else:
            cdc_advertise = '2'

        user = User.objects.create(
        CDC_ID = request.POST['cdc_id'],
        CDC_PW = request.POST['cdc_pw'],
        CDC_Name = request.POST['usr_name'],
        CDC_Birth = user_birth,
        CDC_Gender = cdc_gender,
        CDC_PhoneNumber = request.POST['usr_phonenumber'],
        CDC_Email = cdc_email,
        CDC_Advertisement_Agreement = cdc_advertise,
        CDC_job = cdc_jobfinal,
        CDC_SignUpDate = datetime.now()
        )

        user.is_active = False
        current_site = get_current_site(request) 
        # localhost:8000
        message = render_to_string('acincodingclinic/signup/user_active_email.html',                         {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
        })
        mail_subject = "[코딩클리닉] 회원가입 인증 메일입니다."
        user_email = cdc_email
        email = EmailMessage(mail_subject, message, to=[user_email])
        email.send()
        return render(request, 'acincodingclinic/signup/emailok.html')

    return render(request, 'acincodingclinic/signup/SignUp.html')

def activate(request, uid64, token):
    uid = force_text(urlsafe_base64_decode(uid64))
    user = User.objects.get(pk=uid)

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('acincodingclinic:SignUpGo')
    else:
        return HttpResponse('비정상적인 접근입니다.')

#회원가입 완료 페이지
def SignUpGo(request):
    return render(request, 'acincodingclinic/signup/signupok.html')

#회원가입시 유저 id 중복 방지
def SignUp_idcheck(request):
    id_check = request.POST['idcheck']
    UserList = User.objects.filter(CDC_ID=id_check)
    if not UserList:
        context = {  'msg' : 'Y',  }
    else:
        context = {  'msg' : 'N',  }

    return HttpResponse(json.dumps(context), content_type="application/json")

#회원가입시 유저 id 중복 방지
def SignUp_emailcheck(request):
    emailcontent = request.POST['emailcontent']
    emailcompany = request.POST['emailcompany']
    cdc_email = emailcontent+'@'+emailcompany
    UserList = User.objects.filter(CDC_Email=cdc_email)
    if not UserList:
        context = {  'msg' : 'Y',  }
    else:
        context = {  'msg' : 'N',  }

    return HttpResponse(json.dumps(context), content_type="application/json")

#접속자 객체 반환
def getInfo(request):
    user = User.objects.get(CDC_ID=request.session['cdc_id'])
    return user

#소개 페이지
def codingclinic_info_page(request):
    return render(request, 'acincodingclinic/info/codingclinicinfo.html')

#게시판 관련
#공지사항
def Notice_menu(request, page_num=1):
    #notice_list = CDC_Notice.objects.all().order_by('-Notice_CreateDate')[(int(page_num)-1)*10:int(page_num)*10]
    notice_list = CDC_Notice.objects.all().order_by('-Notice_CreateDate')
    page = request.GET.get('page', 1)
    paginator = Paginator(notice_list, 10)
    posts = paginator.page(page)
    post_count = posts.paginator.count

    return render(request, 'acincodingclinic/notice/notice.html', {'notice_list' : notice_list ,'posts':posts,'post_count':post_count})

# 공지사항 작성
def WriteNotice(request):
    if request.method == 'POST': # method가 POST 방식이라면 글이 써진 것
        form = NoticeForm(request.POST, request.FILES) # 이때는 해당 데이터를 다시 폼으로 넘겨보린다.
        # 그리고 나서 올바른 값들이 들어왔는지 확인해야 한다.
        if form.is_valid():
            CDC_Notice = form.save(commit=False) # commit=Flase는 넘겨진 데이터를 바로 저장하지 말라는 뜻.
            CDC_Notice.Notice_Title = request.POST['Notice_Title']
            CDC_Notice.Notice_Content = request.POST['Notice_content']
            CDC_Notice.Notice_CreateDate = timezone.now()
            try:
                CDC_Notice.Notice_Files = request.FILES['file_upload']
            except:
                pass 
            CDC_Notice.Notice_User = User.objects.get(CDC_ID=request.session['cdc_id'])
            CDC_Notice.save()
            return redirect('acincodingclinic:Notice_menu_default')
    else:
        form = NoticeForm()

    return render(request, 'acincodingclinic/notice/writenotice.html', {'form' : form, 'user_info' : getInfo(request)})

# 공지사항 확인
def ViewNotice(request, notice_num):
    notice = CDC_Notice.objects.get(id=notice_num)
    notice.Notice_hits = notice.Notice_hits + 1
    notice.save()
    next_board = CDC_Notice.objects.filter(id__gt=notice_num).order_by('id')[:1]
    previous_board = CDC_Notice.objects.filter(id__lt=notice_num).order_by('id')[:1]

    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid:
            notice_ = form.save(commit=False)
            notice_.CDC_Notice = notice
            notice_.save()
            return redirect('/notice/post/' + str(notice_num))

    return render(request, "acincodingclinic/notice/noticeView.html", {'notice' : notice, 'next_board':next_board, 'previous_board':previous_board,})

#공지사항 내용, 제목 검색
def findNotice(request, page_num=1):
    find_kind = request.POST['notice_find'] #제목인지 내용 인지 판별
    find_content = request.POST['notice_content_find'] #유저가 입력한 텍스트
    #나중에 검색 기능 추가적으로 개발할 사항 : 단어 띄어쓰기 무시하고 검색 되는 기능 - 2019년 8월에 개발 1차 마무리 되고 할 예정
    if find_kind == "제목":
        if find_content == "":
            notice_list = CDC_Notice.objects.all().order_by('-Notice_CreateDate')
        else:
            notice_list = CDC_Notice.objects.filter(Notice_Title__icontains=find_content).order_by('-Notice_CreateDate')
    else:
        if find_content == "":
            notice_list = CDC_Notice.objects.all().order_by('-Notice_CreateDate')
        else:
            notice_list = CDC_Notice.objects.filter(Notice_Content__icontains=find_content).order_by('-Notice_CreateDate')
    
    page = request.GET.get('page', 1)
    paginator = Paginator(notice_list, 10)
    posts = paginator.page(page)
    post_count = posts.paginator.count

    return render(request, 'acincodingclinic/notice/notice.html', {'notice_list' : notice_list ,'posts':posts,'post_count':post_count})

#공지사항 정렬
def sortNotice(request, page_num=1):
    sort_notice = request.POST['notice_sort'] #정렬 종류
    sort_numeber = 0

    #나중에 검색 기능 추가적으로 개발할 사항 : 단어 띄어쓰기 무시하고 검색 되는 기능 - 2019년 8월에 개발 1차 마무리 되고 할 예정
    if sort_notice == "최신순":
        notice_list = CDC_Notice.objects.all().order_by('-Notice_CreateDate')
    else:
        notice_list = CDC_Notice.objects.all().order_by('Notice_CreateDate')
        sort_numeber = 1

    page = request.GET.get('page', 1)
    paginator = Paginator(notice_list, 10)
    posts = paginator.page(page)
    post_count = posts.paginator.count

    return render(request, 'acincodingclinic/notice/notice.html', {'notice_list' : notice_list , 'sort_numeber':sort_numeber,'posts':posts,'post_count':post_count})


# 공지사항 수정
def EditNotice(request, notice_num):
    notice = CDC_Notice.objects.get(id=notice_num)
    if request.method == 'POST': # method가 POST 방식이라면 글이 써진 것
        # 이때는 해당 데이터를 다시 폼으로 넘겨보린다.
        # 그리고 나서 올바른 값들이 들어왔는지 확인해야 한다.
        notice.Notice_Title = request.POST['Notice_Title']
        notice.Notice_Content = request.POST['Notice_content']
        try:
            notice.Notice_Files = request.FILES['file_upload']
        except:
            pass 
        notice.save()
        return redirect('acincodingclinic:Notice_menu_default')
    else:
        form = NoticeForm(initial={'Notice_Files':notice.Notice_Files }) 

    return render(request, 'acincodingclinic/notice/editnotice.html', {'form' : form, 'user_info' : getInfo(request), 'notice_num':notice_num,
                 'notice':notice})

#공지사항 삭제
@csrf_exempt
def DeleteNotice(request, notice_num):
    notice = CDC_Notice.objects.get(id=notice_num)
    if request.method == 'POST':
        if notice.Notice_User.CDC_PW == request.POST['cdc_pw']:
            CDC_Notice.objects.get(id=notice_num).delete()
        else:
            messages.error(request, '비밀번호 오류')
            return redirect('/notice/view/' + str(notice_num))
    
    messages.success(request, '삭제가 완료되었습니다.')
    return redirect('acincodingclinic:Notice_menu_default')


# 커뮤니티 메뉴 클릭 시
def board_menu(request, page_num=1):
    #board_list = CDC_Board.objects.all().order_by('-Board_CreateDate')[(int(page_num)-1)*10:int(page_num)*10]
    board_list = CDC_Board.objects.all().order_by('-Board_CreateDate')
    page = request.GET.get('page', 1)
    paginator = Paginator(board_list, 10)
    posts = paginator.page(page)
    post_count = posts.paginator.count

    return render(request, 'acincodingclinic/board/board.html', {'board' : board_list ,'posts':posts,'post_count':post_count})

# 게시글 작성 시
def write_board(request):
    if request.method == 'POST': # method가 POST 방식이라면 글이 써진 것
        form = PostForm(request.POST, request.FILES) # 이때는 해당 데이터를 다시 폼으로 넘겨보린다.
        # 그리고 나서 올바른 값들이 들어왔는지 확인해야 한다.
        if form.is_valid():
            CDC_Board = form.save(commit=False) # commit=Flase는 넘겨진 데이터를 바로 저장하지 말라는 뜻.
            CDC_Board.Board_Title = request.POST['Board_Title']
            CDC_Board.Board_Content = request.POST['Board_Content']
            CDC_Board.Board_CreateDate = timezone.now()
            CDC_Board.Board_ClassCode = request.POST['board_classcode']
            CDC_Board.Board_User = User.objects.get(CDC_ID=request.session['cdc_id'])
            try:
                CDC_Board.Board_Files = request.FILES['file_upload']
            except:
                pass 

            CDC_Board.save()
            return redirect('acincodingclinic:board_menu_default')
    else:
        form = PostForm()

    return render(request, 'acincodingclinic/board/writeboard.html', {'form' : form, 'user_info' : getInfo(request)})

# 커뮤니티 확인
def ViewBoard(request, board_num):
    board = CDC_Board.objects.get(id=board_num)
    comment = CDC_Comment.objects.filter(comment_Board=board) #게시글에 해당하는 댓글
    reply = CDC_Comment_reply.objects.filter(cdc_comment=comment) #게시글에 해당하는 대댓글
    board.Board_hits = board.Board_hits + 1
    board.save()
    next_board = CDC_Board.objects.filter(id__gt=board_num).order_by('id')[:1]
    previous_board = CDC_Board.objects.filter(id__lt=board_num).order_by('id')[:1]
    
    if request.method == 'POST':
        form = ComentForm(request.POST)
        if form.is_valid:
            board_ = form.save(commit=False)
            board_.CDC_Board = board
            board_.CDC_Comment = request.POST['comment']
            board_.save()
            return redirect('/board/post/' + str(board_num))
    else:
        form = CommentForm()

    return render(request, "acincodingclinic/board/boardView.html", {'board' : board, 'previous_board':previous_board, 'next_board':next_board,'comment':comment,'reply':reply})

# 커뮤니티 수정
def EditBoard(request, board_num):
    toboard = CDC_Board.objects.get(id=board_num)
    if request.method == 'POST': 
        toboard.Board_Title = request.POST['Board_Title']
        toboard.Board_Content = request.POST['Board_content']
        toboard.Board_ClassCode = request.POST['board_classcode']
        try:
            toboard.Board_Files = request.FILES['file_upload']
        except:
            pass 
        toboard.save()
        return redirect('acincodingclinic:board_menu_default')
    else:
        form = PostForm(initial={'Board_Files':toboard.Board_Files }) 

    return render(request, 'acincodingclinic/board/board_edit.html', {'form' : form, 'user_info' : getInfo(request), 'board_num':board_num,
                    'toboard':toboard})

# 커뮤니티 삭제
@csrf_exempt
def DeleteBoard(request, board_num):
    board = CDC_Board.objects.get(id=board_num)
    if request.method == 'POST':
        if board.Board_User.CDC_PW == request.POST['cdc_pw']:
            CDC_Board.objects.get(id=board_num).delete()
        else:
            messages.error(request, '비밀번호 오류')
            return redirect('/board/view/' + str(board_num))
    
    messages.success(request, '삭제가 완료되었습니다.')
    return redirect('acincodingclinic:board_menu_default')

# 커뮤니티 내용, 제목 검색
def findBoard(request, page_num=1):
    find_kind = request.POST['board_find'] #제목인지 내용 인지 판별
    find_content = request.POST['board_content_find'] #유저가 입력한 텍스트
    #나중에 검색 기능 추가적으로 개발할 사항 : 단어 띄어쓰기 무시하고 검색 되는 기능 - 2019년 8월에 개발 1차 마무리 되고 할 예정
    if find_kind == "제목":
        if find_content == "":
            board = CDC_Board.objects.all().order_by('-Board_CreateDate')
        else:
            board = CDC_Board.objects.filter(Board_Title__icontains=find_content).order_by('-Board_CreateDate')
    else:
        if find_content == "":
            board = CDC_Board.objects.all().order_by('-Board_CreateDate')
        else:
            board = CDC_Board.objects.filter(Board_Title__icontains=find_content).order_by('-Board_CreateDate')

    page = request.GET.get('page', 1)
    paginator = Paginator(board, 10)
    posts = paginator.page(page)
    post_count = posts.paginator.count

    return render(request, 'acincodingclinic/board/board.html', {'board' : board ,'posts':posts,'post_count':post_count})

# 커뮤니티 정렬
def sortBoard(request, page_num=1):
    sort_board = request.POST['board_sort'] #정렬 종류
    sort_numeber = 0
    #나중에 검색 기능 추가적으로 개발할 사항 : 단어 띄어쓰기 무시하고 검색 되는 기능 - 2019년 8월에 개발 1차 마무리 되고 할 예정
    if sort_board == "최신순":
        board = CDC_Board.objects.all().order_by('-Board_CreateDate')
    else:
        board = CDC_Board.objects.all().order_by('Board_CreateDate')
        sort_numeber = 1
    
    page = request.GET.get('page', 1)
    paginator = Paginator(board, 10)
    posts = paginator.page(page)
    post_count = posts.paginator.count

    return render(request, 'acincodingclinic/board/board.html', {'board' : board , 'sort_numeber':sort_numeber,'posts':posts,'post_count':post_count})

# 커뮤니티 글 종류 선택
def SelectBoard(request, type_num, page_num):
    if type_num=='0':
        board = CDC_Board.objects.all().order_by('-Board_CreateDate')
        if not board:
            messages.error(request, '해당하는 종류의 게시글이 존재하지 않습니다.')
            return redirect('acincodingclinic:board_menu_default')
    else:
        board = CDC_Board.objects.filter(Board_ClassCode=type_num).order_by('-Board_CreateDate')
        if not board:
            messages.error(request, '해당하는 종류의 게시글이 존재하지 않습니다.')
            return redirect('acincodingclinic:board_menu_default')

    page = request.GET.get('page', 1)
    paginator = Paginator(board, 10)
    posts = paginator.page(page)
    post_count = posts.paginator.count 
    return render(request, 'acincodingclinic/board/board.html', {'board' : board, 'type_num':type_num, 'posts':posts,'post_count':post_count})
    
#커뮤니티 댓글 및 대댓글
#댓글 작성 
def comment_write(request, board_num):
    comment_wr = CDC_Board.objects.get(id=board_num)
    if request.method == 'POST':
        user = User.objects.get(CDC_ID = request.session['cdc_id'])
        CDC_Comment.objects.create(
            comment_Board = comment_wr,
            comment_user = user,
            comment = request.POST.get('comment_content'),
        )
        return redirect('/board/view/'+str(board_num))
    return redirect('acincodingclinic:board_menu_default')
    
#댓글 삭제
def comment_remove(request, board_num):
    comment_re = CDC_Comment.objects.get(id=board_num)
    comment_pk = comment_re.comment_Board.id
    comment_re.delete()
    return redirect('/board/view/'+str(comment_pk))


#댓글수정
def comment_edit(request, board_num):
    comment_ed = CDC_Comment.objects.get(id=board_num)
    comment_pk = comment_ed.comment_Board.id
    comment_ed.comment = request.GET['content']
    comment_ed.save()
    return redirect('/board/view/'+ str(comment_pk))

#대댓글 달기^^7
def comment_reply(request, board_num):
    comment_re = CDC_Comment.objects.get(id=board_num)
    comment_rr = CDC_Comment_reply.objects.filter(cdc_comment=comment_re) #대댓글
    user = User.objects.get(CDC_ID = request.session['cdc_id'])
    comment_rr=CDC_Comment_reply.objects.create(
        cdc_comment = comment_re,
        comment_reply = request.GET['content'],
        reply_user = user
    )
    number = comment_rr.cdc_comment.comment_Board.id
    return redirect("/board/view/"+str(number))

#대댓글 수정
def comment_reply_edit(request, board_num):
    comment_red = CDC_Comment_reply.objects.get(id=board_num)
    comment_red.comment_reply = request.GET['content']
    comment_red.save()
    number = comment_red.cdc_comment.comment_Board.id
    return redirect('/board/view/'+str(number))

#대댓글 삭제
def comment_reply_remove(request, board_num):
    comment_remo = CDC_Comment_reply.objects.get(id=board_num)
    comment_remo.delete()
    number = comment_remo.cdc_comment.comment_Board.id
    return redirect('/board/view/'+str(number))
#댓글 종료

#신고 및 문의 게시판
# 게시판 메뉴 클릭 시
def Error_board_menu(request, page_num=1):
    try:
        user = User.objects.get(CDC_ID=request.session['cdc_id'])
    except:
        messages.error(request, '로그인시 이용가능 합니다.')
        return redirect('acincodingclinic:main')
    
    if request.session['rank'] == '1':
        board_list = CDC_Error.objects.all().order_by('-Error_Date')
    else:
        board_list = CDC_Error.objects.filter(Error_User=user).order_by('-Error_Date')

    page = request.GET.get('page', 1)
    paginator = Paginator(board_list, 10)
    posts = paginator.page(page)
    post_count = posts.paginator.count

    return render(request, 'acincodingclinic/errorboard/Error_board.html', {'board' : board_list,'posts':posts,'post_count':post_count})

# 게시글 작성 시
def write_errorboard(request):
    if request.method == 'POST': # method가 POST 방식이라면 글이 써진 것
        form = ErrorForm(request.POST, request.FILES) # 이때는 해당 데이터를 다시 폼으로 넘겨보린다.
        # 그리고 나서 올바른 값들이 들어왔는지 확인해야 한다.
        if form.is_valid():
            CDC_Error = form.save(commit=False) # commit=Flase는 넘겨진 데이터를 바로 저장하지 말라는 뜻.
            CDC_Error.Error_Title = request.POST['Error_Title']
            CDC_Error.Error_Content = request.POST['Error_Content']
            CDC_Error.Error_ClassCode = request.POST['error_classcode']
            CDC_Error.Error_Date = timezone.now()
            try:
                CDC_Error.Error_Files = request.FILES['file_upload']
            except:
                pass 
            CDC_Error.Error_User = User.objects.get(CDC_ID=request.session['cdc_id'])
            CDC_Error.save()
            return redirect('acincodingclinic:errorboard_menu_default')
    else:
        form = ErrorForm()

    return render(request, 'acincodingclinic/errorboard/Error_write.html', {'form' : form, 'user_info' : getInfo(request)})

#게시글 확인
def ViewErrorBoard(request, board_num):
    errorboard = CDC_Error.objects.get(id=board_num)
    errorboard.Error_hits = errorboard.Error_hits + 1
    errorboard.save()
    next_board = CDC_Error.objects.filter(id__gt=board_num).order_by('id')[:1]
    previous_board = CDC_Error.objects.filter(id__lt=board_num).order_by('id')[:1]

    if request.method == 'POST':
        form = ComentForm(request.POST)
        if form.is_valid:
            errorboard_ = form.save(commit=False)
            errorboard_.CDC_Error = errorboard
            errorboard_.save()
            return redirect('/errorboard/post/' + str(board_num))

    return render(request, "acincodingclinic/errorboard/Error_view.html", {'errorboard' : errorboard, 'next_board':next_board, 'previous_board':previous_board, 'user_info' : getInfo(request)})

#관리자 페이지 
def adminMypage(request):
    user = User.objects.get(CDC_ID=request.session['cdc_id'])
    return render(request, 'acincodingclinic/admin/admin.html', {'user_info' : user})

#상담 페이지
def Coaching_menu(request, page_num=1):
    try: 
        if request.session['cdc_id']:
            coaching_list = Coaching_Board.objects.all().order_by('-Coaching_CreateDate')
            page = request.GET.get('page', 1)
            paginator = Paginator(coaching_list, 10)
            posts = paginator.page(page)
            post_count = posts.paginator.count

            return render(request, 'acincodingclinic/coaching/tocoaching.html', {'user_info' : getInfo(request), 'coaching_list' : coaching_list,'posts':posts,'post_count':post_count})
        else:
            messages.error(request, '로그인시 이용가능 합니다.')
            return redirect('acincodingclinic:main')
    except:    
        messages.error(request, '로그인시 이용가능 합니다.')
        return redirect('acincodingclinic:main')

def toWriteCoaching(request):
    form = CoachingFileForm()
    return render(request, 'acincodingclinic/coaching/coaching.html', {'form':form, 'user_info' : getInfo(request)})

def writeCoaching(request):
    if request.method == 'POST': # method가 POST 방식이라면 글이 써진 것
        find_author = User.objects.get(CDC_ID=request.session['cdc_id'])
        coaching_board = Coaching_Board.objects.create(
            Coaching_User = User.objects.get(CDC_ID=request.session['cdc_id']),
            Coaching_Title = request.POST['coachingtitle'],
            Coaching_CreateDate = timezone.now(),
            Coaching_ClassCode = request.POST['coaching_classcode'],
        )

        coaching = Coaching.objects.create(
            Coaching_Number = coaching_board,
            Coaching_author = find_author,
            Coaching_Content = request.POST['coachingcontent'],
            Coaching_CodeContent = request.POST['htmleditor'],
            Coaching_Code = 1,
        )
        
        form = CoachingFileForm(request.POST, request.FILES)
        if form.is_valid():
            CoachingFileMa = form.save(commit=False)
            CoachingFileMa.Coaching_FileConnect = coaching
            try:
                CoachingFileMa.Coaching_Files = request.FILES['file_upload']
            except:
                pass 
            CoachingFileMa.save()
        
        return redirect('acincodingclinic:Coaching_menu_default')
    else:
        return redirect('acincodingclinic:writeCoaching')

def from_iterable(iterables):
    # chain.from_iterable(['ABC', 'DEF']) --> ['A', 'B', 'C', 'D', 'E', 'F']
    for it in iterables:
        for element in it:
            yield element

# 코칭 내용, 제목 검색
def findCoaching(request, page_num=1):
    find_kind = request.POST['coaching_find'] #제목인지 내용 인지 판별
    find_content = request.POST['coaching_content_find'] #유저가 입력한 텍스트
    #나중에 검색 기능 추가적으로 개발할 사항 : 단어 띄어쓰기 무시하고 검색 되는 기능 - 2019년 8월에 개발 1차 마무리 되고 할 예정
    if find_kind == "제목":
        if find_content == "":
            coaching = Coaching_Board.objects.all().order_by('-Coaching_CreateDate')
        else:
            coaching = Coaching_Board.objects.filter(Coaching_Title__icontains=find_content).order_by('-Coaching_CreateDate')
    else:
        if find_content == "":
            coaching = Coaching_Board.objects.all().order_by('-Coaching_CreateDate')
        else:
            coaching_ = Coaching.objects.filter(Coaching_Content__icontains=find_content)
            coaching_array = []
            for a in coaching_:
                #coaching.append(Coaching_Board.objects.filter(id=a.Coaching_Number.id).order_by('-Coaching_CreateDate'))
                coaching_lists = Coaching_Board.objects.filter(id=a.Coaching_Number.id)
                coaching_array.append(coaching_lists)
            coaching = list(itertools.chain.from_iterable(coaching_array))

    print(coaching)
    page = request.GET.get('page', 1)
    paginator = Paginator(coaching, 10)
    posts = paginator.page(page)
    post_count = posts.paginator.count

    return render(request, 'acincodingclinic/coaching/tocoaching.html', {'user_info' : getInfo(request), 'coaching_list' :coaching,'posts':posts,'post_count':post_count })

# 코칭 정렬
def sortCoaching(request, page_num=1):
    sort_coaching = request.POST['coaching_sort'] #정렬 종류
    sort_numeber = 0
    #나중에 검색 기능 추가적으로 개발할 사항 : 단어 띄어쓰기 무시하고 검색 되는 기능 - 2019년 8월에 개발 1차 마무리 되고 할 예정
    if sort_coaching == "최신순":
        coaching = Coaching_Board.objects.all().order_by('-Coaching_CreateDate')
    else:
        coaching = Coaching_Board.objects.all().order_by('Coaching_CreateDate')
        sort_numeber = 1
    
    page = request.GET.get('page', 1)
    paginator = Paginator(coaching, 10)
    posts = paginator.page(page)
    post_count = posts.paginator.count

    return render(request, 'acincodingclinic/coaching/tocoaching.html', {'user_info' : getInfo(request), 'coaching_list' :coaching, 'sort_numeber':sort_numeber,'posts':posts,'post_count':post_count})

#게시글 확인
def ViewCoaching(request, coaching_num):
    form = CoachingFileForm()
    coaching_board = Coaching_Board.objects.get(id=coaching_num)
    coaching = Coaching.objects.filter(Coaching_Number=coaching_board)
    bigcoaching = [] # 코칭중에 가장 큰 id 값 배열
    bigcoachingnum = 0 # 코칭중에 가장 큰 id 값
    for maxcoaching in coaching:
        bigcoaching.append(maxcoaching.id)
    bigcoachingnum = max(bigcoaching)
    coaching_userid=coaching_board.Coaching_User.CDC_ID #코칭 작성한 유저
    userid = User.objects.get(CDC_ID=request.session['cdc_id']) #접속 중인 유저
    return render(request, "acincodingclinic/coaching/coachingview.html", {'form':form, 'coachingboard' : coaching_board, 
    'coaching':coaching,'coaching_userid':coaching_userid, 'bigcoachingnum':bigcoachingnum, 'userid':userid,'user_info' : getInfo(request)})

#답변 작성(관리자) + 추가질문(사용자)
def AnswerCoaching(request, coaching_num):
    coaching_board = Coaching_Board.objects.get(id=coaching_num)
    coaching = Coaching.objects.filter(Coaching_Number=coaching_board)
    coaching_first = Coaching.objects.get(Coaching_Number=coaching_board, Coaching_Code=1)
    coaching_code_count = 0
    find_author = User.objects.get(CDC_ID=request.session['cdc_id'])
    for coachingcount in coaching:
        coaching_code_count = coaching_code_count+1
    if request.method == 'POST':
        if find_author.rank == '1':
            Coaching_Board.objects.filter(id=coaching_num).update(Coaching_isAnswer=True)
        else:
            Coaching_Board.objects.filter(id=coaching_num).update(Coaching_isAnswer=False)

        coaching = Coaching.objects.create(
            Coaching_Number= coaching_board,
            Coaching_author = find_author,
            Coaching_Content = request.POST['coachingcontent'],
            Coaching_CodeContent = request.POST.get('htmleditor'),
            Coaching_Code = coaching_code_count+1,
        )
        form = CoachingFileForm(request.POST, request.FILES)
        if form.is_valid():
            CoachingFileMa = form.save(commit=False)
            CoachingFileMa.Coaching_FileConnect = coaching
            try:
                CoachingFileMa.Coaching_Files = request.FILES['file_upload']
            except:
                pass
            CoachingFileMa.save()
            return redirect('acincodingclinic:Coaching_menu_default')
        else:
            return redirect('acincodingclinic:AnswerCoaching')
    else:
        form = CoachingFileForm()
        
    return render(request, 'acincodingclinic/coaching/coachinganswer.html',{'form':form,'coachingboard' : coaching_board, 
    'coaching':coaching_first,'user_info':getInfo(request)})

#답변 생성
def NewAnswerAdd(request):
    coachingboard = Coaching_Board.objects.get(id=request.POST['board_num'])
    coaching_list = Coaching.objects.filter(Coaching_Number=coachingboard)
    userid = request.POST['userid']
    user_id = User.objects.get(CDC_ID=userid)
    count_list = 0
    for count in coaching_list:
        count_list = count_list+1
    
    if count_list % 2 == 1:
        if user_id.rank == '1':
            context = {  'msg' : 'Y',  }
        else:
            context = {  'msg' : 'N',  }
    else:
        if user_id.rank == '2':
            context = {  'msg' : 'Y',  }
        else:
            context = {  'msg' : 'N',  }

    return HttpResponse(json.dumps(context), content_type="application/json")

#질문 및 답변 수정
def ModifyAnswer(request, coaching_num):
    form = CoachingFileForm()
    coaching = Coaching.objects.get(id=coaching_num)
    file = CoachingFileMa.objects.get(Coaching_FileConnect=coaching)
    if request.method == 'POST':
        coaching = Coaching.objects.filter(id=coaching_num)
        coachingobject = Coaching.objects.get(id=coaching_num)
        coaching.update(
            Coaching_Content = request.POST['coachingcontent'],
            Coaching_CodeContent = request.POST.get('htmleditor'),
        )
        form = CoachingFileForm(request.POST, request.FILES)
        if form.is_valid():
            CoachingFiles = form.save(commit=False)
            CoachingFiles.Coaching_FileConnect = coachingobject
            try:
                CoachingFiles.Coaching_Files = request.FILES['file_upload']
                CoachingFiles.save()
                file.delete()
            except:
                pass
            return redirect('acincodingclinic:Coaching_menu_default')
        else:
            return redirect('acincodingclinic:AnswerCoaching')
    else:
        form = CoachingFileForm()

    return render(request, 'acincodingclinic/coaching/coachingmodifyanswer.html', {'form':form, 'coaching':coaching, 'file':file})

#질문 및 답변 삭제
def DeleteAnswer(request, coaching_num):
    coaching = Coaching.objects.get(id=coaching_num)
    number = coaching.Coaching_Number.id
    coaching_board=Coaching_Board.objects.get(id=number)
    if len(coaching_board.coaching_set.all()) == 1:
        coaching_board.delete()
        return redirect('acincodingclinic:Coaching_menu_default')
    else:
        coaching.delete()
        return redirect('/coaching/view/'+str(number))