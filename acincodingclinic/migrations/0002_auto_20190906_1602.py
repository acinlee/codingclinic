# Generated by Django 2.1.7 on 2019-09-06 07:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('acincodingclinic', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CDC_Comment_reply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_reply', models.CharField(blank=True, max_length=150, null=True, verbose_name='대댓글')),
                ('reply_recommend', models.IntegerField(default=0)),
                ('reply_createdate', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CDC_Notice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Notice_Title', models.CharField(max_length=150, null=True)),
                ('Notice_Content', models.TextField()),
                ('Notice_CreateDate', models.DateTimeField(null=True)),
                ('Notice_Files', models.FileField(blank=True, null=True, upload_to='')),
                ('Notice_hits', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Coaching_Board',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Coaching_Title', models.CharField(max_length=150, null=True)),
                ('Coaching_CreateDate', models.DateTimeField(null=True)),
                ('Coaching_ClassCode', models.CharField(blank=True, choices=[('1', 'C'), ('2', 'C++'), ('3', 'C#'), ('4', 'Python'), ('5', 'JAVA'), ('6', 'WEB'), ('7', 'DB'), ('8', '기타')], default='기타', max_length=10, null=True)),
                ('Coaching_isAnswer', models.BooleanField(default=False)),
            ],
        ),
        migrations.RenameModel(
            old_name='Coaching_FileManagement',
            new_name='CoachingFileMa',
        ),
        migrations.RemoveField(
            model_name='board_filemanagement',
            name='Board_FileConnect',
        ),
        migrations.RemoveField(
            model_name='error_filemanagement',
            name='Error_FileConnect',
        ),
        migrations.RemoveField(
            model_name='coaching',
            name='Coaching_ClassCode',
        ),
        migrations.RemoveField(
            model_name='coaching',
            name='Coaching_CreateDate',
        ),
        migrations.RemoveField(
            model_name='coaching',
            name='Coaching_Title',
        ),
        migrations.RemoveField(
            model_name='coaching',
            name='Coaching_User',
        ),
        migrations.AddField(
            model_name='cdc_comment',
            name='comment_user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='acincodingclinic.User'),
        ),
        migrations.AddField(
            model_name='cdc_error',
            name='Error_ClassCode',
            field=models.CharField(blank=True, choices=[('1', '신고'), ('2', '건의'), ('3', '문의')], default='신고', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='cdc_error',
            name='Error_hits',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='coaching',
            name='Coaching_CodeContent',
            field=models.CharField(max_length=10000, null=True),
        ),
        migrations.AddField(
            model_name='coaching',
            name='Coaching_Content',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='coaching',
            name='Coaching_author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='acincodingclinic.User'),
        ),
        migrations.AddField(
            model_name='user',
            name='CDC_Advertisement_Agreement',
            field=models.CharField(default='1', max_length=1, null=True, verbose_name='광고성이메일동의'),
        ),
        migrations.AlterField(
            model_name='cdc_board',
            name='Board_ClassCode',
            field=models.CharField(blank=True, choices=[('1', 'C'), ('2', 'C++'), ('3', 'C#'), ('4', 'Python'), ('5', 'JAVA'), ('6', 'WEB'), ('7', 'DB'), ('8', '기타')], default='기타', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='cdc_board',
            name='Board_Content',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='cdc_comment',
            name='comment',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='cdc_comment',
            name='comment_Board',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='comment', to='acincodingclinic.CDC_Board'),
        ),
        migrations.AlterField(
            model_name='coaching',
            name='Coaching_Code',
            field=models.IntegerField(default=1, null=True),
        ),
        migrations.DeleteModel(
            name='Board_FileManagement',
        ),
        migrations.DeleteModel(
            name='Error_FileManagement',
        ),
        migrations.AddField(
            model_name='coaching_board',
            name='Coaching_User',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='acincodingclinic.User'),
        ),
        migrations.AddField(
            model_name='cdc_notice',
            name='Notice_User',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='acincodingclinic.User'),
        ),
        migrations.AddField(
            model_name='cdc_comment_reply',
            name='cdc_comment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='acincodingclinic.CDC_Comment'),
        ),
        migrations.AddField(
            model_name='cdc_comment_reply',
            name='reply_user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='acincodingclinic.User'),
        ),
        migrations.AddField(
            model_name='coaching',
            name='Coaching_Number',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='acincodingclinic.Coaching_Board'),
        ),
    ]
