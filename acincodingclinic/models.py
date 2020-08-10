from django.db import models

# Create your models here.

#codingclinic 약자 = CDC
#모든 사용자 및 관리자 속성
class User(models.Model):
    class meta:
        db_table = '사용자 기본 속성'
    CDC_ID = models.CharField(max_length=20, null=True, blank=False)
    CDC_PW = models.CharField(max_length=20, null=True, blank=False)
    CDC_Name = models.CharField(max_length=15, null=True, blank=False)
    CDC_Birth = models.CharField(max_length=10, null=True, blank=False)
    CDC_PhoneNumber = models.CharField(max_length=11, null=True, blank=False)
    CDC_Email = models.CharField(max_length=100, null=True, blank=False)
    CDC_Gender = models.CharField(max_length=1, null=True, blank=False) #male=1 female=2
    CDC_joblist = (('1', '초등학생'),('2', '중학생'),('3', '고등학생'),('4', '대학생'),('5', '직장인'))
    CDC_job = models.CharField(max_length=10, choices=CDC_joblist, default='4', null=True, blank=False)
    CDC_isAdmin = models.BooleanField(default=False)
    CDC_Personal_Information_Agreement = models.CharField(max_length=1, verbose_name='개인정보동의', default='1', null=True, blank=False)
    CDC_Advertisement_Agreement = models.CharField(max_length=1, verbose_name='광고성이메일동의', default='1', null=True, blank=False) # 1:동의 2:미동의
    rank_list = (('1', '시스템관리자'),('2', '사용자'))
    rank = models.CharField(max_length=10, choices=rank_list, default='2', null=True, blank=False)
    CDC_SignUpDate = models.DateTimeField(null=True, blank=False) #회원 가입일
    CDC_LastDate = models.DateTimeField(null=True, blank=False) #최종 접속일
    CDC_ClientAddress = models.CharField(max_length=32, null=True, blank=False) #IPv4, IPv6
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.CDC_ID 


#상담 요청 및 답변
class Coaching_Board(models.Model):
    class meta:
        db_table = '상담 게시판'
    Coaching_User = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=False)
    Coaching_Title = models.CharField(max_length=150, null=True, blank=False)
    Coaching_CreateDate = models.DateTimeField(null=True, blank=False)
    Coaching_ClassificationList = (('1', 'C'), ('2','C++'), ('3','C#'), 
                                  ('4','Python'), ('5','JAVA'), ('6','WEB'), ('7','DB'), ('8', '기타')) #분류 리스트
    Coaching_ClassCode = models.CharField(max_length=10, choices=Coaching_ClassificationList, default='기타', null=True, blank=True) #분류코드 
    Coaching_isAnswer = models.BooleanField(default=False)

class Coaching(models.Model):
    class meta:
        db_table = '상담내용'
    Coaching_Number = models.ForeignKey(Coaching_Board, on_delete=models.CASCADE, null=True, blank=False)
    Coaching_author = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=False)
    Coaching_Content = models.TextField(null=True)
    Coaching_CodeContent = models.CharField(max_length=10000, null=True, blank=False)
    Coaching_Code = models.IntegerField(default=1, null=True, blank=False)
    
#상담 요청 및 답변 파일 관리    
class CoachingFileMa(models.Model):
    class meta:
        db_table = '상담 요청 및 답변 파일 관리'
    Coaching_FileConnect = models.ForeignKey(Coaching, on_delete=models.CASCADE, null=True, blank=False) #상담 + 파일 연결
    Coaching_Files = models.FileField(null=True, blank=True)

#공지사항
class CDC_Notice(models.Model):
    class meta:
        db_table = '각종 게시판'
    Notice_User = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=False)
    Notice_Title = models.CharField(max_length=150, null=True, blank=False)
    Notice_Content = models.TextField()
    Notice_CreateDate = models.DateTimeField(null=True, blank=False)
    Notice_Files = models.FileField(null=True, blank=True)
    Notice_hits= models.PositiveIntegerField(default=0)

#커뮤니티
class CDC_Board(models.Model):
    class meta:
        db_table = '커뮤니티'
    Board_User = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=False)
    Board_Title = models.CharField(max_length=150, null=True, blank=False)
    Board_Content = models.TextField()
    Board_CreateDate = models.DateTimeField(null=True, blank=False)
    Board_ClassificationList = (('1', 'C'), ('2','C++'), ('3','C#'), 
                               ('4','Python'), ('5','JAVA'), ('6','WEB'), ('7','DB'),('8', '기타')) #게시글 분류 코드
    Board_ClassCode = models.CharField(max_length=10, choices=Board_ClassificationList, default='기타', null=True, blank=True)
    Board_Files = models.FileField(null=True, blank=True)
    Board_hits= models.PositiveIntegerField(default=0)

#게시판 댓글
class CDC_Comment(models.Model):
    class meta:
        db_table = '댓글'
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE, default="")
    comment = models.CharField(max_length=150, null=True, blank=True)
    recommend = models.IntegerField(default=0)
    comment_Board = models.ForeignKey(CDC_Board, on_delete=models.CASCADE, default="", related_name ='comment')
    
    @staticmethod
    def getCommentAboutArticle(board_num):
        return Comment.objects.filter(CDC_Board__id=board_num)

#게시판 댓글에 댓글
class CDC_Comment_reply(models.Model):
    class meta:
        db_table = '대댓글'
    cdc_comment = models.ForeignKey(CDC_Comment, on_delete=models.CASCADE, null=True, blank=False)
    comment_reply = models.CharField(max_length=150, null=True, blank=True, verbose_name='대댓글')
    reply_user = models.ForeignKey(User,on_delete=models.CASCADE, default="")
    reply_recommend = models.IntegerField(default=0)
    reply_createdate = models.DateTimeField(null=True, blank=False,auto_now_add=True)
    def __str__(self):
        return self.comment_reply

#신고, 건의, 문의 게시판
class CDC_Error(models.Model):
    class meta:
        db_table = '신고 목록 관리'
    Error_User = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=False)
    Error_Title = models.CharField(max_length=150)
    Error_ClassificationList = (('1', '신고'), ('2','건의') ,('3','문의')) #게시글 분류 코드
    Error_ClassCode = models.CharField(max_length=10, choices=Error_ClassificationList, default='신고', null=True, blank=True) #분류코드 
    Error_Content = models.CharField(max_length=1000)
    Error_Files = models.FileField(null=True, blank=True)
    Error_Date = models.DateTimeField(null=True, blank=False)
    Error_hits= models.PositiveIntegerField(default=0)

#사용자 포인트 
class Point(models.Model):
    class meta:
        db_table = '포인트'
    Point_User = models.ForeignKey(User, on_delete=models.CASCADE)
    Point_balance = models.IntegerField(default=0)


