# 📄 manuscripts/utils.py

from django.db.models import Count, Q
from users.models import User
from .models import Review
from .emails import send_reviewer_assignment_email   # ✅ import


def assign_reviewer_automatically(manuscript):
    reviewers = User.objects.filter(role='reviewer')

    if not reviewers.exists():
        return None

    reviewers = reviewers.annotate(
        active_reviews=Count(
            'assigned_reviews',
            filter=Q(assigned_reviews__decision='pending')
        )
    ).order_by('active_reviews')

    reviewer = reviewers.first()

    review = Review.objects.create(
        manuscript=manuscript,
        reviewer=reviewer
    )

    # ✅ NOW INSIDE FUNCTION
    try:
        send_reviewer_assignment_email(manuscript, reviewer.email)
    except Exception as e:
        print("Email error:", e)

    return reviewer