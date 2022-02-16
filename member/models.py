from django.db import models
from django.contrib.auth.models import User


# Create your models here.
from backend.models import Project


class Member(User):
    is_datascientist = models.BooleanField(default=False)
    is_annotator = models.BooleanField(default=False)

    def save(self, *args, **kwargs):

        if self.id and not self.password:
            # keep original password
            self.password = Member.objects.get(id=self.id).password

        if self.password and not self.password.startswith("pbkdf2_sha256$"):
            self.set_password(self.password)
        if not self.is_staff:
            self.is_staff = True
        super(Member, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Member"
        verbose_name_plural = "Member"


class Assignment(models.Model):
    member_id = models.ForeignKey(
        Member, related_name='my_assignments', on_delete=models.CASCADE
    )
    project_id = models.ForeignKey(
        Project, related_name='assigned_member', on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('member_id', 'project_id')

