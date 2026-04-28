# 📄 manuscripts/models.py

import datetime
from django.db import models
from django.conf import settings


# =========================
# Manuscript Model
# =========================
class Manuscript(models.Model):

    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('revision', 'Revision Required'),
    ]

    FINAL_DECISION_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('revision', 'Revision Required'),
    ]

    paper_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='manuscripts/', blank=True, null=True)

    status = models.CharField(max_length=20, default='submitted', choices=STATUS_CHOICES)

    # ✅ Admin notes for review
    admin_notes = models.TextField(blank=True, null=True)

    final_decision = models.CharField(
        max_length=20,
        choices=FINAL_DECISION_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.paper_id:
            year = datetime.datetime.now().year
            count = Manuscript.objects.filter(created_at__year=year).count() + 1

            while True:
                generated_id = f"PAPER-{year}-{str(count).zfill(4)}"
                if not Manuscript.objects.filter(paper_id=generated_id).exists():
                    self.paper_id = generated_id
                    break
                count += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.paper_id


class Author(models.Model):
    manuscript = models.ForeignKey(
        'Manuscript',
        on_delete=models.CASCADE,
        related_name='authors'
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    is_main_author = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# =========================
# Review Model
# =========================
class Review(models.Model):
    manuscript = models.ForeignKey(
        'Manuscript',
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_reviews'
    )

    review_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )

    decision = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )

    comments = models.TextField(blank=True, null=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('manuscript', 'reviewer')

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # detect previous decision for updates
        previous_decision = None
        if not is_new:
            try:
                prev = Review.objects.get(pk=self.pk)
                previous_decision = prev.decision
            except Review.DoesNotExist:
                previous_decision = None

        if not self.review_code:
            year = datetime.datetime.now().year
            count = Review.objects.filter(
                assigned_at__year=year
            ).count() + 1

            self.review_code = f"REV-{year}-{str(count).zfill(4)}"

        super().save(*args, **kwargs)

        # 📧 Send email only when review is first created
        if is_new:
            self._send_assignment_email()
        else:
            # If decision changed from pending->(accepted/rejected), notify editor/admin
            if previous_decision != self.decision and self.decision != 'pending':
                try:
                    from .emails import send_review_submitted_email
                    send_review_submitted_email(self.manuscript)
                except Exception as e:
                    print(f"Failed to notify editor about submitted review: {e}")

    def _send_assignment_email(self):
        """Send assignment email to reviewer"""
        from .emails import send_reviewer_assignment_email
        try:
            send_reviewer_assignment_email(self.manuscript, self.reviewer.email)
        except Exception as e:
            print(f"Email error for reviewer {self.reviewer.email}: {e}")
