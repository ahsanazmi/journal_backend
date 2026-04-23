from django.db import models
from datetime import datetime
from rest_framework.permissions import IsAdminUser  # ✅ ADD THIS

from django.conf import settings
class Manuscript(models.Model):
    """
    Main paper submission model
    """

    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    # 🔑 Simple Paper ID (e.g., 2026-0001)
    paper_id = models.CharField(max_length=20, unique=True, blank=True)

    # 📌 Paper Details
    title = models.CharField(max_length=255)
    abstract = models.TextField(default="Not Provided")
    keywords = models.CharField(max_length=255, default="General")
    area_of_research = models.CharField(max_length=100, default="General")

    # 📄 File Upload
    file = models.FileField(upload_to='manuscripts/')

    # 📍 Address
    address_line1 = models.CharField(max_length=255, default="Not Provided")
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, default="India")
    state = models.CharField(max_length=100, default="Unknown")
    city = models.CharField(max_length=100, default="Unknown")
    pincode = models.CharField(max_length=10, default="000000")

    # 🔁 Optional previous paper ID
    previous_paper_id = models.CharField(max_length=100, blank=True, null=True)

    # 🔄 Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted'
    )

    # ⏱️ Created time
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        Auto-generate paper_id like: 2026-0001
        """
        if not self.paper_id:
            year = datetime.now().year

            # get last paper for this year
            last_paper = Manuscript.objects.filter(
                paper_id__startswith=f"{year}"
            ).order_by('-id').first()

            if last_paper:
                last_number = int(last_paper.paper_id.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.paper_id = f"{year}-{str(new_number).zfill(4)}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.paper_id} - {self.title}"


class Author(models.Model):
    """
    Main + Co-authors
    """

    manuscript = models.ForeignKey(
        Manuscript,
        on_delete=models.CASCADE,
        related_name='authors'
    )

    name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)

    is_main_author = models.BooleanField(default=False)

    def __str__(self):
        return self.name

from rest_framework.permissions import IsAdminUser




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
        unique_together = ('manuscript', 'reviewer')  # ❗ prevent duplicate assignment


# 📄 manuscripts/models.py

FINAL_DECISION_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
    ('revision', 'Revision Required'),
]

final_decision = models.CharField(
    max_length=20,
    choices=FINAL_DECISION_CHOICES,
    default='pending'
)